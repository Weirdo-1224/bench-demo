"""Prepare and verify review evidence only; never adjudicate or run benchmark tasks."""
from __future__ import annotations
import bisect
import csv
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / 'golden_episode/GX010021'
OUT = EP / 'evidence'
MEDIA = EP / 'source/GX010021.MP4'
IDS = ['GX010021-T1-001', 'GX010021-T2-002', 'GX010021-T2-003']

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(f'{cmd[0]} failed: {r.stderr[-4000:]}')
    return r.stdout

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def rp(p):
    return p.relative_to(ROOT).as_posix()

def hms(t):
    return f'{int(t//3600):02}:{int(t%3600//60):02}:{t%60:06.3f}'

def probe(p, frames=False):
    cmd = ['ffprobe', '-v', 'error', '-of', 'json']
    if frames:
        cmd += ['-select_streams', 'v:0', '-show_frames', '-show_entries',
                'frame=best_effort_timestamp,best_effort_timestamp_time,duration,pkt_duration']
    else:
        cmd += ['-show_format', '-show_streams']
    return json.loads(run(cmd + [str(p)]))

def md5s(p):
    s = run(['ffmpeg', '-v', 'error', '-i', str(p), '-map', '0:v:0',
             '-fps_mode', 'passthrough', '-f', 'framemd5', '-'])
    return [line.split(',')[-1].strip() for line in s.splitlines() if line and not line.startswith('#')]

def pointer(d, ptr):
    for part in ptr.lstrip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        d = d[int(part)] if isinstance(d, list) else d[part]
    return d

tasks_doc = read(EP / 'tasks/v1_candidates/pilot_task_candidates.json')
tasks = {t['task_id']: t for t in tasks_doc['tasks'] if t['task_id'] in IDS}
events_doc = read(EP / 'annotations/v1_candidate/events.json')
objects_doc = read(EP / 'annotations/v1_candidate/objects.json')
reviews_doc = read(EP / 'annotations/v1_candidate/review_queue.json')
raw = read(EP / 'source/annotations.json')
evreg = {e['id']: e for e in events_doc['evidence']}
evmap = {e['id']: e for e in events_doc['events']}
obmap = {o['id']: o for o in objects_doc['objects']}
rqmap = {q['id']: q for q in reviews_doc['review_items']}
source_files = [p for folder in ['source', 'annotations', 'tasks', 'annotation_reports', 'reports']
                for p in (EP / folder).rglob('*') if p.is_file()]
source_files += [ROOT / 'docs/Long_Horizon_Streaming_Agent_Benchmark_Overall_Design_v1.0 (1).md']
before = {rp(p): sha(p) for p in source_files}
meta = probe(MEDIA)
vs = next(s for s in meta['streams'] if s['codec_type'] == 'video')
audio = [s for s in meta['streams'] if s['codec_type'] == 'audio']
if audio:
    raise RuntimeError('This preparation recipe expects the inspected source with no audio; revise audio trimming before reuse.')
sf = probe(MEDIA, True)['frames']
tb = Fraction(vs['time_base'])
pts = [int(f['best_effort_timestamp']) for f in sf]
times = [float(Fraction(x)*tb) for x in pts]
step = pts[1] - pts[0]
assert all(b-a == step for a,b in zip(pts, pts[1:])), 'CFR mapping must be reworked for VFR input'
assert len(pts) == int(vs['nb_frames'])
source_hashes = md5s(MEDIA)
assert len(source_hashes) == len(pts)
print(f'Source checked: {len(pts)} video frames, {len(audio)} audio streams', flush=True)

# No concatenated highlights: adjacent partitions retain every decoded source frame.
specs = [
    ('C00',0,139,'prefix_context'), ('C01',139,166,'primary'),
    ('C02',166,194,'bridge'), ('C03',194,239.3,'primary'),
    ('C04',239.3,269,'bridge'), ('C05',269,293,'primary'),
    ('C06',293,461,'bridge'), ('C07',461,530,'bridge'),
    ('C08',530,560,'dialogue_context'), ('C09',560,581,'primary'),
    ('C10',581,594,'bridge'), ('C11',594,605,'primary'),
    ('C12',605,632,'bridge'), ('C13',632,641.3,'primary'),
    ('C14',641.3,687,'bridge'), ('C15',687,692.3,'primary'),
]
clips = []
(OUT/'clips').mkdir(exist_ok=True)
(OUT/'frames').mkdir(exist_ok=True)
mapping_path = OUT/'clips/time_mapping.csv'
with mapping_path.open('w', encoding='utf-8', newline='') as mf:
    writer = csv.writer(mf)
    writer.writerow(['clip_id','clip_frame_index','clip_pts','clip_time_base','clip_time_sec',
                     'source_frame_index','source_pts','source_time_base','source_time_sec'])
    for cid,start,end,role in specs:
        first = bisect.bisect_left(times,start)
        stop = bisect.bisect_left(times,end)
        file = OUT/f'clips/{cid}_{start:07.3f}_{end:07.3f}.mp4'
        cmd = ['ffmpeg','-v','error','-nostdin','-y','-i',str(MEDIA),'-map','0:v:0','-map','0:a?',
               '-vf',f'trim=start_frame={first}:end_frame={stop},setpts=PTS-STARTPTS',
               '-c:v','libx264','-crf','0','-preset','veryfast','-fps_mode','passthrough',
               '-video_track_timescale','30000','-map_metadata','-1','-write_tmcd','0',
               '-movflags','+faststart',str(file)]
        run(cmd)
        cm = probe(file)
        cf = probe(file,True)['frames']
        cv = next(s for s in cm['streams'] if s['codec_type']=='video')
        ctb = Fraction(cv['time_base'])
        hashes = md5s(file)
        assert hashes == source_hashes[first:stop], f'{cid}: decoded pixel mismatch'
        assert len(cf)==stop-first==len(hashes)
        offset = Fraction(pts[first])*tb
        for i,f in enumerate(cf):
            cp = int(f['best_effort_timestamp'])
            assert Fraction(cp)*ctb == Fraction(pts[first+i])*tb-offset
            writer.writerow([cid,i,cp,str(ctb),f'{float(Fraction(cp)*ctb):.9f}',
                             first+i,pts[first+i],str(tb),f'{times[first+i]:.9f}'])
        clips.append({'clip_id':cid,'path':file.relative_to(OUT).as_posix(),'role':role,
                      'requested_source_interval_sec':[start,end],'interval_semantics':'[start,end)',
                      'first_source_frame_index':first,'last_source_frame_index':stop-1,
                      'first_source_pts':pts[first],'last_source_pts':pts[stop-1],
                      'source_time_base':str(tb),'first_source_frame_time_sec':times[first],
                      'last_source_frame_time_sec':times[stop-1],'clip_time_base':str(ctb),
                      'frame_count':stop-first,'duration_sec':float(cv['duration']),
                      'time_mapping':'source_time = clip_frame_pts * clip_time_base + first_source_frame_time',
                      'frame_mapping_csv':'clips/time_mapping.csv','audio_stream_count':0,
                      'audio_status':'ABSENT_IN_SOURCE','codec':cv['codec_name'],
                      'encoding':'libx264 CRF 0 lossless; native dimensions, cadence and pixel format',
                      'source_pixel_format':vs['pix_fmt'],'clip_pixel_format':cv['pix_fmt'],
                      'decoded_frame_md5_matches_source':True,'sha256':sha(file),'ffmpeg_command':cmd})
        print(f'{cid}: {start:.3f}--{end:.3f}s, {stop-first} frames; lossless mapping PASS',flush=True)

