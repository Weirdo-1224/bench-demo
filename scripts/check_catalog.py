"""Check new catalog links, Episode references, ignore policy and original assets."""
from pathlib import Path
import json
import re
import subprocess
from urllib.parse import unquote

from verify_layout import ROOT, sha


def main():
    documents = ['README.md', 'docs/README.md', 'docs/experiments.md',
                 'docs/maintenance/README.md', 'docs/maintenance/validation.md',
                 'data/README.md', 'archive/README.md', 'benchmark/README.md', 'tests/README.md']
    links = 0
    for name in documents:
        path = ROOT / name
        text = path.read_text(encoding='utf8')
        assert '\ufffd' not in text and '???' not in text, name
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            assert (path.parent / unquote(target.split('#')[0])).exists(), (name, target)
            links += 1
    manifest = json.loads((ROOT / 'data/episodes/GX010021/episode.json').read_text(encoding='utf8'))
    refs = [manifest[k] for k in ['data_root', 'raw', 'human_gold', 'evidence_manifest', 'experiment']]
    refs += manifest['candidates'] + [manifest['source_video']['path']]
    for ref in refs:
        assert (ROOT / ref).exists(), ref
    assert sha(ROOT / manifest['source_video']['path']) == manifest['source_video']['sha256']
    assert manifest['P02'] == 'PENDING'
    for row in json.loads((ROOT / 'docs/maintenance/migration.json').read_text(encoding='utf8')):
        assert (ROOT / row['new']).exists(), row
    for path, ignored in [('.recovery/layout-20261028/inventory.json', True),
                          ('.local/layout-validation/before/result.json', True),
                          ('data/episodes/EP002/raw/video.mp4', True),
                          ('data/episodes/EP002/annotations/gold/tasks.jsonl', False),
                          ('data/episodes/EP002/evidence/evidence_manifest.json', False)]:
        status = subprocess.run(['git', 'check-ignore', '-q', path], cwd=ROOT).returncode
        assert status in [0, 1] and (status == 0) == ignored, path
    snapshot = ROOT / '.recovery/layout-20261028/inventory.json'
    checked = 0
    if snapshot.exists():
        for row in json.loads(snapshot.read_text(encoding='utf8')):
            if row['path'] in ['README.md', '.gitignore']:
                continue
            path = ROOT / row['path']
            assert path.is_file() and sha(path) == row['sha256'], row['path']
            checked += 1
    result = {'catalog_documents':len(documents), 'links_checked':links,
              'episode_references':len(refs), 'unchanged_original_files':checked,
              'ignore_policy':'PASS', 'source_video_hash':'PASS'}
    output = ROOT / '.local/layout-validation/catalog.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
