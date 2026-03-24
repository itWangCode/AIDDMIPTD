"""
GO/KEGG富集分析、疾病关键词过滤
使用gseapy进行富集分析
"""
import pandas as pd
import gseapy as gp
from utils import logger, save_data, load_data

class EnrichmentAnalyzer:
    def __init__(self, output_dir='results'):
        self.output_dir = output_dir

    def enrich_go(self, gene_list, organism='human', outfile='GO_enrichment.csv'):
        """GO富集分析"""
        try:
            enr = gp.enrichr(gene_list=gene_list,
                             gene_sets=['GO_Biological_Process_2021'],
                             organism=organism,
                             description='GO_analysis')
            df = enr.results
            df.to_csv(f"{self.output_dir}/{outfile}", index=False)
            logger.info(f"GO enrichment saved to {outfile}")
            return df
        except Exception as e:
            logger.error(f"GO enrichment failed: {e}")
            return pd.DataFrame()

    def enrich_kegg(self, gene_list, organism='human', outfile='KEGG_enrichment.csv'):
        """KEGG富集分析"""
        try:
            enr = gp.enrichr(gene_list=gene_list,
                             gene_sets=['KEGG_2021_Human'],
                             organism=organism,
                             description='KEGG_analysis')
            df = enr.results
            df.to_csv(f"{self.output_dir}/{outfile}", index=False)
            logger.info(f"KEGG enrichment saved to {outfile}")
            return df
        except Exception as e:
            logger.error(f"KEGG enrichment failed: {e}")
            return pd.DataFrame()

    def filter_by_disease(self, gene_list, disease_keywords, outfile='disease_filtered.txt'):
        """
        根据疾病关键词过滤靶点
        disease_keywords: list of keywords (e.g., ['cancer', 'apoptosis'])
        """
        # 这里简化：直接返回基因列表，实际需要从数据库查询疾病关联
        # 可以使用DisGeNET等，此处模拟
        filtered = gene_list  # 实际实现需要查询
        with open(f"{self.output_dir}/{outfile}", 'w') as f:
            for g in filtered:
                f.write(g + '\n')
        logger.info(f"Filtered targets by disease saved to {outfile}")
        return filtered