cmap = {c['clip_id']:c for c in clips}
alloc = {IDS[0]:['C00','C01','C02','C03'],
         IDS[1]:[f'C{i:02}' for i in range(8,14)],
         IDS[2]:[f'C{i:02}' for i in range(16)]}

facts = []
def add(task,number,question,intervals,eids,focus,risk,kind='visual',extra_refs=None):
    fid = f'{task}-F{number:02}'
    intervals = [list(x) for x in intervals]
    eligible = alloc[task]
    links = []
    for a,b in intervals:
        for cid in eligible:
            c = cmap[cid]; x,y = c['requested_source_interval_sec']
            if max(a,x) < min(b,y) or (a==b and x<=a<y):
                lo,hi = max(a,x),min(b,y)
                links.append({'clip_id':cid,'source_interval_sec':[lo,hi],
                              'clip_seek_interval_sec':[max(0,lo-c['first_source_frame_time_sec']),
                                                        max(0,hi-c['first_source_frame_time_sec'])]})
    refs = [{'evidence_id':e,'registry_pointer':f'/evidence/{next(i for i,v in enumerate(events_doc["evidence"]) if v["id"]==e)}',
             'source':evreg[e]['source'],'kind':evreg[e]['kind'],'time':evreg[e].get('time')} for e in eids]
    facts.append({'fact_id':fid,'task_id':task,'neutral_verification_question':question,
                  'source_intervals_sec':intervals,'evidence_ids':eids,'source_refs':refs,
                  'additional_source_refs':extra_refs or [],'clips':links,'observation_focus':focus,
                  'potential_conflict_or_limitation':risk,'verification_kind':kind,
                  'observability':'PENDING_INDEPENDENT_REVIEW',
                  'earliest_sufficient_time_sec':None,'earliest_time_status':'PENDING',
                  'earliest_search_intervals_sec':intervals,'decision_status':'PENDING'})

t=IDS[0]
add(t,1,'199–235秒期间，器具与容器内材料之间发生了什么动作？',[(194,235.5)],['V-E027-01','V-E027-02'],'记录接触、运动、开始/停止边界。','不能仅凭器具接近液面判定正在电动运行；原视频无音轨。')
add(t,2,'器具工作端何时、以何种方式离开容器内材料？',[(233,237)],['V-E027-03'],'逐帧区分暂时抬升和该动作段结束。','提离不自动证明断电或规范步骤完成。')
add(t,3,'截至239.3秒，器具位于哪里，是否仍由手持或接触容器？',[(235,239.3)],['V-E028-01'],'记录最后可见位置及手部接触。','位置按画面参照；不能引用239.3秒以后的画面。')
add(t,4,'该动作段开始前，容器内材料呈现哪些可见外观特征？',[(194,200.2)],['V-E027-01'],'记录颜色、分层、表面状态，不反推配方。','视觉外观不能独立确定所有化学成分。')
add(t,5,'该动作段结束前，容器内材料呈现哪些可见外观特征？',[(229,239.3)],['V-E027-02','V-E027-03'],'记录宏观均匀程度及仍可辨识的差异。','表面外观不证明全部材料充分混匀。')
add(t,6,'194–239.3秒前后涉及的混合容器能否连续识别为同一物体？',[(194,239.3)],['V-E027-01','V-E028-01'],'跟踪轮廓、位置、接触和出画/再入画。','同一候选对象ID不能代替视觉追踪。','continuity')
add(t,7,'动作段与其后放置动作中的器具能否连续识别为同一物体？',[(194,239.3)],['V-E027-01','V-E027-03','V-E028-01'],'追踪本体与工作端，并记录遮挡。','短暂遮挡需要单独登记，不能默认身份成立。','continuity')
add(t,8,'截至239.3秒，在可见历史中这个器具的同类动作段次序是什么？',[(0,239.3)],['V-E027-01','V-E027-02'],'仅审计该器具是否有更早同类动作，不重标整段视频。','次序不能只由当前片段或历史事件标题确定。','temporal_order')

t=IDS[1]
for i,rec in enumerate(range(39,44),1):
    ti=raw['text_timestamps'][rec-1]
    add(t,i,f'源对话记录R{rec:02}的说话者、字面内容与视频实际话语是否一致？',[(530,560)],
        [f'T-R{rec:02}'],'见清单末尾原始对话摘录；分别记文本语义与实际话语核实状态。',
        '源MP4没有音轨，无法从该媒体独立确认话语、说话者或话段终点；单点标签不是整句公开时刻。',
        'dialogue_occurrence',[{'path':'source/annotations.json','pointer':f'/texts/{rec-1}','point_label_sec':ti}])
add(t,6,'结合这组问答，各建议或许可指向什么对象、用途和条件，彼此关系是什么？',[(530,560)],
    ['T-R39','T-R40','T-R41','T-R42','T-R43'],'分别记录指代、条件、自述与规则的关系；保持原话。',
    '标签类型不证明规则替代；物资自述不证明实际库存；视频无法独立确认原话。','dialogue_semantics')
