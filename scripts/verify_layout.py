"""Read-only asset audit and network-blocked P01 replay in a disposable copy.

Run from the repository root. No inference entry point is called.
"""
from pathlib import Path
import argparse
import contextlib
import hashlib
import io
import json
import os
import shutil
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=['before', 'after'])
    args = parser.parse_args()
    recovery = ROOT / '.recovery/layout-20261028'
    inventory = json.loads((recovery / 'inventory.json').read_text(encoding='utf8'))
    mapping_file = ROOT / 'docs/maintenance/migration.json'
    mapping = json.loads(mapping_file.read_text(encoding='utf8')) if mapping_file.exists() else []
    moves = {x['old']: x['new'] for x in mapping if x['action'] == 'move'}
    changes = []
    for row in inventory:
        old = row['path']
        path = (recovery / 'files' / old) if args.phase == 'before' else (ROOT / moves.get(old, old))
        if not path.is_file() or sha(path) != row['sha256']:
            changes.append(old)
    allowed = ['README.md', '.gitignore'] if args.phase == 'after' else []
    unexpected = [x for x in changes if x not in allowed]
    if unexpected:
        raise RuntimeError(f'Unexpected original asset changes: {unexpected}')
    out = ROOT / '.local/layout-validation' / args.phase
    out.mkdir(parents=True, exist_ok=False)
    sandbox = out / 'workspace'
    sandbox.mkdir()
    # Only the experiment and its dependencies are needed; preserve original paths.
    source = recovery / 'files' if args.phase == 'before' else ROOT
    for name in ['annotation_pipeline', 'experiments', 'golden_episode']:
        shutil.copytree(source / name, sandbox / name,
                        ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['README.md', '.gitignore', 'Benchmark_Research_Showcase_Final.html']:
        shutil.copy2(source / name, sandbox / name)
    shutil.copytree(source / 'docs', sandbox / 'docs')
    (sandbox / '.git').write_text('gitdir: ' + str(ROOT / '.git') + '\n', encoding='utf8')
    env = dict(os.environ, PYTHONPATH=str(sandbox), PYTHONDONTWRITEBYTECODE='1')
    (sandbox / 'sitecustomize.py').write_text(
        "import socket\ndef blocked(*a, **kw):\n raise RuntimeError('Offline validation: network disabled')\nsocket.socket.connect=blocked\nsocket.create_connection=blocked\n", encoding='utf8')
    results = {}
    for label, folder in [('annotation', 'annotation_pipeline/tests'),
                          ('pilot', 'experiments/icme2027_pilot')]:
        command = [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', folder, '-p', 'test_*.py', '-v']
        run = subprocess.run(command, cwd=sandbox, env=env, capture_output=True)
        (out / f'{label}-tests.txt').write_bytes(run.stdout + run.stderr)
        results[label] = run.returncode
    # Supplementary test only: reconstruct the frozen audit context in this copy.
    # Keep the unmodified-context failures above; never patch the repository audit.
    frozen_head = json.loads((ROOT / 'experiments/icme2027_pilot/audit/audit.json').read_text(encoding='utf8'))['git_head']
    (sandbox / '.gitignore').write_bytes(subprocess.check_output(
        ['git', 'show', frozen_head + ':.gitignore'], cwd=ROOT))
    shutil.copy2(recovery / 'files/README.md', sandbox / 'README.md')
    frozen_test = """import sys, unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path('experiments/icme2027_pilot').resolve()))
import pilot
import test_pilot
original = test_pilot.pilot.cmd
def frozen_cmd(args, **kwargs):
    if args == ['git', 'rev-parse', 'HEAD']:
        return FROZEN_HEAD
    return original(args, **kwargs)
with patch.object(test_pilot.pilot, 'cmd', frozen_cmd):
    suite = unittest.defaultTestLoader.discover('experiments/icme2027_pilot', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
""".replace('FROZEN_HEAD', repr(frozen_head))
    frozen_run = subprocess.run([sys.executable, '-X', 'utf8', '-c', frozen_test],
                                cwd=sandbox, env=env, capture_output=True)
    (out / 'pilot-frozen-context-tests.txt').write_bytes(frozen_run.stdout + frozen_run.stderr)
    results['pilot_frozen_context_supplementary'] = frozen_run.returncode
    sys.path.insert(0, str(sandbox))
    sys.path.insert(0, str(sandbox / 'experiments/icme2027_pilot'))
    import pilot as p
    import runtime as r
    def blocked(*a, **kw):
        raise RuntimeError('Network disabled during offline validation')
    socket.socket.connect = blocked
    socket.create_connection = blocked
    r.invoke = blocked
    r.run = blocked
    p.now = lambda: json.loads((recovery / 'files/experiments/icme2027_pilot/summary.json').read_text(encoding='utf8'))['created_at']
    t = r.gold()
    replayed = 0
    for path in sorted(r.RUN.glob('*/seg-*/attempt-*.response.json')):
        directory = path.parent
        raw = p.read(path)
        request = p.read(directory / 'request.json')
        manifest = p.read(directory / 'input_manifest.json')
        r.assert_input(t, request['condition'], manifest['frames'], manifest['segment'])
        wire = r.wire_request(directory, manifest, request['prompt'])
        wire['max_tokens'] = raw.get('effective_max_output_tokens', r.CONFIG['max_output_tokens'])
        assert r.digest(wire) == raw['request_sha256'], str(path)
        replayed += 1
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        rows, summary = r.score()
        r.report()
    (out / 'replay-score-report.txt').write_text(log.getvalue(), encoding='utf8')
    assert replayed == 18
    assert summary['P02'] == 'PENDING'
    assert summary['conditions_complete'] == 4
    assert all(x['execution_status'] == 'SUCCESS' for x in rows)
    outputs = {}
    for name in ['results.csv', 'predictions.jsonl', 'scoring_details_v1.json', 'figures/p01_conditions_v1.png', 'advisor_report_v1.md']:
        outputs[name] = sha(p.HERE / name)
    summary.pop('created_at', None)
    result = {'phase': args.phase, 'tests': results, 'wire_replays': replayed,
              'original_files_checked': len(inventory), 'allowed_document_changes': changes,
              'outputs': outputs, 'summary': summary,
              'network_calls': 0, 'original_experiment_files_written': 0}
    result['recorded_results_equal'] = {name: outputs[name] == sha(recovery / 'files/experiments/icme2027_pilot' / name)
                                        for name in outputs if name != 'advisor_report_v1.md'}
    assert all(result['recorded_results_equal'].values()), 'Replayed results differ from recorded results'
    # Native integrity guard is retained verbatim; report its pre-existing limitations.
    frozen = p.read(ROOT / 'experiments/icme2027_pilot/audit/original_hashes.json')
    result['frozen_audit_mismatches'] = [x for x,h in frozen.items() if not (source/x).is_file() or sha(source/x) != h]
    result['frozen_git_head'] = p.read(ROOT / 'experiments/icme2027_pilot/audit/audit.json')['git_head']
    result['current_git_head'] = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT).decode().strip()
    if args.phase == 'after':
        before = json.loads((out.parent / 'before/result.json').read_text(encoding='utf8'))
        assert before['outputs'] == outputs, 'Derived output hashes changed'
        assert before['summary'] == summary, 'Normalized summary changed'
        result['before_after_equal'] = True
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if any(results.values()):
        raise SystemExit('Unit tests failed; inspect logs')


if __name__ == '__main__':
    main()
