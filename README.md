# AIDDMIPTD: Multi-source Integrative Progressive Target Discovery Framework

## Overview
AIDDMIPTD is an open-source framework for small molecule target discovery. It takes a compound CAS number as input and outputs a ranked list of candidate targets through multi-source data integration, functional enrichment analysis, and deep learning-based prioritization.

**AIDDMIPTD（多源整合渐进式靶点发现框架）**。该项目以化合物CAS号为输入，经过多源靶点收集、整合、富集分析，最终利用Chemprop深度学习模型对候选靶点进行优先级排序，并支持断点续传和异常恢复。整体采用模块化设计，代码文件精简，关键算法细节均包含在内。

## Features
- Multi-source target collection (PubChem, SwissTargetPrediction, SEA, ChEMBL, PPB2)
- Data integration and overlap visualization (Venn diagrams)
- GO/KEGG enrichment analysis with disease keyword filtering
- Deep learning ranking using Chemprop (graph neural networks)
- Automatic caching and checkpointing for fault tolerance
- Modular design for easy extension

## Project list

```bash
AIDDMIPTD/
├── main.py                 # 主流程入口，支持断点续传
├── data_fetcher.py         # 多源靶点数据采集（含重试、缓存）
├── integration.py          # 多源数据整合、Venn图绘制
├── enrichment.py           # GO/KEGG富集分析及疾病关键词过滤
├── chemprop_ranker.py      # Chemprop深度学习排序器
├── utils.py                # 通用工具：CAS转SMILES、文件IO、日志
├── requirements.txt        # 依赖包列表
└── README.md               # 项目说明
```



## Installation
```bash
git clone https://github.com/yourusername/AIDDMIPTD.git
cd AIDDMIPTD
pip install -r requirements.txt
```

## Used

```bash
python main.py 123-45-6 --model /path/to/chemprop_model.pt --output results --cache cache
```

---

## 使用说明
1. 将以上所有文件保存到本地，目录结构如所示。
2. 安装依赖：`pip install -r requirements.txt`。
3. 运行示例：`python main.py 50-78-2`（阿司匹林的CAS号），如已有Chemprop模型可加`--model`参数。
4. 结果保存在`results/`目录下，包括：
   - `combined_targets.csv`：整合后的候选靶点列表。
   - `GO_enrichment.csv`、`KEGG_enrichment.csv`：富集分析结果。
   - `ranked_targets.txt`：最终排序后的靶点列表。
   - 以及其他中间可视化文件。

## 注意事项
- **数据源API**：部分数据源（如SwissTargetPrediction）需要网络访问，若无法连接或返回空，请检查网络或替换为本地数据库。
- **Chemprop模型**：排序需要预训练的多任务模型，若无可用模型，排序步骤将跳过（返回原始列表）。您可以使用Chemprop自行训练模型。
- **断点续传**：所有关键步骤的结果均自动缓存，重新运行时会跳过已完成步骤，适用于网络不稳定或长时运行场景。

这个项目为您提供了一个完整、可扩展的框架，满足科研级需求。如有任何问题，欢迎在GitHub仓库中提交Issue。