add(t,7,'560–563秒期间，是否有物质从瓶口进入烤模，进入什么位置？',[(558,564)],['V-E049-01'],
    '追踪瓶口、流体与落点；记录能直接辨识的物质特征。','用途许可不能代替实际倒入证据；反光和瓶口遮挡可能影响判断。')
add(t,8,'563–581秒期间，烤模如何被移动、倾斜或旋转？',[(563,581)],['V-E049-02'],
    '记录连续姿态变化、持模方式。','动作意图与实际涂覆效果需分别记录。')
add(t,9,'处理后烤模内壁的表面状态与覆盖范围能否直接辨识？',[(560,581),(632,641.3)],['V-E049-01','V-E049-02'],
    '分别记录模底、侧壁；指出无法观察区域。','不能由倾斜或评价词推断覆盖；反光、分辨率和遮挡风险待审核。')
add(t,10,'截至641.3秒，当前发生了哪些容器间的材料转移动作？',[(632,641.3)],['V-E053-01'],
    '追踪源容器、材料流和接受容器。','该检查点之后的刮取或终态不能用于此任务。')
add(t,11,'先前接受瓶中物质的烤模与当前接收材料的烤模能否连续关联？',[(560,641.3)],['V-E049-01','V-E049-02','V-E053-01'],
    '查看全部桥接区间，记录移位、出画及再出现。','候选烤模ID相同不证明物理身份；未出现在画面不等于被替换。','continuity')
add(t,12,'这组原话何时结束、何时实际公开，各建议何时生效能否独立确定？',[(530,560)],['T-R39','T-R40','T-R41','T-R42','T-R43'],
    '区分源标签、话段起止、送达与生效；所有缺失时间保持空值。','无音轨、无真实送达日志；不得用下一条标签时间补造话段结束。','availability')

t=IDS[2]
add(t,1,'152–157秒期间，盒内物质被转移到哪个容器？',[(146,158)],['V-E022-01'],'追踪盒口、材料流和接收容器。','物质名称需有可读证据；包装品牌不要求裁决。')
add(t,2,'158–165秒期间，杯内物质被转移到哪个容器？',[(157,166)],['V-E023-01'],'记录实际进入容器的动作和可见洒落。','不声称无损或全量转移。')
add(t,3,'上述量取与倒入动作使用的杯能否在两动作之间连续关联？',[(152,165)],['V-E022-01','V-E023-01'],'沿手持、位置和倒入过程追踪单杯。','杯组不等于单杯；此项只核验局部链。','continuity')
add(t,4,'269–282秒期间，袋中物质被转移到哪个容器？',[(269,283)],['V-E031-01'],'追踪袋口、接收容器与动作边界。','量取与加入混合容器是不同的转移边。')
add(t,5,'283–292秒期间，杯内物质被转移到哪个容器？',[(282,293)],['V-E032-01'],'记录实际落点与容器表面变化。','倾杯姿态不能独立证明物质已进入。')
add(t,6,'上述袋中量取与其后倒入动作使用的杯能否连续关联？',[(269,293)],['V-E031-01','V-E032-01'],'查看282秒前后的衔接，记录杯交换。','不能由相似外观确认跨阶段同杯。','continuity')
add(t,7,'595–604秒期间，袋中物质通过什么路径到达什么容器？',[(594,605)],['V-E051-01','V-E051-02'],'记录直接或经中间容器的实际路径。','单点末态与完整转移过程分开。')
add(t,8,'早段供粉袋与595–604秒出现的供料袋之间能否连续关联？',[(269,605)],['V-E031-01','V-E051-01'],'检查袋的存放、取回、外观及出画区间。','长期出画或同类袋替换无法仅凭两个端点排除。','continuity')
add(t,9,'各入料与后段倒出动作涉及的混合容器能否连续关联？',[(152,641.3)],['V-E023-01','V-E032-01','V-E051-01','V-E053-01'],'按全部桥接区间跟踪容器轮廓、移动和再次出现。','连续录像覆盖不等于目标持续在画内。','continuity')
add(t,10,'161.2–291.2秒期间，容器内材料的延续或替换情况能否确定？',[(161.2,291.2)],['V-E023-01','V-E027-02','V-E032-01'],'记录可见搅拌、移位和任何取出/替换。','不得把同一容器直接等同同一份材料。','continuity')
add(t,11,'291.2–602.2秒期间，容器内材料的延续或替换情况能否确定？',[(291.2,602.2)],['V-E032-01','V-E051-01'],'审计间隙内与该容器有关的加入、混合及移位。','含较长视角转离；其他材料加入不自动断开来源链。','continuity')
add(t,12,'602.2–633.2秒期间，容器内材料与倒出时材料能否连续关联？',[(602.2,633.2)],['V-E051-01','V-E053-01'],'检查搅拌至开始转移的全过程。','宏观混合状态与物质质量守恒分开。','continuity')
add(t,13,'633–679秒期间，材料实际转移到什么容器？',[(632,679)],['V-E053-01','V-E053-02'],'完整查看倾倒与后续操作，只记录可见转移。','不要求认定全量转移、近空或工具物理同一性。')
add(t,14,'接收材料的烤模与687–692.3秒出现的烤模能否连续关联？',[(633.2,692.3)],['V-E053-01','V-E053-02','V-E055-01'],'完整查看641.3–687秒桥接，包括搬运前后。','不能仅依据相同候选ID判断烤模或其材料同一。','continuity')
add(t,15,'截至692.3秒，烤模及其中材料被移到什么位置？',[(687,692.3)],['V-E055-01'],'记录移动、放置位置与门态，不评价预热。','禁止使用692.608秒后续评价或尾部画面。')
add(t,16,'在已提供历史中，有多少独立、直接可见的粉状材料入混合容器动作？',[(0,692.3)],['V-E031-01','V-E032-01','V-E051-01','V-E051-02'],
    '自行列出每次事件时间；区分上游量取和真正进入混合容器。','可见次数与实际总次数不同；不把历史计数作为前提。','count')
add(t,17,'是否存在无法排除额外加入或材料替换的遮挡/出画区间？',[(0,692.3)],['V-E032-01','V-E051-01'],
    '给出风险区间和受影响的转移边；无证据不可当作额外动作。','连续视频不能排除画外操作；标注缺失与客观不可观测性不同。','observability')
