"""Curated showcase assembly and simple source/media checks; no model calls.

Run from any directory. All writes stay in this script's showcase directory,
apart from TemporaryDirectory files used for optional decoding verification.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
EP = 'golden_episode/GX010021/'
V2 = EP + 'annotations/v2_video_model/'
TASK = EP + 'tasks/v2_candidates/task_candidates.json'
LOCAL = V2 + 'runs/session2-full-video/local_visual_checks/manifest.json'
FRAMES = EP + 'evidence/frames/index.json'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def pointer(data, ptr):
    for part in ptr.lstrip('/').split('/') if ptr else []:
        part = part.replace('~1', '/').replace('~0', '~')
        data = data[int(part)] if isinstance(data, list) else data[part]
    return data


def source(path, ptr=''):
    return {'path': path, 'json_pointer': ptr, 'sha256': sha(ROOT / path)}


def wrapped(path, ptr, summary=None):
    result = {'source': source(path, ptr), 'source_record': pointer(read(path), ptr)}
    if summary is not None:
        result['display_summary_zh'] = summary
    return result


# All captions describe single-frame display scope; event boundaries remain candidates.
# (existing image ID, caption, event IDs, evidence IDs, Session 3 task IDs)
T1, T2, T3 = [f'GX010021-V2-{x}' for x in ['T1-002', 'T2-003', 'T3-001']]
SELECTION = [
    ('K002', '奶盒与黑色量具处于量取阶段；不等于奶已进入主容器。', ['V2-E7'], ['H1-V-E022-01'], [T2]),
    ('K004', '量具在主容器上方倾斜，展示奶入主容器的候选阶段。', ['V2-E8'], ['H1-V-E023-01'], [T2]),
    ('K013', '量具内可见白色粉状物；这张图展示量取，不展示粉已入主容器。', ['V2-E12'], ['H1-V-E031-01'], [T2]),
    ('K015', '主容器表面可见白色粉层、量具在其上方；单帧不证明整段倾倒。', ['V2-E13'], ['H1-V-E032-01'], [T2]),
    ('LC-431-2', '玻璃容器中黄色液体与浅色固块共存的单帧候选。', ['V2-E19'], ['LC-431-2'], [T1]),
    ('LC-445-2', '黑色工具位于黄色材料中，仍可见浅色固态材料的单帧候选。', ['V2-E20'], ['LC-445-2'], [T1]),
    ('K017', '烤模底部可见局部液体、油瓶在附近；不能据此确认内壁全部覆盖。', ['V2-E24'], ['H1-V-E049-01'], [T3]),
    ('K018', '手持烤模的倾转候选阶段；这张静态图不证明完整旋转轨迹。', ['V2-E25'], ['H1-V-E049-02'], [T3]),
    ('LC-599-2', '纸袋在主容器上方倾斜、表面可见浅色粉状物；对应后段补粉候选。', ['H1-E051'], ['H1-V-E051-01', 'LC-599-2'], [T2]),
    ('LC-610-2', '搅拌器工作端在主容器中；对应后段搅拌候选，不能确认光滑终态。', ['H1-E052'], ['LC-610-2', 'H1-V-E052-01'], []),
    ('K025', '主容器倾斜，混合物向烤模转移；不证明全部材料转移完毕。', ['V2-E26', 'V2-E27'], ['V2-V24'], [T2]),
    ('LC-680-2', '烤模已有面糊，主容器仍见残留与黑色工具；这是末段 Probe 的原帧锚点。', [], ['LC-680-2'], [T2]),
]


def build():
    OUT.mkdir(exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    ann = read(V2 + 'annotation_manifest.json')
    tasks = read(TASK)
    evidence_package = read(EP + 'evidence/evidence_manifest.json')
    frames = read(FRAMES)['frames']
    local = read(LOCAL)['records']
    lookup = {r['frame_id']: (r, FRAMES, '/frames/' + str(i)) for i, r in enumerate(frames)}
    lookup.update({r['id']: (r, LOCAL, '/records/' + str(i)) for i, r in enumerate(local)})
    registry = {}

    def record(name, rid, collection='records', summary=None):
        if rid in registry:
            return rid
        path = V2 + name + '.json'
        rows = read(path)[collection]
        index = next(i for i, r in enumerate(rows) if r['id'] == rid)
        entry = wrapped(path, f'/{collection}/{index}', summary)
        r = entry['source_record']
        entry['kind'] = 'state' if collection == 'states' else name
        keys = ['id', 'action', 'label', 'start_time', 'end_time', 'objects', 'object_id',
                'attribute', 'value', 'valid_from', 'valid_to', 'transition_event_id', 'type',
                'from_id', 'to_id', 'event_ids', 'text_type', 'text', 'source_timestamp',
                'availability_time', 'effective_from', 'annotation_status', 'confirmation_status',
                'source_type', 'observability', 'uncertainties', 'evidence_refs', 'time_precision',
                'material_identity', 'identity_status', 'validity_status', 'reported_observation_interval']
        entry['key_fields'] = {k: r[k] for k in keys if k in r}
        registry[rid] = entry
        return rid

    assets = []
    for rid, caption, events, evids, tids in SELECTION:
        raw, path, ptr = lookup[rid]
        original = EP + 'evidence/' + raw['path'] if rid.startswith('K') else raw['path']
        name = Path(original).name if rid.startswith('K') else rid + '_' + Path(original).name
        destination = OUT / 'assets' / name
        shutil.copyfile(ROOT / original, destination)
        for eid in events:
            record('events', eid)
        for eid in evids:
            record('evidence_index', eid)
        time = raw.get('source_time_sec', raw.get('source_time'))
        pts = raw['source_pts']
        bindings = []
        for eid in evids:
            e = registry[eid]['source_record']
            start, end = e['start_time'], e['end_time']
            outside = max(start - time, time - end, 0)
            bindings.append({'evidence_id': eid, 'candidate_locator_sec': [start, end],
                             'frame_minus_locator_end_sec': round(time - end, 9),
                             'outside_locator_distance_sec': round(outside, 9),
                             'association': 'EXACT_SOURCE_PTS_SNAPSHOT' if start == end == time else
                             ('FRAME_WITHIN_CANDIDATE_RANGE' if outside == 0 else 'NEAR_APPROXIMATE_LOCATOR_ENDPOINT'),
                             'semantic_confirmation': 'NOT_ADJUDICATED'})
        clip = None
        if rid.startswith('K'):
            c = next(c for c in evidence_package['clips'] if c['clip_id'] == raw['clip_id'])
            clip = {'clip_id': c['clip_id'], 'path': EP + 'evidence/' + c['path'],
                    'sha256': c['sha256'], 'source_interval_sec': c['requested_source_interval_sec'],
                    'source_frame_index': raw['source_frame_index'],
                    'clip_frame_index': raw['clip_frame_index'], 'clip_time_sec': raw['clip_time_sec'],
                    'time_mapping': c['time_mapping']}
        assets.append({'asset_id': rid, 'relative_path': 'assets/' + name,
                       'original_image_path': original, 'source_video_path': ann['media']['source_path'],
                       'source_video_sha256': ann['media']['sha256'],
                       'original_video_time_sec': time, 'source_pts': pts,
                       'time_base': raw.get('source_time_base', raw.get('time_base')),
                       'requested_seek_time_sec': raw.get('requested_source_time_sec', raw.get('requested_seek_time')),
                       'sha256': sha(destination), 'expected_original_sha256': raw['sha256'],
                       'newly_extracted': False, 'transformation': 'BYTE_IDENTICAL_COPY',
                       'origin_metadata': wrapped(path, ptr), 'historical_clip': clip,
                       'display_caption_zh': caption, 'event_ids': events, 'evidence_ids': evids,
                       'event_bindings': [{'event_id': e,
                           'candidate_event_interval_sec': [registry[e]['source_record']['start_time'], registry[e]['source_record']['end_time']],
                           'outside_candidate_event_distance_sec': round(max(
                               registry[e]['source_record']['start_time'] - time,
                               time - registry[e]['source_record']['end_time'], 0), 9),
                           'association_basis': 'DISPLAY_STAGE_LINK_VIA_EVIDENCE_NOT_EXACT_EVENT_BOUNDARY'} for e in events],
                       'task_ids': tids, 'evidence_bindings': bindings,
                       'confirmation_status': 'UNCONFIRMED', 'human_review': 'NOT_REVIEWED',
                       'display_semantics': 'SINGLE_FRAME_ILLUSTRATION_NOT_CONTINUOUS_ACTION_ADJUDICATION'})

    by_asset = {a['asset_id']: a for a in assets}
    # Eight frame anchors, never exact event onset/offset declarations.
    timeline_ids = ['K002', 'K004', 'K013', 'K015', 'LC-431-2', 'LC-599-2', 'LC-610-2', 'K025']
    titles = ['奶量取候选', '奶加入主容器候选', '粉量取候选', '粉入主容器候选',
              '黄油处理局部快照', '后段直接补粉候选', '后段搅拌候选', '混合物入模候选']
    timeline = []
    for i, (aid, title) in enumerate(zip(timeline_ids, titles), 1):
        a = by_asset[aid]
        timeline.append({'node_id': f'timeline-{i:02}', 'title_zh': title,
                         'description_zh': a['display_caption_zh'], 'asset_ids': [aid],
                         'video_time_sec': a['original_video_time_sec'],
                         'timestamp_role': 'DISPLAY_FRAME_ANCHOR_NOT_CONFIRMED_ACTION_BOUNDARY',
                         'event_ids': a['event_ids'], 'evidence_ids': a['evidence_ids'],
                         'candidate_event_intervals': [{'event_id': e,
                             'start_time': registry[e]['source_record']['start_time'],
                             'end_time': registry[e]['source_record']['end_time'],
                             'time_precision': registry[e]['source_record']['time_precision'],
                             'confirmation_status': registry[e]['source_record']['confirmation_status']}
                             for e in a['event_ids']],
                         'source_refs': [registry[e]['source'] for e in a['event_ids'] + a['evidence_ids']],
                         'annotation_status': 'CANDIDATE', 'confirmation_status': 'UNCONFIRMED'})

    event_ids = ['V2-E7', 'V2-E8', 'V2-E13']
    state_ids = ['H1-O05.S06', 'H1-O01.S05', 'H1-O01.S07']
    state_captions = ['历史候选：量具观察组中当时的一只杯用于量取奶；不建立跨阶段同一性。',
                      '历史候选：主容器新增奶；观察区间不等于持续有效区间。',
                      '历史候选：主容器液面新增白色粉堆；不能由外观识别全部材料成分。']
    for rid, summary in zip(state_ids, state_captions):
        record('objects', rid, 'states', summary)
    relation_ids = ['PATH-03', 'PATH-04', 'PATH-06']
    for rid in relation_ids:
        record('relations', rid)
    for rid, summary in {
        'V2-E7': '奶盒与量具之间的量取/转移候选；杯身份和容量未知。',
        'V2-E8': '奶从量具进入主容器的候选；与量取分开。',
        'V2-E13': '粉从量具进入主容器的候选；模型区间与历史定位边界不同。',
        'PATH-03': '奶盒→量具观察组的候选转移，不代表主容器已入料。',
        'PATH-04': '量具观察组→主容器的候选奶路径，物理杯身份未确认。',
        'PATH-06': '量具观察组→主容器的候选粉路径，不默认是奶阶段同一只杯。',
    }.items():
        registry[rid]['display_summary_zh'] = summary
    record('procedure', 'SRC-R26', summary='来源文本提出加粉要求；单点时间标签不证明指令已送达或生效。')
    examples = {'event_ids': event_ids, 'state_ids': state_ids, 'relation_ids': relation_ids,
                'optional_guidance_ids': ['SRC-R26'],
                'display_links': [
                    {'asset_ids': ['K002'], 'event_id': 'V2-E7', 'state_id': 'H1-O05.S06', 'relation_id': 'PATH-03',
                     'description_zh': '奶盒→量具的量取候选；尚未进入主容器。'},
                    {'asset_ids': ['K004'], 'event_id': 'V2-E8', 'state_id': 'H1-O01.S05', 'relation_id': 'PATH-04',
                     'description_zh': '量具→主容器的入料候选；与量取分开展示。'},
                    {'asset_ids': ['K013', 'K015'], 'event_id': 'V2-E13', 'state_id': 'H1-O01.S07', 'relation_id': 'PATH-06',
                     'description_zh': '先展示杯中粉，再展示主容器粉层；静态图不替代整个倾倒段。'}],
                'display_rule': 'Render key_fields and short summaries; source_record is the unmodified audit snapshot.'}

    def case(task_id):
        index = next(i for i, t in enumerate(tasks['tasks']) if t['task_id'] == task_id)
        result = wrapped(TASK, '/tasks/' + str(index))
        t = result['source_record']
        result.update({k: t[k] for k in ['task_id', 'track', 'subtask', 'title', 'status', 'maturity',
                                        'agent_public', 'evaluator_private', 'assessment']})
        result['agent_output_contract'] = wrapped(TASK, '/public_output_contracts/' + t['agent_public']['output_contract_id'])
        for rr in t['evaluator_private']['record_refs']:
            name = Path(rr['path']).stem
            collection = 'states' if rr['kind'] == 'state' else 'records'
            record(name, rr['id'], collection)
        evids = {b['evidence_id'] for s in t['evaluator_private']['required_evidence_sets'] for b in s['bindings']}
        for eid in evids:
            if tasks['evidence_registry'][eid]['kind'] == 'evidence':
                record('evidence_index', eid)
            else:
                record('procedure', eid)
        result['task_evidence_registry'] = {e: wrapped(TASK, '/evidence_registry/' + e) for e in sorted(evids)}
        return result

    c1, c2, c3 = [case(tid) for tid in [T1, T2, T3]]
    c1['display_checkpoints'] = [{'video_time_sec': time, 'asset_id': aid,
                                'evidence_id': aid, 'state_id': 'STATE-' + aid,
                                'candidate_visible_phase': 'liquid_and_solid',
                                'validity_scope': 'THIS_FRAME_ONLY'}
                               for time, aid in zip([431.2308, 445.211433], ['LC-431-2', 'LC-445-2'])]
    c1['display_summary_zh'] = '两帧局部相态候选均为固液共存；比例、倒入时最终相态与中间持续状态未知。'

    stages = [
        ('H1-V-E022-01', ['K002'], ['PATH-03'], '奶盒到量具', 'MEASURING_NOT_MAIN_CONTAINER_ENTRY'),
        ('H1-V-E023-01', ['K004'], ['PATH-04'], '奶从量具到主容器', 'CANDIDATE_MATERIAL_ENTRY'),
        ('H1-V-E031-01', ['K013'], ['PATH-05'], '粉袋到量具', 'MEASURING_NOT_MAIN_CONTAINER_ENTRY'),
        ('H1-V-E032-01', ['K015'], ['PATH-06'], '粉从量具到主容器', 'CANDIDATE_MATERIAL_ENTRY'),
        ('H1-V-E051-01', ['LC-599-2'], ['PATH-07'], '晚期粉袋到主容器', 'CANDIDATE_DIRECT_ENTRY'),
        ('V2-V24', ['K025'], ['V2-R12'], '主容器到烤模', 'CANDIDATE_DOWNSTREAM_TRANSFER'),
        ('LC-680-2', ['LC-680-2'], [], '当前烤模内容锚点', 'EXACT_PTS_CANDIDATE_SNAPSHOT'),
    ]
    c2['historical_evidence_display'] = []
    for eid, aids, rels, role, kind in stages:
        e = registry[eid]['source_record']
        c2['historical_evidence_display'].append({'evidence_id': eid, 'role_zh': role,
            'candidate_interval_sec': [e['start_time'], e['end_time']], 'source': registry[eid]['source'],
            'asset_ids': aids, 'image_times_sec': [by_asset[a]['original_video_time_sec'] for a in aids],
            'relation_ids': rels, 'operation_kind': kind, 'confirmation_status': e['confirmation_status'],
            'locator_precision': e['locator_precision']})
    c2['material_graph'] = {'nodes': [], 'edges': []}
    for rid, label in [('V2-O5', '奶盒观察'), ('V2-O7', '粉袋观察'), ('V2-O13', '量具观察组（物理同一性未知）'),
                       ('V2-O1', '主混合容器候选'), ('V2-O10', '烤模候选')]:
        record('objects', rid)
        c2['material_graph']['nodes'].append({'object_id': rid, 'label_zh': label,
                                            'identity_status': registry[rid]['source_record']['identity_status'],
                                            'source': registry[rid]['source']})
    for rid in ['PATH-03', 'PATH-04', 'PATH-05', 'PATH-06', 'PATH-07', 'V2-R12']:
        r = registry[rid]['source_record']
        c2['material_graph']['edges'].append({'relation_id': rid, 'from_id': r['from_id'], 'to_id': r['to_id'],
            'type': r['type'], 'event_ids': r['event_ids'], 'evidence_ids': r['evidence_refs'],
            'source': registry[rid]['source'], 'confirmation_status': r['confirmation_status'],
            'display_style': 'DASHED_CANDIDATE', 'uncertainties': r['uncertainties']})
    c2['span_explanation'] = {
        'earliest_evidence_id': 'H1-V-E022-01', 'earliest_candidate_locator_sec': 153.2,
        'latest_evidence_id': 'LC-680-2', 'latest_source_frame_sec': 680.212867,
        'candidate_locator_span_sec': 527.012867,
        'earliest_selected_asset_id': 'K002', 'earliest_selected_frame_sec': by_asset['K002']['original_video_time_sec'],
        'latest_selected_asset_id': 'LC-680-2',
        'selected_frame_span_sec': round(680.212867 - by_asset['K002']['original_video_time_sec'], 9),
        'source': source(TASK, '/tasks/6/evaluator_private/reasoning'),
        'interpretation_zh': '527.012867秒来自候选定位153.2到原帧680.212867；选定图片实际跨度约526.993134秒。跨度不证明历史必要性或最小充分性。'}
    c2['unknown_fields'] = {k: c2['evaluator_private']['candidate_answer'][k] for k in
                           ['physical_utensil_identity', 'material_continuity', 'total_volume', 'complete_transfer']}
    c2['display_summary_zh'] = '七个证据定位连接奶/粉的不同候选入料路径与当前烤模内容；图中的同类量具节点表示观察组，不能读成同一物理杯。'

    c3['normative_display'] = []
    for rid, label in zip(['SRC-R39', 'SRC-R40', 'SRC-R41', 'SRC-R42', 'SRC-R43'],
                          ['垫纸要求', '无纸自述', '剩余黄油建议', '无黄油自述并提议用油', '本烤模语境中的用油许可候选']):
        record('procedure', rid)
        c3['normative_display'].append({'record_id': rid, 'summary_zh': label, 'source': registry[rid]['source'],
            'source_label_time_sec': registry[rid]['source_record']['source_timestamp'],
            'availability_time': None, 'effective_from': None})
    c3['visual_evidence_display'] = [{'evidence_id': e, 'asset_ids': [a], 'source': registry[e]['source']}
                                   for e, a in [('H1-V-E049-01', 'K017'), ('H1-V-E049-02', 'K018')]]
    c3['display_summary_zh'] = '仅针对本烤模语境中垫纸/剩余黄油被许可用油替代的候选负例；不证明全片正常。公开/生效时间及Gold正常分母缺失，评分关闭。'
    c3['excluded_evidence_note'] = {'evidence_id': 'V2-V24', 'record_ids': ['L5-06', 'V2-E25'],
        'reason_zh': '原记录保留未来入模证据引用；Session 3用油负例集合已排除它，网页不得用633–678秒帧支持560–579秒的正常结论。'}

    cross = read(V2 + 'crosscheck.json')
    cross_examples = []
    for cid, v1ids, eventids, aids, title, conclusion in [
        ('late-flour', ['E051'], ['H1-E051'], ['LC-599-2'], '后段补粉未被独立全片模型单独表示',
         'V1-only是覆盖差异；599秒局部帧佐证候选阶段，不证明595–604秒完整动作及全片入料次数。'),
        ('late-mixing', ['E052'], ['H1-E052'], ['LC-610-2'], '后段第三次搅拌未被独立全片模型单独表示',
         '610秒可见工作端在容器内；第三次序号和605–631秒区间仍来自历史候选，不确认光滑完成。'),
        ('butter-phase', ['E042', 'E043'], ['V2-E19', 'V2-E20'], ['LC-431-2', 'LC-445-2'], '黄油完全融化主张过度推断',
         '模型完全融化与局部固块快照有分歧；统一候选限定局部相态，不裁定加热次数与倒入时最终相态。'),
    ]:
        comparisons, historical = [], []
        for vid in v1ids:
            i = next(i for i, r in enumerate(cross['v1_event_comparisons']) if r['v1_event_id'] == vid)
            comparisons.append(wrapped(V2 + 'crosscheck.json', '/v1_event_comparisons/' + str(i)))
            rows = read(EP + 'annotations/v1_candidate/events.json')['events']
            j = next(j for j, r in enumerate(rows) if r.get('event_id', r.get('id')) == vid)
            historical.append(wrapped(EP + 'annotations/v1_candidate/events.json', '/events/' + str(j)))
        cross_examples.append({'example_id': cid, 'title_zh': title, 'v1_event_ids': v1ids,
            'unified_event_ids': eventids, 'asset_ids': aids,
            'comparisons': comparisons, 'historical_candidates': historical,
            'model_claims': [{'event_id': eid, 'claim': registry[eid]['source_record'].get('model_claim'),
                              'source': registry[eid]['source']} for eid in eventids],
            'currently_supportable_conclusion_zh': conclusion, 'confirmation_status': 'UNCONFIRMED'})
    cross_examples[-1]['source_time_discrepancy'] = {
        'record_ref': source(V2 + 'crosscheck.json', '/v1_event_comparisons/42'),
        'original_note_time_sec': 445.245, 'display_frame_pts_time_sec': 445.211433,
        'note_zh': '交叉核验E043原文写445.245秒，与局部帧PTS445.211433不同；原文原样保留，展示检查点以Session 3及局部帧PTS为准，未修改源文件。'}

    # Include evidence and objects referenced by selected records, without upgrading them.
    changed = True
    while changed:
        old_count = len(registry)
        for item in list(registry.values()):
            r = item['source_record']
            for eid in r.get('evidence_refs', []):
                record('evidence_index', eid)
            for oid in r.get('objects', []) + ([r['object_id']] if 'object_id' in r else []):
                record('objects', oid)
        changed = old_count != len(registry)

    input_paths = [V2 + f + '.json' for f in ['annotation_manifest', 'events', 'objects', 'procedure',
                   'relations', 'anomaly_candidates', 'evidence_index', 'crosscheck']]
    input_paths += [V2 + f for f in ['crosscheck_report.md', 'full_video_report.md']]
    input_paths += [EP + 'tasks/v2_candidates/' + f for f in ['task_candidates.json', 'task_schema.json',
                    'task_feasibility_report.md', 'track_coverage_report.md', 'evidence_gaps.md']]
    input_paths += [EP + 'source/annotations.json', EP + 'source/GX010021.MP4', FRAMES, LOCAL,
                    EP + 'evidence/evidence_manifest.json', EP + 'evidence/review_decisions.json',
                    V2 + 'runs/session2-full-video/local_visual_checks/pts_validation.json']
    input_paths += [(EP + 'annotation_reports/' + f.name) for f in (ROOT / EP / 'annotation_reports').glob('*.md')]
    input_paths += [s['path'] for s in ann['sources']]
    source_catalog = [{'path': p, 'sha256': sha(ROOT / p)} for p in sorted(set(input_paths))]
    gaps = [wrapped(TASK, '/evidence_gaps/' + str(i)) for i, g in enumerate(tasks['evidence_gaps'])
            if g['gap_id'] in ['G01', 'G02', 'G04', 'G05', 'G06', 'G07', 'G08', 'G09']]
    manifest = {
        'showcase_version': 'session4a-showcase-v1', 'created_date': '2026-10-13', 'timezone': 'Asia/Shanghai',
        'path_conventions': {'source_paths': 'repository-root-relative', 'asset_relative_path': 'showcase-relative'},
        'episode_overview': {'episode_id': 'GX010021', 'media': ann['media'],
            'annotation_status': ann['annotation_status'], 'human_review': ann['human_review'],
            'semantic_truth_verified': ann['semantic_truth_verified'],
            'gold_records': ann['statistics']['gold_records'], 'source': source(V2 + 'annotation_manifest.json'),
            'summary_zh': '厨房烘焙操作的候选标注与任务展示；原片时长696.929567秒，无音轨。',
            'scope': 'EXISTING_EVIDENCE_CURATION_ONLY', 'new_vlm_calls': 0, 'new_extracted_frames': 0,
            'counts': {'timeline_nodes': len(timeline), 'annotation_events': 3, 'annotation_states': 3,
                       'annotation_relations': 3, 'optional_guidance': 1, 'assets': len(assets), 'crosscheck_cases': 3}},
        'timeline': timeline, 'annotation_examples': examples,
        'track1_case': c1, 'track2_case': c2, 'track3_case': c3,
        'crosscheck_examples': {'statistics': wrapped(V2 + 'crosscheck.json', '/category_counts'),
            'v1_comparison_count': len(cross['v1_event_comparisons']),
            'count_interpretation_zh': '56条V1事件：28宏观匹配、8冲突、20 V1-only；不是准确率或事实裁决。',
            'examples': cross_examples},
        'asset_registry': assets, 'record_registry': registry, 'source_catalog': source_catalog,
        'source_id_paths': {s['source_id']: s['path'] for s in ann['sources']},
        'evidence_gaps': {'inherited_session3_gaps': gaps,
            'showcase_limits': [
                {'id': 'S01', 'description_zh': '历史定位区间与模型动作区间不完全一致；K013/K015/K017分别在历史定位尾端后一帧内，不冒充精确检查点。',
                 'asset_ids': ['K013', 'K015', 'K017']},
                {'id': 'S05', 'description_zh': 'K015比V2-E13模型结束时间晚1.224267秒，K018比V2-E25模型开始早0.766667秒；通过历史定位关联候选阶段，不强行使模型边界匹配图片。',
                 'asset_ids': ['K015', 'K018']},
                {'id': 'S02', 'description_zh': '没有公开观察ID/运行送达日志；本包资产ID与私有证据ID用于研究展示，不能代替Agent在线观察ID。', 'source': source(TASK, '/protocol')},
                {'id': 'S03', 'description_zh': 'E043交叉核验注释时间与实际帧PTS不同；详见黄油差异实例。', 'source': source(V2 + 'crosscheck.json', '/v1_event_comparisons/42')},
                {'id': 'S04', 'description_zh': '没有独立人工裁决、连续材料/物体身份核验、异常及恢复Gold；图片齐备不等于评测证据成熟。',
                 'source': source(V2 + 'annotation_manifest.json', '/statistics')}],
            'missing_display_images': [],
            'semantic_gaps_resolved_by_curation': False},
        'reuse_policy': 'Research showcase includes private candidate references. Do not use as evaluated Agent input.',
    }
    write('showcase_manifest.json', manifest)
    return manifest


def validate(manifest, verify_media=False):
    errors, checks = [], []

    def check(name, ok):
        checks.append({'check': name, 'pass': bool(ok)})
        if not ok:
            errors.append(name)

    duration = manifest['episode_overview']['media']['duration_sec']
    for s in manifest['source_catalog']:
        p = ROOT / s['path']
        check('source exists/hash: ' + s['path'], p.is_file() and sha(p) == s['sha256'])

    def walk(x):
        if isinstance(x, dict):
            if 'source_record' in x and 'source' in x:
                s = x['source']
                check('source snapshot: ' + s['path'] + '#' + s['json_pointer'],
                      sha(ROOT / s['path']) == s['sha256'] and pointer(read(s['path']), s['json_pointer']) == x['source_record'])
            if set(['path', 'json_pointer', 'sha256']).issubset(x):
                check('source pointer: ' + x['path'] + '#' + x['json_pointer'],
                      (ROOT / x['path']).is_file() and sha(ROOT / x['path']) == x['sha256'])
                pointer(read(x['path']), x['json_pointer'])
            for val in x.values():
                walk(val)
        elif isinstance(x, list):
            for val in x:
                walk(val)
    walk(manifest)

    records = manifest['record_registry']
    assets = {a['asset_id']: a for a in manifest['asset_registry']}
    tasks = read(TASK)
    for rid, item in records.items():
        r = item['source_record']
        check('original ID/status: ' + rid, r['id'] == rid and r['annotation_status'] == 'CANDIDATE' and r['confirmation_status'] == 'UNCONFIRMED')
        check('key fields unchanged: ' + rid, all(r[k] == val for k, val in item['key_fields'].items()))
        for ref in r.get('source_refs', []):
            path = manifest['source_id_paths'][ref['source_id']]
            pointer(read(path), ref['json_pointer'])
        for eid in r.get('evidence_refs', []):
            check('evidence ID: ' + rid + ' -> ' + eid, eid in records and records[eid]['kind'] == 'evidence_index')
        for k in ['start_time', 'end_time', 'valid_from', 'valid_to', 'source_timestamp']:
            if r.get(k) is not None:
                check('time bounds: ' + rid + ':' + k, 0 <= r[k] <= duration)
    for a in assets.values():
        p = OUT / a['relative_path']
        check('image copy/hash: ' + a['asset_id'], p.is_file() and sha(p) == a['sha256'] == sha(ROOT / a['original_image_path']) == a['expected_original_sha256'])
        check('image PTS/range: ' + a['asset_id'], 0 <= a['original_video_time_sec'] <= duration and
              abs(float(a['source_pts'] * Fraction(a['time_base'])) - a['original_video_time_sec']) < 0.000001)
        check('image status: ' + a['asset_id'], a['confirmation_status'] == 'UNCONFIRMED' and not a['newly_extracted'])
        for e in a['event_ids']:
            check('asset event ID: ' + a['asset_id'] + ':' + e, e in records and records[e]['kind'] == 'events')
        for tid in a['task_ids']:
            check('asset task ID: ' + a['asset_id'] + ':' + tid, tid in {t['task_id'] for t in tasks['tasks']})
        for b in a['evidence_bindings']:
            e = records[b['evidence_id']]['source_record']
            distance = max(e['start_time'] - a['original_video_time_sec'], a['original_video_time_sec'] - e['end_time'], 0)
            check('image locator association: ' + a['asset_id'] + ':' + b['evidence_id'],
                  abs(distance - b['outside_locator_distance_sec']) < 0.0000001 and distance < 1001 / 30000 + 0.000001)
        if a['historical_clip']:
            c = a['historical_clip']
            check('historical clip exists/hash: ' + c['clip_id'], (ROOT / c['path']).is_file() and sha(ROOT / c['path']) == c['sha256'])
    for node in manifest['timeline']:
        check('timeline original frame: ' + node['node_id'],
              node['video_time_sec'] == assets[node['asset_ids'][0]]['original_video_time_sec'])
        for interval in node['candidate_event_intervals']:
            event = records[interval['event_id']]['source_record']
            check('timeline original event interval: ' + interval['event_id'],
                  all(interval[k] == event[k] for k in ['start_time', 'end_time', 'time_precision', 'confirmation_status']))
    for link in manifest['annotation_examples']['display_links']:
        event, state, relation = [records[link[k]]['source_record'] for k in ['event_id', 'state_id', 'relation_id']]
        check('annotation event/state/relation link: ' + event['id'],
              state['transition_event_id'] == event['id'] and event['id'] in relation['event_ids'] and
              (state['object_id'] in [relation['from_id'], relation['to_id']]))
        check('annotation image/evidence relation: ' + event['id'], all(
              aid in assets for aid in link['asset_ids']) and any(
              eid in relation['evidence_refs'] for aid in link['asset_ids'] for eid in assets[aid]['evidence_ids']))
    for key in ['track1_case', 'track2_case', 'track3_case']:
        c = manifest[key]
        t = next(t for t in tasks['tasks'] if t['task_id'] == c['task_id'])
        check('Session 3 exact task: ' + c['task_id'], all(c[k] == t[k] for k in
              ['task_id', 'track', 'subtask', 'title', 'status', 'maturity', 'agent_public', 'evaluator_private', 'assessment']))
        check('no Gold/score promotion: ' + c['task_id'], c['maturity']['gold_answer'] is None and not c['evaluator_private']['scoring']['hard_score_eligible'])
    for cp in manifest['track1_case']['display_checkpoints']:
        check('exact T1 checkpoint image: ' + cp['asset_id'], cp['video_time_sec'] == assets[cp['asset_id']]['original_video_time_sec'])
    c2 = manifest['track2_case']
    query = c2['evaluator_private']['trigger']['query_time']
    displayed = c2['historical_evidence_display']
    check('T2 complete original evidence set', [s['evidence_id'] for s in displayed] == c2['evaluator_private']['reasoning']['required_history'])
    check('T2 no future display image', all(assets[aid]['original_video_time_sec'] <= query for s in displayed for aid in s['asset_ids']))
    for edge in c2['material_graph']['edges']:
        r = records[edge['relation_id']]['source_record']
        check('T2 unchanged material relation: ' + r['id'], all(
              edge[k] == r[k] for k in ['from_id', 'to_id', 'type', 'event_ids', 'confirmation_status', 'uncertainties'])
              and edge['evidence_ids'] == r['evidence_refs'])
    span = c2['span_explanation']
    check('T2 source span', abs(span['latest_source_frame_sec'] - span['earliest_candidate_locator_sec'] - span['candidate_locator_span_sec']) < 1e-8)
    check('T3 no fabricated incidents', manifest['track3_case']['evaluator_private']['monitoring']['error_events'] == [] and
          manifest['track3_case']['evaluator_private']['scoring']['mode'] == 'DISABLED')
    check('crosscheck actual statistics', manifest['crosscheck_examples']['statistics']['source_record'] == {'V1_ONLY': 20, 'BOTH_OBSERVED': 28, 'CONFLICT': 8})

    media_result = {'performed': False}
    if verify_media:
        from PIL import Image
        media = ROOT / manifest['episode_overview']['media']['source_path']
        probe_command = ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(media)]
        probe = json.loads(subprocess.check_output(probe_command, text=True, encoding='utf-8'))
        check('actual video duration/audio', abs(float(probe['format']['duration']) - duration) < 0.001 and not any(s['codec_type'] == 'audio' for s in probe['streams']))
        ordered = sorted(assets.values(), key=lambda a: a['source_pts'])
        select = '+'.join(f'eq(pts\\,{a["source_pts"]})' for a in ordered)
        with tempfile.TemporaryDirectory(prefix='gx-showcase-verify-') as td:
            command = ['ffmpeg', '-v', 'error', '-nostdin', '-i', str(media), '-map', '0:v:0',
                       '-vf', 'select=' + select, '-fps_mode', 'passthrough', str(Path(td) / 'frame-%02d.png')]
            subprocess.run(command, check=True, capture_output=True)
            decoded = sorted(Path(td).glob('frame-*.png'))
            check('decoded selected frame count', len(decoded) == len(ordered))
            frame_results = []
            for a, f in zip(ordered, decoded):
                with Image.open(f) as im, Image.open(OUT / a['relative_path']) as asset_im:
                    same = im.size == asset_im.size and im.convert('RGB').tobytes() == asset_im.convert('RGB').tobytes()
                check('source decoded pixels equal: ' + a['asset_id'], same)
                frame_results.append({'asset_id': a['asset_id'], 'source_pts': a['source_pts'], 'pixels_identical': same})
            command[-1] = '<temporary-directory>/frame-%02d.png'
        media_result = {'performed': True, 'ffprobe_command': probe_command,
                        'ffmpeg_command': command, 'frame_results': frame_results,
                        'scope': 'PTS_AND_PIXELS_ONLY_NOT_SEMANTIC_ADJUDICATION'}
    report = {'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
              'date': '2026-10-13', 'timezone': 'Asia/Shanghai', 'checks': checks,
              'check_count': len(checks), 'media_verification': media_result,
              'semantic_truth_verified': False, 'human_review': 'NOT_REVIEWED',
              'limits': 'Source/time/hash/contract checks do not establish Gold, exact action boundaries, physical identity, history necessity, or normal/anomaly truth.'}
    write('validation_report.json', report)
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'errors': errors,
                      'counts': manifest['episode_overview']['counts'], 'media_verification': verify_media}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--verify-media', action='store_true', help='Decode selected PTS once and compare original pixels; requires ffmpeg/ffprobe/Pillow.')
    args = parser.parse_args()
    data = read(EP + 'showcase/showcase_manifest.json') if args.validate_only else build()
    validate(data, args.verify_media)
