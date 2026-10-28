# 测试入口

现有测试保留原位，保持导入和 fixture 路径：

```powershell
python -X utf8 -m unittest discover -s annotation_pipeline/tests -p "test_*.py" -v
python -X utf8 -m unittest discover -s experiments/icme2027_pilot -p "test_*.py" -v
```

P01 测试可能物化帧并检查旧 Git HEAD。本次验收通过 scripts/verify_layout.py 在禁止网络的副本中执行，不写原实验目录。当前上下文的历史门禁失败与恢复冻结上下文后的补充测试分开记录，不能改原审计或 Gold 让测试通过。

未来跨 Episode 契约测试放在本目录，模块单元测试仍可随模块保留。