add(t,18,'奶操作所用杯与早先查看标签的杯能否独立确认为同一只？',[(139,166)],['V-E020-02','V-E022-01','V-E023-01'],
    '分别定位标签杯与实际奶杯并跟踪之间的接触。',
    '早先杯标签不证明后来所用杯相同；此项只审核身份可判定性，不新增评分字段。','observability')
add(t,19,'实际加入的奶量能否由杯规格和操作过程直接读证？',[(139,166)],['V-E020-02','V-E022-01','V-E023-01'],
    '记录实际奶杯可读规格、填充程度与可见洒落，无法测量则注明原因。',
    '指令量值不等于实测；身份未确认时不得套用别杯标签。','observability')
add(t,20,'粉操作所用杯的具体物理身份能否由此前历史独立确定？',[(139,293)],['V-E020-02','V-E031-01','V-E032-01'],
    '局部同杯衔接与相对早先杯的跨阶段同一性分开；只审计后者。',
    '杯组或相似外观不证明奶杯、糖杯、粉杯为同一只，不要求强认同一。','observability')
add(t,21,'首段实际加入的粉量能否由杯规格和操作过程直接读证？',[(269,293)],['V-E031-01','V-E032-01'],
    '记录可读规格、填充程度与实际转移；只审计可判定性，非新增量值评分。',
    '一杯指令不是实际杯规格或实际进入量的测量。','observability')
add(t,22,'后段实际加入的粉量能否由合法观察直接确定？',[(594,605)],['V-E051-01','V-E051-02'],
    '记录是否存在可读计量依据，直接倾倒不能凭时长估量。',
    '少量等自述或视觉印象不能替代精确体积/质量读证。','observability')

# Key frames are navigation aids, without captions, boxes, inferred identities or answers.
frame_targets = [144.2,153.2,156.2,159.2,161.2,194.2,199.2,234.2,235.2,236.2,238.2,
                 270.2,281.2,287.2,291.2,560.2,562.2,567.2,579.2,595.2,602.2,603.2,
                 633.2,641.2,645.2,677.2,687.2,689.2,691.2]
frames=[]
for n,target in enumerate(frame_targets,1):
    fi=bisect.bisect_left(times,target)
    actual=times[fi]
    cid=next(c['clip_id'] for c in clips if c['first_source_frame_index']<=fi<=c['last_source_frame_index'])
    path=OUT/f'frames/K{n:03}_{actual:010.6f}.png'
    run(['ffmpeg','-v','error','-nostdin','-y','-i',str(OUT/cmap[cid]['path']),'-vf',
         f'select=eq(n\\,{fi-cmap[cid]["first_source_frame_index"]})','-frames:v','1',str(path)])
    frames.append({'frame_id':f'K{n:03}','path':path.relative_to(OUT).as_posix(),
                   'requested_source_time_sec':target,'source_time_sec':actual,'source_pts':pts[fi],
                   'source_time_base':str(tb),'source_frame_index':fi,'clip_id':cid,
                   'clip_frame_index':fi-cmap[cid]['first_source_frame_index'],
                   'clip_time_sec':actual-cmap[cid]['first_source_frame_time_sec'],
                   'task_ids':[t for t in IDS if cid in alloc[t]],'sha256':sha(path),
                   'purpose':'navigation_only; no fact adjudication; complete clips remain required'})
write(OUT/'frames/index.json',{'access':'BLIND_REVIEW_NAVIGATION','frames':frames})

gaps=[
    {'id':'G01','task_ids':[IDS[2]],'interval_sec':[156.2,159.2],'object_refs':['O05'],'bridges':['C01'],'risk':'局部量杯交换或遮挡'},
    {'id':'G02','task_ids':[IDS[2]],'interval_sec':[161.2,270.2],'object_refs':['O01','O15'],'bridges':['C01','C02','C03','C04','C05'],'risk':'容器/材料延续、出画或替换'},
    {'id':'G03','task_ids':[IDS[2]],'interval_sec':[281.2,287.2],'object_refs':['O05'],'bridges':['C05'],'risk':'量取杯与倒入杯的局部衔接'},
    {'id':'G04','task_ids':[IDS[2]],'interval_sec':[291.2,595.2],'object_refs':['O01','O08','O15'],'bridges':['C05','C06','C07','C08','C09','C10','C11'],'risk':'长时出画、容器或袋替换、额外入料；不能用首尾默认连续'},
    {'id':'G05','task_ids':[IDS[1]],'interval_sec':[579.2,633.2],'object_refs':['O12'],'bridges':['C09','C10','C11','C12','C13'],'risk':'处理烤模至倒糊之间的身份连续性'},
    {'id':'G06','task_ids':[IDS[2]],'interval_sec':[602.2,633.2],'object_refs':['O01','O15'],'bridges':['C11','C12','C13'],'risk':'后段混合至转移的材料连续性'},
    {'id':'G07','task_ids':[IDS[2]],'interval_sec':[641.2,687.2],'object_refs':['O12','O15'],'bridges':['C13','C14','C15'],'risk':'倾倒后续、放置和搬运；不得只看开始倒糊和入炉'},
]
for g in gaps:
    g.update({'media_gap_status':'COVERED_WITH_CONTINUOUS_SOURCE_FRAMES',
              'identity_continuity_status':'PENDING_INDEPENDENT_REVIEW','uncovered_media_intervals_sec':[],
              'observed_occlusion_intervals_sec':None})

checks=[]
def check(label,condition):
    checks.append({'check':label,'status':'PASS' if condition else 'FAIL'})
    assert condition,label
