# 保守目录整理记录 · 2026-10-28

本次建立目录职责、文档入口、数据索引和可自动验证的复现边界。最终没有迁移既有文件：Session 1 文档试迁移后发现冻结路径约束，已恢复原位。不修改源码、原视频、请求、记忆、输入帧、原始响应、Gold 或历史结果。

```text
bench-demo/
├── README.md                          简洁根入口（更新）
├── docs/                              研究文档
│   ├── README.md                      文档索引（新增）
│   ├── Long_Horizon_...v1.0 (1).md     当前设计（原位）
│   ├── SESSION1*.md                   历史研究，保留冻结路径
│   ├── experiments.md                 实验版本说明（新增）
│   └── maintenance/                   本次映射、盘点和验收（新增）
├── annotation_pipeline/               通用标注代码（兼容保留）
│   ├── providers/、schemas/、prompts/
│   └── tests/                         原单元测试
├── benchmark/README.md                共用模块职责规划（新增）
├── data/                              Episode 索引与未来规范（新增）
│   ├── README.md
│   └── episodes/GX010021/episode.json  旧数据定位，不复制资产
├── golden_episode/GX010021/            旧 Episode 整体原位
│   ├── source/、annotations/、annotation_reports/
│   ├── evidence/、tasks/、scripts/、reports/
│   └── showcase/
├── experiments/icme2027_pilot/         实验结果及完整重构链，原位
│   ├── runs/p01-v1/                   请求、响应、帧、记忆、checkpoint、代码快照
│   ├── archive_phase1/                历史准备阶段
│   ├── request_ledger/、audit/
│   └── …                              原协议、Gold、脚本、测试和结果
├── tests/README.md                    测试入口（新增）
├── scripts/                           verify_layout.py 和 check_catalog.py（新增）
├── archive/README.md                  历史材料索引（新增）
├── _showcase_export/                  历史展示（原位）
├── Benchmark_Research_Showcase_Final.html  历史展示（原位）
├── .venv/                             本地环境
├── .recovery/layout-20261028/           本地恢复快照（忽略）
└── .local/layout-validation/           本地验证副本、完整清单和日志（忽略）
```

六类职责分别由 docs、annotation_pipeline/benchmark、data/旧 Episode、experiments、tests/模块内 tests、archive/历史索引承载。新 Episode 的目标树见 [数据说明](../../data/README.md)，当前有效实验见 [版本说明](../experiments.md)，历史材料见 [归档索引](../../archive/README.md)。

## 扫描、快照与恢复

整理分支为 `chore/conservative-layout-20261028`，整理前 HEAD 为 `635cc72905cc2b12ebdd54a12d85cbdba74b05fd`，初始工作区无未提交或未跟踪文件。

扫描 5,381 个文件、3,384,284,850 字节：跟踪 263 个，忽略 5,118 个，未忽略的未跟踪文件 0 个。按目录统计见 [inventory-summary.json](inventory-summary.json)。完整路径、大小、状态和哈希在 `.recovery/layout-20261028/inventory.json`，逐文件旧/新映射在 `.local/layout-validation/full-file-mapping.csv`。Git 内部数据库通过 bundle 保护，不作为普通资产重复盘点。

快照 `files/` 复制全部文件，包括 .venv、凭据、ignored 视频、响应、帧和运行记录，并逐文件核对 SHA-256。repository.bundle 保存完整 Git 历史和分支，已通过 git bundle verify。

恢复时在新的空目录执行 `git clone <快照路径>/repository.bundle <新目录>`，再将 files 中清单对应文件复制到新目录并核对 inventory 哈希，不覆盖当前工作区。快照含凭据，不上传共享仓库。它是同盘恢复点，长期保存可再复制到研究数据备份位置。

## 调整和暂缓

- 更新根 README 和 .gitignore，新增文档、数据、实验及归档入口。
- 增加 GX010021 兼容 manifest，仅引用现有数据。
- 规划未来 benchmark 模块和新 Episode 布局，保留 Python 导入及脚本入口。
- 新增全量哈希、离线重放、评分、报告和测试自动验证。
- 原文件路径全部保留；机器可读职责映射见 [migration.json](migration.json) 和 [migration.csv](migration.csv)。

pilot.py 固定 golden_episode/GX010021，runtime.py 固定 runs/p01-v1，validate_v2.py 固定旧输出路径。Episode 的构建、验证、证据准备和展示脚本依赖父目录层级、相对资源与源哈希。迁移会影响请求身份、清单或审计，因此暂缓。Session 1 文档同样受 original_hashes 保护。展示导出和 HTML 需要独立资源验证，.venv 不重定位。

后续先实现显式 manifest 配置与旧路径兼容，再逐项验证引用、导入、入口和 P01 replay。新实验版本另存，保留旧代码快照和审计，不覆盖历史。

## Git 与本地资产

Git 保留代码、协议、研究文档、schemas、小型结构化标注、人工 Gold、证据/审核清单和已有结果；既有跟踪 PNG 继续保留。

视频、衍生帧/切片、原始请求/响应、账本、原始候选运行、凭据、环境、恢复快照和本次副本仅保留本地并独立备份。新增忽略规则覆盖未来 data Episode 的 raw、帧/切片及原始模型运行，未取消已有文件跟踪。忽略不代表不重要。

## 验收

见 [validation.md](validation.md) 与 [validation.json](validation.json)。当前审计的历史失败和冻结上下文补充测试分开报告。P01 原始文件哈希不变，P02 始终 PENDING；没有启动付费 API 或后续真实实验。
