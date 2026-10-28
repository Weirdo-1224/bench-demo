# 提取验收

- PASS — json_utf8_parse: 40 JSON files parsed
- PASS — task_definition_count: actual=12
- PASS — task_id_unique: 12 unique IDs
- PASS — no_gold_promotion: all adjudicated_gt=null
- PASS — four_cases: four JSON case cards
- PASS — times_within_video: max=680.212867 duration=696.929567
- PASS — t1_checkpoints_exact: exact source precision retained
- PASS — t2_query_exact: early/late anchors retained
- PASS — media_count: actual=12
- PASS — media_hashes: all byte-identical
- PASS — video_omitted_by_size: size=91608663
- PASS — secret_scan: hits=[]
- PASS — excluded_private_dirs: no .git/__pycache__
- PASS — zip_crc: final testzip returned null across 80 members（补入 5 份现存历史报告快照后重打包）
- PASS — zip_single_root: every member is under GX010021_targeted_20261016/
- PASS — zip_decompression: final archive all 80 members opened successfully

总体：PASS。最终 ZIP 在写入本记录并刷新 manifest 后再次构建和复验。