check('exact_selected_task_ids',set(tasks)==set(IDS))
check('unique_atom_ids',len({f['fact_id'] for f in facts})==len(facts))
check('all_decisions_pending',all(f['decision_status']=='PENDING' for f in facts))
for t in IDS:
    for eid in tasks[t]['reference_event_ids']: check(f'{t}:event:{eid}',eid in evmap)
    for oid in tasks[t]['reference_object_ids']: check(f'{t}:object:{oid}',oid in obmap)
    for q in tasks[t]['existing_review_queue_ids']: check(f'{t}:review:{q}',q in rqmap)
    for e in tasks[t]['evidence_refs']:
        check(f'{t}:evidence:{e["evidence_id"]}',e['evidence_id'] in evreg)
        check(f'{t}:registry_pointer:{e["evidence_id"]}',pointer(events_doc,e['registry_ref'].split('#')[1])['id']==e['evidence_id'])
        check(f'{t}:evidence_time:{e["evidence_id"]}',e['time']['end_sec']<=tasks[t]['observation_cutoff'])
    for ref in tasks[t]['reference_facts']:
        ptr=ref['source_ref'].split('#')[1]
        d={'events':events_doc,'objects':objects_doc,'annotations':raw}[ref['artifact']]
        original=pointer(d,ptr)
        if ref['artifact']=='annotations':
            check(f'{t}:text:{ref["record_id"]}',original==ref['text'] and raw['text_timestamps'][ref['source_index']]==ref['time']['start_sec'])
        else:
            check(f'{t}:reference_fact:{ref.get("state_id",ref.get("event_id"))}:{ref.get("field")}',
                  all(original[k]==ref[k] for k in ['field','status','evidence_ids'] if k in ref) and
                  all(original[k]==ref[k] for k in ['before','after','value'] if k in ref))
    for cid in alloc[t]:check(f'{t}:clip_cutoff:{cid}',cmap[cid]['last_source_frame_time_sec']<tasks[t]['observation_cutoff'])
for a,b in zip(clips,clips[1:]):check(f'no_frame_gap:{a["clip_id"]}:{b["clip_id"]}',a['last_source_frame_index']+1==b['first_source_frame_index'])
for f in facts:
    check(f'{f["fact_id"]}:evidence_ids',all(x in evreg for x in f['evidence_ids']))
    check(f'{f["fact_id"]}:bounds',all(0<=a<=b<=tasks[f['task_id']]['observation_cutoff'] for a,b in f['source_intervals_sec']))
    check(f'{f["fact_id"]}:clip_refs',bool(f['clips']))
    for src in f['source_refs']:
        p=EP/src['source']['path'];check(f'{f["fact_id"]}:source:{p.name}',p.is_file())
        if 'line' in src['source']:check(f'{f["fact_id"]}:source_line',src['source']['line']<=len(p.read_text(encoding='utf-8-sig').splitlines()))
check('decoded_pixels_equal_for_all_clips',all(c['decoded_frame_md5_matches_source'] for c in clips))
check('audio_absence_documented',not audio and all(c['audio_status']=='ABSENT_IN_SOURCE' for c in clips))
check('source_integrity_unchanged',all(sha(ROOT/p)==v for p,v in before.items()))

manifest={'evidence_package_version':'1.0','episode_id':'GX010021','created_date':'2026-10-09',
          'timezone':'Asia/Shanghai','data_status':'CANDIDATE_EVIDENCE_PREPARATION','adjudication_performed':False,
          'access':'INTERNAL_ONLY; this manifest contains private source links; do not send to blind reviewer or evaluated Agent',
          'source_media':{'path':rp(MEDIA),'sha256':before[rp(MEDIA)],'duration_sec':float(vs['duration']),
                          'video_stream':vs,'audio_stream_count':0,'audio_status':'ABSENT_IN_SOURCE',
                          'source_timecode':vs.get('tags',{}).get('timecode'),
                          'time_origin':'media PTS seconds from first source frame, NOT wall clock or GoPro timecode'},
          'time_mapping_policy':{'selection':'source frame PTS in requested [start,end); no duplicate/drop/interpolation',
                                  'boundary_quantization':'first selected PTS >= start; last selected PTS < end; use CSV for exact frame time',
                                  'frame_duration_at_cutoff':'last frame display duration may extend past cutoff by <1 frame; no source frame at/after cutoff is included',
                                  'csv':'clips/time_mapping.csv','csv_sha256':sha(mapping_path),
                                  'precision':'integer PTS + rational time_base authoritative; decimal seconds are navigation'},
          'source_integrity':[{'path':p,'sha256_before':h,'sha256_after':sha(ROOT/p)} for p,h in before.items()],
          'clips':clips,'frames_index':'frames/index.json','facts':facts,'continuity_gaps_and_bridges':gaps,
          'tasks':[],
          'access_partition':{'blind_allowlist':['review_checklist.md','review_decisions.json','frames/index.json','clips/time_mapping.csv']+
                              [c['path'] for c in clips]+[f['path'] for f in frames],
                              'per_task_clip_allowlist':alloc,
                              'internal_only':['evidence_manifest.json','internal_reference.md','history_necessity_plan.md','prepare_evidence.py'],
                              'delivery':'copy only allowlisted task-specific review assets to independent review; never mount parent project; physical shared-root access is not a permission boundary',
                              'evaluated_agent':'none of these review artifacts are Agent inputs; only causal observations and query/answer_type at query_time'},
          'validation':{'status':'PASS','checks':checks,'independent_fact_verification':False,
                        'history_experiments_executed':False,'gold_count':0}}
for t in IDS:
    manifest['tasks'].append({'task_id':t,'source_pointer':f'/tasks/{next(i for i,v in enumerate(tasks_doc["tasks"]) if v["task_id"]==t)}',
                             'source_path':rp(EP/'tasks/v1_candidates/pilot_task_candidates.json'),'cutoff_sec':tasks[t]['observation_cutoff'],
                             'atom_count':sum(f['task_id']==t for f in facts),'fact_ids':[f['fact_id'] for f in facts if f['task_id']==t],
                             'review_clip_ids':alloc[t],'original_reference_facts':tasks[t]['reference_facts'],
                             'original_evidence_refs':tasks[t]['evidence_refs'],
                             'original_required_evidence_sets':tasks[t].get('required_evidence_sets',[]),
                             'original_pending_verification':tasks[t]['pending_verification'],
                             'candidate_earliest_answerable_time':tasks[t].get('earliest_answerable_time'),
                             'verified_earliest_answerable_time':None,
                             'readiness':'VISUAL_REVIEW_READY; DIALOGUE_AUDIO_AND_RELEASE_TIME_UNVERIFIABLE_FROM_THIS_SOURCE' if t==IDS[1] else 'INDEPENDENT_VISUAL_REVIEW_READY',
                             'hard_scoring_eligible':False})
write(OUT/'evidence_manifest.json',manifest)

