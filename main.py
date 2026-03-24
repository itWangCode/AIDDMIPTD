"""
主流程：CAS号输入 -> 多源靶点收集 -> 整合 -> 富集分析 -> 深度学习排序
支持断点续传，每一步结果自动缓存
"""
import os
import argparse
from pathlib import Path

from utils import logger, cas_to_smiles, save_data, load_data
from data_fetcher import TargetFetcher
from integration import Integrator
from enrichment import EnrichmentAnalyzer
from chemprop_ranker import ChempropRanker

class MIPTD:
    def __init__(self, cas, output_dir='results', cache_dir='cache', model_path=None):
        self.cas = cas
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.model_path = model_path
        self.smiles = None
        self.raw_targets = None
        self.combined_df = None
        self.ranked_targets = None

        # 创建目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """执行完整流程"""
        logger.info(f"Starting MIPTD for CAS: {self.cas}")

        # Step 1: CAS转SMILES
        self.smiles = self._step1_smiles()
        if not self.smiles:
            logger.error("Failed to get SMILES. Exiting.")
            return

        # Step 2: 多源靶点收集
        self.raw_targets = self._step2_fetch_targets()
        if not self.raw_targets:
            logger.error("No targets collected. Exiting.")
            return

        # Step 3: 多源整合与Venn图
        self.combined_df = self._step3_integrate()

        # Step 4: 富集分析
        self._step4_enrichment()

        # Step 5: Chemprop排序
        self.ranked_targets = self._step5_ranking()

        # 最终输出
        self._save_final_results()
        logger.info("MIPTD completed successfully.")

    def _step1_smiles(self):
        """CAS转SMILES（带缓存）"""
        cache_file = self.cache_dir / f"{self.cas}_smiles.pkl"
        smiles = load_data(cache_file)
        if smiles is not None:
            logger.info(f"Loaded SMILES from cache: {smiles}")
            return smiles
        smiles = cas_to_smiles(self.cas, cache_dir=str(self.cache_dir))
        if smiles:
            save_data(smiles, cache_file)
        return smiles

    def _step2_fetch_targets(self):
        """多源靶点收集（带缓存）"""
        cache_file = self.cache_dir / f"{self.cas}_raw_targets.pkl"
        data = load_data(cache_file)
        if data is not None:
            logger.info("Loaded raw targets from cache")
            return data

        fetcher = TargetFetcher(cache_dir=str(self.cache_dir))
        results = fetcher.fetch_all(self.cas, self.smiles)
        save_data(results, cache_file)
        return results

    def _step3_integrate(self):
        """多源整合与可视化"""
        integrator = Integrator(output_dir=str(self.output_dir))
        df = integrator.combine_targets(self.raw_targets, min_sources=2)
        df.to_csv(self.output_dir / "combined_targets.csv", index=False)
        # 绘制Venn图
        integrator.draw_venn(self.raw_targets, output_file="venn.png")
        return df

    def _step4_enrichment(self):
        """富集分析"""
        if self.combined_df.empty:
            logger.warning("No combined targets for enrichment.")
            return
        gene_list = self.combined_df['Target'].tolist()
        analyzer = EnrichmentAnalyzer(output_dir=str(self.output_dir))
        go_df = analyzer.enrich_go(gene_list, outfile='GO_enrichment.csv')
        kegg_df = analyzer.enrich_kegg(gene_list, outfile='KEGG_enrichment.csv')
        # 疾病关键词过滤（示例）
        disease_keywords = ['cancer', 'inflammation']  # 用户可自定义
        filtered = analyzer.filter_by_disease(gene_list, disease_keywords, outfile='disease_filtered.txt')
        logger.info(f"Filtered {len(filtered)} targets by disease.")

    def _step5_ranking(self):
        """Chemprop排序"""
        if self.combined_df.empty:
            return []
        gene_list = self.combined_df['Target'].tolist()
        ranker = ChempropRanker(model_path=self.model_path, output_dir=str(self.output_dir))
        ranked = ranker.predict(self.smiles, gene_list)
        # 保存排序结果
        with open(self.output_dir / "ranked_targets.txt", 'w') as f:
            for t in ranked:
                f.write(t + '\n')
        return ranked

    def _save_final_results(self):
        """汇总最终结果"""
        final = {
            'cas': self.cas,
            'smiles': self.smiles,
            'total_candidates': len(self.combined_df) if self.combined_df is not None else 0,
            'ranked_targets': self.ranked_targets
        }
        save_data(final, self.output_dir / "final_results.json", use_json=True)

def main():
    parser = argparse.ArgumentParser(description='MIPTD: Multi-source Integrative Progressive Target Discovery Framework')
    parser.add_argument('cas', type=str, help='Compound CAS number')
    parser.add_argument('--model', type=str, default=None, help='Path to Chemprop model file')
    parser.add_argument('--output', type=str, default='results', help='Output directory')
    parser.add_argument('--cache', type=str, default='cache', help='Cache directory')
    args = parser.parse_args()

    pipeline = MIPTD(cas=args.cas, output_dir=args.output, cache_dir=args.cache, model_path=args.model)
    pipeline.run()

if __name__ == '__main__':
    main()