"""Validate Session 3 artifacts only. No media inference, Runner or scoring execution."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
KINDS = {'event': ('events.json', 'records'), 'object': ('objects.json', 'records'),
         'state': ('objects.json', 'states'), 'step': ('procedure.json', 'observed_steps'),
         'rule': ('procedure.json', 'records'), 'relation': ('relations.json', 'records'),
         'l5': ('anomaly_candidates.json', 'records'), 'evidence': ('evidence_index.json', 'records')}
V2 = 'golden_episode/GX010021/annotations/v2_video_model/'

class Invalid(ValueError):
    pass

class Audit:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.documents = {}
        self.checks = Counter()
    def need(self, condition, label, message):
        self.checks[label] += 1
        if not condition:
            raise Invalid(message)
    def path(self, name):
        p = Path(name)
        self.need(not p.is_absolute() and '..' not in p.parts and ':' not in name
                  and '\\' not in name, 'safe_paths', f'Unsafe repository path: {name}')
        resolved = (self.root / p).resolve()
        self.need(resolved.is_relative_to(self.root), 'safe_paths', f'Path escapes repository: {name}')
        return resolved
    def read(self, name):
        if name not in self.documents:
            self.documents[name] = json.loads(self.path(name).read_text(encoding='utf-8'))
        return self.documents[name]
    def pointer(self, document, pointer):
        self.need(pointer.startswith('/'), 'pointers', f'Invalid JSON pointer: {pointer}')
        value = document
        try:
            for token in pointer[1:].split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                value = value[int(token)] if isinstance(value, list) else value[token]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise Invalid(f'Unresolved JSON pointer {pointer}') from exc
        return value
    def bounded(self, value, duration, label):
        self.need(isinstance(value, (int, float)) and not isinstance(value, bool)
                  and math.isfinite(value) and 0 <= value <= duration,
                  'times', f'Invalid media time {label}: {value}')
    def interval(self, interval, duration):
        self.bounded(interval['start_time'], duration, 'start')
        self.bounded(interval['end_time'], duration, 'end')
        self.need(interval['start_time'] <= interval['end_time'], 'times', 'Reversed interval')
    def ref(self, ref):
        filename, key = KINDS[ref['kind']]
        self.need(ref['path'] == V2 + filename, 'references', 'Reference uses wrong registry')
        self.need(ref['json_pointer'].startswith('/' + key + '/'), 'references', 'Wrong reference collection')
        record = self.pointer(self.read(ref['path']), ref['json_pointer'])
        self.need(record['id'] == ref['id'], 'references', 'ID/pointer mismatch')
        return record
    def validate(self, package, schema, verify_sources=True):
        self.checks.clear()
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema).iter_errors(package))
        self.need(not errors, 'schema', '; '.join(str(e)[:250] for e in errors[:3]))
        duration = package['media']['duration_sec']
        manifest = {s['path']: s['sha256'] for s in package['source_manifest']}
        self.need(len(manifest) == len(package['source_manifest']), 'sources', 'Duplicate source path')
        self.need(package['design_source'] in manifest, 'sources', 'Design source missing')
        self.need('golden_episode/GX010021/annotations/v2_video_model/annotation_manifest.json' in manifest,
                  'sources', 'Media annotation manifest missing')
        authoritative = self.read(V2 + 'annotation_manifest.json')
        self.need(package['media'] == authoritative['media'], 'media', 'Media manifest changed')
        if verify_sources:
            for filename, expected in manifest.items():
                file = self.path(filename)
                self.need(file.is_file(), 'sources', f'Missing frozen source: {filename}')
                actual = hashlib.sha256(file.read_bytes()).hexdigest()
                self.need(actual == expected, 'hashes', f'Changed source: {filename}')
            media_file = self.path(package['media']['source_path'])
            self.need(media_file.is_file(), 'media', 'Original media missing')
            self.need(hashlib.sha256(media_file.read_bytes()).hexdigest() == package['media']['sha256'],
                      'hashes', 'Original media hash changed')
        for contract in package['public_input_contracts'].values():
            Draft202012Validator.check_schema(contract)
            self.need(contract.get('additionalProperties') is False, 'contracts', 'Open public input contract')
        for name, contract in package['public_output_contracts'].items():
            Draft202012Validator.check_schema(contract)
            self.need(contract.get('additionalProperties') is False, 'contracts', 'Open output contract')
            self.need({'media_time', 'request_visible_media_cutoff', 'availability_time_ms',
                       'emission_wall_time_ms', 'evidence_refs'} <= set(contract['required']),
                      'contracts', 'Missing output clock/evidence fields')
        evidence = package['evidence_registry']
        for eid, entry in evidence.items():
            self.need(eid == entry['id'], 'evidence', 'Evidence registry key mismatch')
            self.need(entry['path'] in manifest, 'sources', 'Unfrozen evidence registry')
            source = self.ref(entry)
            self.interval(entry, duration)
            expected_start = source['source_timestamp'] if entry['modality'] == 'external_text' else source['start_time']
            expected_end = source['source_timestamp'] if entry['modality'] == 'external_text' else source['end_time']
            self.need(entry['start_time'] == expected_start and entry['end_time'] == expected_end,
                      'evidence', 'Evidence times do not match source')
            description = source['text'] if entry['modality'] == 'external_text' else source['description']
            self.need(entry['description'] == description, 'evidence', 'Evidence source text changed')
            for source_ref in source['source_refs']:
                origin = next((s for s in authoritative['sources'] if s['source_id'] == source_ref['source_id']), None)
                self.need(origin is not None and origin['path'] in manifest, 'sources', 'Missing underlying source')
                self.pointer(self.read(origin['path']), source_ref['json_pointer'])
            self.need(entry['availability_time'] is None and entry['effective_from'] is None,
                      'availability', 'Invented availability/effective time')
            if entry['modality'] == 'external_text':
                self.need(source['availability_time'] is None and source['effective_from'] is None,
                          'availability', 'Unexpected source rule timing: requires new schema/version review')
            if entry['frame_path'] is not None:
                self.need(entry['frame_path'] == source['frame_path'] and entry['frame_sha256'] == source['frame_sha256'],
                          'frames', 'Frame provenance changed')
                if verify_sources:
                    frame = self.path(entry['frame_path'])
                    self.need(frame.is_file(), 'frames', 'Missing referenced local frame')
                    self.need(hashlib.sha256(frame.read_bytes()).hexdigest() == entry['frame_sha256'],
                              'frames', 'Frame hash mismatch')
        tasks = package['tasks']
        ids = [t['task_id'] for t in tasks]
        self.need(len(ids) == len(set(ids)), 'ids', 'Duplicate task ID')
        gaps = {g['gap_id']: g for g in package['evidence_gaps']}
        self.need(len(gaps) == len(package['evidence_gaps']), 'ids', 'Duplicate gap ID')
        for task in tasks:
            tid = task['task_id']
            private = task['evaluator_private']
            public = task['agent_public']
            trigger = private['trigger']
            track = task['track']
            self.need(('-' + track + '-') in tid and task['subtask'].startswith(track + '.'), 'ids', 'Track ID mismatch')
            self.need(public['output_contract_id'] == {'T1':'state','T2':'probe','T3':'alarm'}[track],
                      'contracts', 'Wrong output contract for Track')
            self.need(public['input']['mode'] == {'T1':'CONTINUOUS_VIDEO_STATE','T2':'ISOLATED_TIMED_PROBE',
                      'T3':'CONTINUOUS_AUTONOMOUS_MONITORING'}[track], 'public_boundary', 'Wrong Track input mode')
            if public['payload_schema'] is not None:
                Draft202012Validator.check_schema(public['payload_schema'])
            forbidden = {'candidate_answer','gold_answer','evidence_ids','record_refs','json_pointer',
                         'normal_intervals','error_events','checkpoint_times','query_time','monitoring_interval'}
            def public_audit(value):
                if isinstance(value, dict):
                    self.need(not forbidden.intersection(value), 'public_boundary', 'Private field in public input')
                    self.need('const' not in value, 'public_boundary', 'Task public schema must not encode answer constants')
                    for child in value.values(): public_audit(child)
                elif isinstance(value, list):
                    for child in value: public_audit(child)
                elif isinstance(value, str):
                    self.need(not any(eid in value for eid in evidence), 'public_boundary', 'Private evidence ID in public text')
            public_audit(public)
            if track == 'T1':
                self.need(len(trigger['checkpoint_times']) > 0 and trigger['query_time'] is None
                          and trigger['monitoring_interval'] is None and public['input']['question'] is None,
                          'triggers', 'Invalid T1 snapshot protocol')
                self.need(trigger['checkpoint_times'] == sorted(trigger['checkpoint_times']), 'times', 'Unsorted checkpoints')
                for time in trigger['checkpoint_times']: self.bounded(time, duration, 'checkpoint')
                self.need(public['input']['question_delivery'] == 'NONE', 'public_boundary', 'T1 question trigger')
            elif track == 'T2':
                self.need(trigger['query_time'] is not None and not trigger['checkpoint_times']
                          and trigger['monitoring_interval'] is None and bool(public['input']['question'])
                          and public['input']['question_delivery'] == 'AT_PRIVATE_QUERY_TIME_ONLY',
                          'triggers', 'Invalid T2 isolated Probe')
                self.bounded(trigger['query_time'], duration, 'query')
            else:
                self.need(not trigger['checkpoint_times'] and trigger['query_time'] is None
                          and public['input']['question'] is None and public['input']['question_delivery'] == 'NONE'
                          and public['payload_schema'] is None, 'monitoring', 'T3 converted to question/answer')
                self.need(trigger['monitoring_interval'] == {'start_time':0,'end_time':duration},
                          'monitoring', 'T3 must continue throughout Episode')
            for reference in private['record_refs']:
                self.need(reference['path'] in manifest, 'sources', 'Unfrozen record registry')
                self.ref(reference)
                self.need(reference['access'] == 'EVALUATOR_ONLY_CONTEXT_NOT_ONLINE_EVIDENCE',
                          'public_boundary', 'Full record access cannot imply causal evidence access')
            sets = private['required_evidence_sets']
            self.need(len({s['set_id'] for s in sets}) == len(sets), 'ids', 'Duplicate evidence set ID')
            for evidence_set in sets:
                self.need(set(evidence_set['covers_fields']) <= set(private['scoring']['fields']), 'scoring', 'Evidence set field scope mismatch')
                refs = [b['evidence_id'] for b in evidence_set['bindings']]
                self.need(len(refs) == len(set(refs)), 'evidence', 'Duplicate evidence within set')
                at = evidence_set['applies_at_media_time']
                if track == 'T1': self.need(at in trigger['checkpoint_times'], 'times', 'Evidence set has no checkpoint')
                if track == 'T2': self.need(at == trigger['query_time'], 'times', 'Evidence set/query cutoff mismatch')
                if track == 'T3': self.need(at is None, 'monitoring', 'No per-event T3 query cutoff')
                for eid in refs:
                    self.need(eid in evidence, 'references', 'Unknown evidence ID')
                    if at is not None:
                        self.need(evidence[eid]['end_time'] <= at, 'future_evidence', f'{tid} references future evidence {eid}')
                if task['status'] == 'PILOT_CANDIDATE':
                    self.need(evidence_set['validity'] == 'CANDIDATE_MINIMAL_UNVERIFIED', 'maturity', 'Pilot insufficient set')
            if private['reference_items']:
                self.need(private['scoring']['fields'] == list(dict.fromkeys(i['field'] for i in private['reference_items'])),
                          'scoring', 'Scoring field list mismatch')
            for item in private['reference_items']:
                at = item['evaluate_at_media_time']
                self.bounded(at, duration, 'item checkpoint')
                self.need(at in trigger['checkpoint_times'] if track == 'T1' else at == trigger['query_time'],
                          'times', 'Reference item has no matching trigger')
                for eid in item['evidence_ids']:
                    self.need(eid in evidence and evidence[eid]['end_time'] <= at, 'future_evidence', 'Reference item future/unknown evidence')
                self.need(set(item['evidence_ids']) <= {b['evidence_id'] for s in sets if s['applies_at_media_time'] == at for b in s['bindings']},
                          'evidence', 'Score reference is not in applicable evidence set')
                if item['observable_time'] is not None:
                    ot = item['observable_time']
                    self.bounded(ot['earliest'], duration, 'earliest observable')
                    self.bounded(ot['latest'], duration, 'latest observable')
                    self.need(ot['earliest'] <= ot['latest'] <= at, 'times', 'Invalid observable interval')
                answer = private['candidate_answer']
                if track == 'T1' and 'checkpoints' in answer:
                    answer = next(a for a in answer['checkpoints'] if a['at'] == at)
                expected = answer
                for part in item['field'].split('.'): expected = expected[part]
                self.need(expected == item['value'], 'scoring', 'Candidate answer/reference item mismatch')
            uses_rule = any(evidence[b['evidence_id']]['modality'] == 'external_text' for s in sets for b in s['bindings'])
            if uses_rule:
                self.need(task['status'] != 'PILOT_CANDIDATE' and private['scoring']['mode'] == 'DISABLED',
                          'availability', 'Unreleased rule task cannot enter Pilot scoring')
                self.need(public['input']['visibility_regime'] == 'G1_BLOCKED_MISSING_GUIDANCE_TIMING',
                          'availability', 'Missing rule delivery restriction')
            if track == 'T2':
                reason = private['reasoning']
                query = trigger['query_time']
                all_eids = [b['evidence_id'] for s in sets for b in s['bindings']]
                span = round(query - min(evidence[e]['start_time'] for e in all_eids), 6) if all_eids else None
                self.need(reason['source_label_span_sec'] == span, 'span', 'Label span mismatch')
                self.need(reason['required_history'] == all_eids, 'evidence', 'Required history mismatch')
                self.need(reason['dependency_span_sec'] == (None if uses_rule else span), 'span', 'Dependency span confuses source label and release time')
                self.need(reason['instruction_temporal_limit'] == uses_rule, 'availability', 'Rule timing limitation mismatch')
                earliest = reason['earliest_answerable_time']
                if uses_rule: self.need(earliest is None, 'availability', 'Invented earliest answerable time')
                if earliest is not None:
                    self.need(0 <= earliest['earliest'] <= earliest['latest'] <= query,
                              'times', 'Earliest answerable interval violates query time')
                    self.need(earliest['latest'] >= max(evidence[e]['end_time'] for e in all_eids),
                              'future_evidence', 'Claimed answerable before required evidence')
                for rid in reason['relation_refs']:
                    relation = next((r for r in self.read(V2+'relations.json')['records'] if r['id'] == rid), None)
                    self.need(relation is not None, 'references', 'Unknown reasoning relation')
                    self.need(relation['type'] != 'temporal_precedes', 'dependency', 'Temporal order alone is not dependency')
                if task['status'] == 'PILOT_CANDIDATE':
                    self.need(any(len(s['bindings']) >= 2 for s in sets), 'dependency', 'T2 Pilot needs multiple evidence')
            if track == 'T3':
                monitor = private['monitoring']
                for interval in monitor['normal_intervals']:
                    self.interval(interval, duration)
                    self.need(trigger['monitoring_interval']['start_time'] <= interval['start_time']
                              and interval['end_time'] <= duration, 'monitoring', 'Normal interval outside Episode')
                    for eid in interval['evidence_ids']:
                        self.need(eid in evidence and evidence[eid]['start_time'] <= interval['end_time']
                                  and evidence[eid]['end_time'] >= interval['start_time'],
                                  'monitoring', 'No normal interval evidence overlap')
                self.need(not monitor['normal_intervals'] or bool(monitor['scoped_categories']),
                          'monitoring', 'Negative interval requires category scope')
            self.need(private['scoring']['mode'] == ('CANDIDATE_DIAGNOSTIC_ONLY'
                      if task['status'] == 'PILOT_CANDIDATE' else 'DISABLED'), 'maturity', 'Wrong status/scoring gate')
            self.need(bool(private['reference_items']) if task['status'] == 'PILOT_CANDIDATE' else True,
                      'scoring', 'Pilot has no scoreable reference fields')
            for gid in task['assessment']['evidence_gaps']:
                self.need(gid in gaps and tid in gaps[gid]['affected_task_ids'], 'gaps', 'Gap/task backlink missing')
        for gid, gap in gaps.items():
            self.need(set(gap['affected_task_ids']) == {t['task_id'] for t in tasks if gid in t['assessment']['evidence_gaps']},
                      'gaps', 'Gap affected-task set mismatch')
        statistics = {'definition_count':len(tasks), 'candidate_count':sum(t['status'] != 'UNSUITABLE' for t in tasks),
                      'by_track':dict(Counter(t['track'] for t in tasks)),
                      'by_track_candidates':dict(Counter(t['track'] for t in tasks if t['status'] != 'UNSUITABLE')), 'by_status':dict(Counter(t['status'] for t in tasks)),
                      'by_subtask':dict(Counter(t['subtask'] for t in tasks)), 'gold_count':0,
                      'hard_scoring_count':0, 't3_positive_count':0}
        self.need(package['statistics'] == statistics, 'statistics', 'Statistics mismatch')
        return dict(self.checks)

def self_test(package, schema):
    cases = []
    def add(name, mutate): cases.append((name, mutate))
    add('duplicate_id', lambda p: p['tasks'][1].update(task_id=p['tasks'][0]['task_id']))
    add('wrong_track', lambda p: p['tasks'][0].update(subtask='T2.1'))
    add('gold_promotion', lambda p: p['tasks'][0]['maturity'].update(gold_answer={'ok':True}))
    add('invalid_status', lambda p: p['tasks'][0].update(status='GOLD'))
    add('hard_score_promotion', lambda p: p['tasks'][0]['evaluator_private']['scoring'].update(hard_score_eligible=True))
    add('unknown_ref', lambda p: p['tasks'][0]['evaluator_private']['record_refs'][0].update(id='STEP-404'))
    add('pointer_mismatch', lambda p: p['tasks'][0]['evaluator_private']['record_refs'][0].update(json_pointer='/observed_steps/0'))
    add('unsafe_source_path', lambda p: p['source_manifest'].append({'path':'../outside.json','sha256':'0'*64}))
    add('media_manifest_change', lambda p: p['media'].update(duration_sec=700))
    add('future_set_evidence', lambda p: p['tasks'][0]['evaluator_private']['required_evidence_sets'][0]['bindings'][0].update(evidence_id='LC-680-2'))
    add('future_reference_item', lambda p: p['tasks'][0]['evaluator_private']['reference_items'][0].update(evidence_ids=['LC-680-2']))
    add('out_of_bounds_checkpoint', lambda p: p['tasks'][0]['evaluator_private']['trigger'].update(checkpoint_times=[999]))
    add('invented_release_time', lambda p: p['evidence_registry']['SRC-R18'].update(availability_time=134.748))
    add('invented_effective_time', lambda p: p['evidence_registry']['SRC-R18'].update(effective_from=134.748))
    add('invented_answerable_time', lambda p: p['tasks'][4]['evaluator_private']['reasoning'].update(earliest_answerable_time={'earliest':161.2,'latest':161.2,'status':'VERIFIED'}))
    add('unreleased_rule_pilot', lambda p: p['tasks'][4].update(status='PILOT_CANDIDATE'))
    add('probe_state_pollution', lambda p: p['tasks'][6]['evaluator_private']['trigger'].update(isolation_required=False))
    add('public_answer_leak', lambda p: p['tasks'][0]['agent_public']['input'].update(candidate_answer={'x':True}))
    add('public_private_evidence_id', lambda p: p['tasks'][6]['agent_public']['input'].update(question='See LC-680-2'))
    add('public_answer_const', lambda p: p['tasks'][0]['agent_public'].update(payload_schema={'const':{'answer':'completed'}}))
    add('full_event_access', lambda p: p['tasks'][0]['evaluator_private']['record_refs'][0].update(access='AGENT_VISIBLE'))
    add('t3_question_conversion', lambda p: p['tasks'][8]['agent_public']['input'].update(question='Is there an error?'))
    add('t3_window_reset', lambda p: p['tasks'][8]['evaluator_private']['trigger'].update(monitoring_interval={'start_time':560.2,'end_time':579.2}))
    add('fabricated_t3_onset', lambda p: p['tasks'][10]['evaluator_private']['monitoring'].update(error_onset=76.2))
    add('fabricated_recovery', lambda p: p['tasks'][11]['evaluator_private']['monitoring'].update(resolved_at=431.2308))
    add('invented_normal_interval', lambda p: p['tasks'][8]['evaluator_private']['monitoring']['normal_intervals'][0].update(end_time=700))
    add('whole_episode_normal', lambda p: p['tasks'][8]['evaluator_private']['monitoring'].update(whole_episode_normal=True))
    add('event_order_as_dependency', lambda p: p['tasks'][6]['evaluator_private']['reasoning'].update(relation_refs=['V2-R9']))
    add('span_mismatch', lambda p: p['tasks'][6]['evaluator_private']['reasoning'].update(dependency_span_sec=999))
    add('score_answer_mismatch', lambda p: p['tasks'][2]['evaluator_private']['reference_items'][0].update(value='empty'))
    add('statistics_mismatch', lambda p: p['statistics'].update(candidate_count=12))
    add('changed_frozen_source_hash', lambda p: p['source_manifest'][0].update(sha256='0'*64))
    results = []
    for name, mutate in cases:
        altered = copy.deepcopy(package)
        mutate(altered)
        try:
            # Keep path/hash negative meaningful even in fast, non-I/O mutation checks.
            audit = Audit()
            for source in altered['source_manifest']: audit.path(source['path'])
            audit.validate(altered, schema, verify_sources=name == 'changed_frozen_source_hash')
        except (Invalid, KeyError, ValueError) as exc:
            results.append({'case':name,'rejected':True,'reason':str(exc)[:250]})
        else:
            raise AssertionError(f'Invalid fixture was accepted: {name}')
    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    package = json.loads((HERE/'task_candidates.json').read_text(encoding='utf-8'))
    schema = json.loads((HERE/'task_schema.json').read_text(encoding='utf-8'))
    checks = Audit().validate(package, schema)
    results = self_test(package, schema) if args.self_test else []
    report = {'status':'PASS', 'schema_version':package['schema_version'],
              'check_count':sum(checks.values()), 'checks':checks,
              'negative_test_count':len(results), 'negative_tests':results,
              'statistics':package['statistics'],
              'package_sha256':hashlib.sha256((HERE/'task_candidates.json').read_bytes()).hexdigest(),
              'schema_sha256':hashlib.sha256((HERE/'task_schema.json').read_bytes()).hexdigest(),
              'scope':'Static schema/time/reference/source-hash/privacy/maturity checks only',
              'semantic_truth_verified':False, 'runtime_availability_verified':False,
              'probe_isolation_executed':False, 'history_necessity_experiment_executed':False}
    if args.write_report:
        (HERE/'validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','check_count':sum(checks.values()),
                      'negative_tests_rejected':len(results),'statistics':package['statistics']},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