decision_rows=[]
for f in facts:
    decision_rows.append({'fact_id':f['fact_id'],'task_id':f['task_id'],'status':'PENDING',
                          'neutral_verification_question':f['neutral_verification_question'],
                          'verdict':None,'observed_value':None,'observability':None,
                          'observed_source_intervals_sec':[],'review_clip_ids':[],
                          'earliest_sufficient_time_sec':None,'earliest_sufficient_time_interval_sec':None,
                          'occlusion_or_offscreen_intervals_sec':[],'continuity_verdict':None,
                          'alternative_explanations':[],'source_type':None,'confidence':None,
                          'reviewer_id':None,'reviewed_at':None,'notes':None})
write(OUT/'review_decisions.json',{'package_version':'1.0','episode_id':'GX010021','status':'PENDING',
                                 'purpose':'independent_review_form; not Ground Truth',
                                 'verdict_options':['SUPPORTED','CONTRADICTED','UNCERTAIN','UNOBSERVABLE','INSUFFICIENT_EVIDENCE'],
                                 'decisions':decision_rows,'task_decisions':[{'task_id':t,'status':'PENDING',
                                 'answer':None,'earliest_answerable_time_sec':None,'earliest_answerable_time_interval_sec':None,
                                 'completion_criteria':None,'unresolved_fact_ids':[],'evidence_sufficiency':None,
                                 'reviewer_id':None,'reviewed_at':None} for t in IDS]})

lines=['# GX010021 独立核验清单（盲审）','',
       '本清单不含候选答案、历史 AI 判定或私有对象图。所有问题为待审核问题，不能当作事实。核验者只应收到本文件、空白裁决表及当前任务允许的媒体和时间索引；不要打开项目父目录或内部材料。',
       '', '本轮源视频为854×480、30000/1001 fps，时长696.929567秒，**没有音频流**。未合成音轨。原始对话摘录可供文本语义审核，无法用这份MP4独立证明实际话语、说话者、话段结束或公开时刻。',
       '', '时间均为原始媒体秒。剪辑时间从0开始；精确映射见 `clips/time_mapping.csv`。原始时间 = 剪辑帧PTS×剪辑time_base + 对应片段第一原始帧时间。区间按[start,end)选择源帧，切点量化至原帧网格；不能用文件名起点代替精确偏移。',
       '', '关键帧只作导航，索引见 `frames/index.json`；原帧时间与目标定位时间有所量化。请先看连续片段，再定位细节，不凭关键帧裁定跨时间身份。连续录像不保证目标持续可见，出画、遮挡、模糊都应登记。',
       '', '裁决填写 `review_decisions.json`：逐项填写观察值、verdict、observability、原媒体证据区间、剪辑ID、最早证据充分时间或区间、遮挡/出画区间、替代解释、置信度、审核者和时间。无足够证据时保持空值并注明缺口；标注尚未查清不能自动成为unknown真值。',
       '', '每项最早证据充分时间当前均未裁定；下列区间仅为搜索范围。任务级时间必须依赖核验后的必要事实及真实信息可见时刻；多项尚不充分时保持null。T1动作段结束与整个规范步骤完成分别记录。']
for t in IDS:
    fs=[f for f in facts if f['task_id']==t]
    lines += ['',f'## {t}','',f'媒体截止：**{tasks[t]["observation_cutoff"]:.3f} 秒**；{len(fs)}条原子核验项。',
              '', '允许观看的片段如下。不得观看本任务截止之后的片段，不能在共享目录中提前打开下一任务媒体。','',
              '| 片段 | 原媒体区间（秒） | 文件 |','|---|---|---|']
    for cid in alloc[t]:
        c=cmap[cid];a,b=c['requested_source_interval_sec']
        lines.append(f'| {cid} | {a:.3f}–{b:.3f} | [{c["path"]}]({c["path"]}) |')
    lines+=['','只复核本任务命题涉及的对象和动作，桥接片段用于连续性风险审计，不要求重新标注整段视频。',
            '', '| 原子项 | 待验证问题 | 原媒体定位/最早充分时间搜索范围（秒） | 观察重点 | 潜在混淆或缺口（非历史结论） |','|---|---|---|---|---|']
    for f in fs:
        rs='；'.join(f'{a:.3f}–{b:.3f}' for a,b in f['source_intervals_sec'])
        lines.append(f'| {f["fact_id"]} | {f["neutral_verification_question"]} | {rs} | {f["observation_focus"]} | {f["potential_conflict_or_limitation"]} |')
    lines+=['','### 逐项媒体定位与必要来源','']
    for f in fs:
        parts=[f'{x["clip_id"]}本地{hms(x["clip_seek_interval_sec"][0])}–{hms(x["clip_seek_interval_sec"][1])}' for x in f['clips']]
        lines.append(f'- `{f["fact_id"]}`：'+'；'.join(parts)+'。来源：原MP4对应源PTS帧'+('；末尾原始对话摘录（仅文本，话语真实性不可独立核实）' if f['verification_kind'] in ['dialogue_occurrence','dialogue_semantics','availability'] else '')+'。最早证据充分时间：**PENDING / null**。')
    if t==IDS[1]:
        lines+=['','本任务全部语义判断应分为“基于原始文字可解释”与“实际话语独立核实”两层。不得将第一层的结论代替第二层，不得由物资自述推定库存事实。当前问题涉及的631秒之后动作只能查看至641.3秒。']
    if t==IDS[2]:
        lines+=['','量杯的局部衔接、跨阶段杯身份和杯组指称分别登记。奶/粉身份与体积要分别记录证据，不要求推定品牌、全量转移、质量守恒或全程无画外加入。数量/身份可判定性项仅用于审核现有任务的不确定性边界。']
lines+=['','## 连续性桥接审计','',
        '下列区间已准备连续源帧；这只消除剪辑漏段，不决定对象或材料同一性。核验者填写实际遮挡/出画时间及受影响转移边。',
        '', '| 区间（秒） | 适用任务 | 所需桥接片段 | 观察目的 |','|---|---|---|---|']
for g in gaps: lines.append(f'| {g["interval_sec"][0]:.3f}–{g["interval_sec"][1]:.3f} | {", ".join(g["task_ids"])} | {", ".join(g["bridges"])} | {g["risk"]} |')
lines+=['','## 必要原始对话上下文（只供文本语义审核）','',
        '以下逐字复制源annotations的R37–R44，没有历史AI结论，也未整理为“有效规则”。点时间是源标签，**并非经核验话段起止或送达时间**；说话者角色同样只来自原标注。不得从无音轨视频假称听到这些话。',
        '', '| 源记录 | 点时间（秒） | 源类型标签 | 原文 |','|---|---|---|---|']
for rec in range(37,45):
    i=rec-1;lines.append(f'| R{rec:02} | {raw["text_timestamps"][i]:.3f} | {raw["text_types"][i]} | {raw["texts"][i]} |')
lines+=['','这些原文是必要的源证据上下文，不能发布为已验证答案。若独立核验必须确认实际话语，应提供可核对的原始音轨或对话记录与真实公开日志；本包对此保留待审核字段。','']
(OUT/'review_checklist.md').write_text('\n'.join(lines),encoding='utf-8')

# Independent task handoffs: each has its own blank form and blind checklist.
# The root checklist is a coordinator's combined blind version, not a per-task handoff.
combined = '\n'.join(lines)
common = combined.split(f'## {IDS[0]}')[0]
for ti,t in enumerate(IDS):
    folder=OUT/t
    folder.mkdir(exist_ok=True)
    start=combined.index(f'## {t}')
    end=combined.index(f'## {IDS[ti+1]}') if ti+1<len(IDS) else combined.index('## 连续性桥接审计')
    section=combined[start:end]
    page=common.replace('`review_decisions.json`','`review_decisions.json`（本任务独立表）')+section
    page=page.replace('`frames/index.json`','本文末尾本任务关键帧索引')
    page=page.replace('`clips/time_mapping.csv`','`../clips/time_mapping.csv`')
    page=page.replace('](clips/','](../clips/')
    page+='\n## 本任务连续性桥接\n\n'
    for g in gaps:
        if t in g['task_ids']:
            page+=f'- 原媒体{g["interval_sec"][0]:.3f}–{g["interval_sec"][1]:.3f}秒；片段{", ".join(g["bridges"])}；{g["risk"]}。实际遮挡区间及身份状态待填写。\n'
    if t==IDS[0]:
        page+='- 本任务动作区间已连续覆盖；0–194秒只用于同类动作次序审计，无需整段重新标注。\n'
    if t==IDS[1]:
        page+='\n'+combined[combined.index('## 必要原始对话上下文'):]
    page+='\n## 本任务关键帧索引（只作定位）\n\n| 帧 | 原媒体秒 | 剪辑 | 剪辑秒 | 图像 |\n|---|---|---|---|---|\n'
    for f in frames:
        if t in f['task_ids']:
            page+=f'| {f["frame_id"]} | {f["source_time_sec"]:.6f} | {f["clip_id"]} | {f["clip_time_sec"]:.6f} | [{f["path"]}](../{f["path"]}) |\n'
    (folder/'review_checklist.md').write_text(page+'\n',encoding='utf-8')
    form=read(OUT/'review_decisions.json')
    form['decisions']=[x for x in form['decisions'] if x['task_id']==t]
    form['task_decisions']=[x for x in form['task_decisions'] if x['task_id']==t]
    write(folder/'review_decisions.json',form)
    manifest['access_partition'].setdefault('independent_task_handoffs',{})[t]={
        'checklist':f'{t}/review_checklist.md','blank_decisions':f'{t}/review_decisions.json',
        'media_files':[cmap[c]['path'] for c in alloc[t]],
        'frame_files':[f['path'] for f in frames if t in f['task_ids']],
        'time_mapping':'clips/time_mapping.csv',
        'do_not_deliver':['review_checklist.md','frames/index.json','evidence_manifest.json','internal_reference.md',
                          'history_necessity_plan.md','prepare_evidence.py','other task checklists and media']}
    assert 'candidate_answer' not in page and 'REPORTED_SUPPORTED' not in page
    assert 'SUPPORTED |' not in page
    if t!=IDS[1]:assert 'Use a parchment paper' not in page
write(OUT/'evidence_manifest.json',manifest)

# Internal source archive and conflict trace, without modifying any upstream data.
il=['# GX010021 内部参考（禁止向盲审者或被评测Agent提供）','',
    '本文件保留候选事实、原引用及历史AI判断。全部候选，未经本轮视频事实裁决，Gold=0。盲审者只使用allowlist中本任务的材料，不能打开本文件或evidence_manifest.json。',
    '', '## 准备结论与限制','',
    '- 原媒体无音轨；标注中55条对话无法由本MP4听证。T2-002可开展视频动作与文本语义分层复核，但真实对话及公开时间审核条件不足。',
    '- 原始对话单点time不等于话段结束、availability或effective_from。所有真实时刻仍为null。',
    '- 提取[0,692.3)全部源帧，按任务分段并设置截止；没有提取692.608秒R55及尾部作为任务证据。源余段[692.3,696.929567)不属本轮任务合法输入，历史尾部缺口696.2–696.929567无须为这些任务补裁决。',
    '- 所有片段原帧解码MD5与来源逐帧一致。此校验只证明媒体技术完整性，不判断动作、身份、材料或Ground Truth。',
    '', '## 路径修复与引用边界','',
    '上游reference_facts的`../../annotations.json#/texts/...`为整理前遗留定位，当前实际唯一源为`golden_episode/GX010021/source/annotations.json`；`events.json`和`objects.json`实际在`annotations/v1_candidate/`。保留原字符串并通过artifact解析其JSON Pointer，本包不创建副本、不写回上游。任务media_ref的`../../source/GX010021.MP4`从tasks文件目录直接解释也不能找到实际文件；本包按Episode根规范化到现有source路径。',
    '', '## 历史冲突（全部为历史主张）','',
    '| 项目 | 历史分歧与后续修订 | 本包处理 |','|---|---|---|',
    '| E027/E028 | 初稿E027为200–234秒；后轮改为199–235秒。E028对象状态仍234–239秒，与约235.2秒提离及236.2–238.2秒放置重叠。 | 保留原引用；提取194–239.3秒连续过程；不裁定精确结束/完成时刻。 |',
    '| E049 | 初稿声称内壁沾油且起点566秒；后轮改为560–581秒；只报告倒油/旋转，内壁油膜仍UNCERTAIN。 | 分开核验进入、姿态、表面结果，不用R45 Success证实覆盖。 |',
    '| 时间转换 | 第二轮将MM:SS去冒号误写成绝对秒，如920.2→560.2、995.2→595.2、1033.2→633.2；第三轮纠正。 | 使用结构化time与更正后的绝对秒，原字符串只存内部。 |',
    '| E031/E032/E051 | 曾把量取/倒入/袋直倒混为三次加入；第三轮撤销，候选为E032与E051两处可见入混合容器，未排除隐藏加入。 | 盲审问题不提供次数，要求自行列出直接可见事件。 |',
    '| O05身份/量值 | 原稿将杯组和搅拌/刮糊黑工具当同一件；整合层分离O16/O17未知同一性。早段1/4 CUP不证明奶杯或粉杯规格，half cup/one cup是指令。 | 局部转移杯身份与跨阶段身份分别审核，不增加体积评分。 |',
    '| T2-002规则 | R39→R41→R43只是待审局部替代链，supersedes/effective_from未核实；R40/R42为自述。 | 原文仅作为必要文本上下文；实际话语/可见性缺口单列。 |',
    '| T2-003持续性 | O01/O08/O12/O15相同候选ID不能证明间隙身份；原任务只列首尾时段。 | 补齐中间全部帧，审计7类间隙；视觉身份仍PENDING。 |',
    '| E053完整记录 | 633–679秒包含刮取/末态；T2-002截止641.3，只允许初段；T2-003可用后续。 | C13在641.3切分；C14仅供T2-003，不能发给T2-002审核或Agent。 |',
    '| 黄油/预热 | 早轮“完全融化”和“已预热”被后续降级/修正。 | 桥接视频中的这些操作仅为连续性背景，不借此新增任务/规则或裁决。 |',
    '', '## 原子事实与上游引用','']
for t in IDS:
    il += [f'### {t}','', '原候选答案（未核验）：','```json',json.dumps(tasks[t]['candidate_answer'],ensure_ascii=False,indent=2),'```','',
           '完整任务定义（内部原样快照）：','```json',json.dumps(tasks[t],ensure_ascii=False,indent=2),'```','']
    for f in [x for x in facts if x['task_id']==t]:
        related=[r for r in tasks[t]['reference_facts'] if set(r['evidence_ids']) & set(f['evidence_ids'])]
        il += [f'#### {f["fact_id"]}','',f'中性核验问题：{f["neutral_verification_question"]}',
               '', '关联候选reference_facts（多个字段可拆成独立命题，重复油膜字段不重复计数）：',
               '```json',json.dumps(related,ensure_ascii=False,indent=2),'```','',
               '来源证据（历史V-/I-/T-分类不升级）：','```json',
               json.dumps([evreg[e] for e in f['evidence_ids']],ensure_ascii=False,indent=2),'```','']
il += ['## 相关结构化记录和历史来源完整保留','']
for label,d in [('events',list(evmap.values())),('objects',list(obmap.values())),('review_items',list(rqmap.values()))]:
    keys=set()
    for t in IDS:keys.update(tasks[t].get({'events':'reference_event_ids','objects':'reference_object_ids','review_items':'existing_review_queue_ids'}[label],[]))
    selected=[x for x in d if x['id'] in keys]
    il += [f'### {label}','', '```json',json.dumps(selected,ensure_ascii=False,indent=2),'```','']
il += ['## 时间覆盖、桥接与技术校验','',f'{len(clips)}个连续片段，{len(frames)}帧导航，{len(facts)}条原子项；{len(checks)}项结构/来源/截止/完整性检查PASS。',
       '', '桥接详见manifest.continuity_gaps_and_bridges；uncovered_media_intervals为空只说明提取不漏段。observed_occlusion_intervals=null，表示未由Codex裁决视频遮挡；不是全程无遮挡结论。',
       '', '阅读来源与SHA-256（生成前后未变）：','', '| 来源 | SHA-256 |','|---|---|']
for p,h in before.items():il.append(f'| {p} | {h} |')
(OUT/'internal_reference.md').write_text('\n'.join(il)+'\n',encoding='utf-8')

# Parse generated records and verify every delivered file once more.
read(OUT/'evidence_manifest.json');read(OUT/'review_decisions.json');read(OUT/'frames/index.json')
assert all((OUT/c['path']).is_file() for c in clips)
assert all((OUT/f['path']).is_file() for f in frames)
assert all(sha(ROOT/p)==h for p,h in before.items())
import re
for t,hand in manifest['access_partition']['independent_task_handoffs'].items():
    page_path=OUT/hand['checklist']
    page=page_path.read_text(encoding='utf-8')
    form=read(OUT/hand['blank_decisions'])
    assert all(x['task_id']==t and x['status']=='PENDING' and x['verdict'] is None for x in form['decisions'])
    assert len(form['decisions'])==sum(f['task_id']==t for f in facts)
    for forbidden in ['candidate_answer','REPORTED_SUPPORTED','gold_answer','oil_permitted_for_this_pan_preparation',
                      'visible_flour_additions','历史主张']:
        assert forbidden not in page
    for link in re.findall(r'\]\(([^)]+)\)',page):
        assert page_path.parent.joinpath(link).is_file(),(t,link)
    assert all(cmap[c]['last_source_frame_time_sec']<tasks[t]['observation_cutoff'] for c in alloc[t])
with mapping_path.open(encoding='utf-8') as mf:
    rows=list(csv.DictReader(mf))
assert len(rows)==sum(c['frame_count'] for c in clips)
assert [int(r['source_frame_index']) for r in rows]==list(range(len(rows)))
manifest['validation']['handoff_validation']={
    'status':'PASS','task_forms_pending':True,'task_media_cutoffs_checked':True,
    'blind_forbidden_content_scan':'PASS','local_markdown_links_resolve':True,
    'mapping_row_count':len(rows),'source_frame_indices_contiguous':True,
    'keyframe_preview_scope':'navigation readability only; no factual adjudication',
    'filesystem_security_boundary_created':False,
    'delivery_requirement':'send each task handoff allowlist only; do not share whole evidence/project directory'}
write(OUT/'evidence_manifest.json',manifest)
print(json.dumps({'atoms':{t:sum(f['task_id']==t for f in facts) for t in IDS},
                  'clips':len(clips),'frames':len(frames),'checks':len(checks),'status':'PASS',
                  'gold':0,'audio':'ABSENT_IN_SOURCE'},ensure_ascii=False),flush=True)
