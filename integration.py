"""
多源数据整合、交集比较、Venn图可视化
"""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from utils import logger, save_data, load_data

class Integrator:
    def __init__(self, output_dir='results'):
        self.output_dir = output_dir

    def combine_targets(self, source_dict, min_sources=2):
        """
        整合多源靶点，保留至少出现在min_sources个来源中的靶点
        返回整合后的DataFrame
        """
        all_targets = set()
        for src, targets in source_dict.items():
            all_targets.update(targets)

        target_sources = {}
        for target in all_targets:
            count = 0
            sources = []
            for src, targets in source_dict.items():
                if target in targets:
                    count += 1
                    sources.append(src)
            if count >= min_sources:
                target_sources[target] = {'count': count, 'sources': ','.join(sources)}

        df = pd.DataFrame.from_dict(target_sources, orient='index')
        df.index.name = 'Target'
        df.reset_index(inplace=True)
        df.columns = ['Target', 'SourceCount', 'Sources']
        df = df.sort_values('SourceCount', ascending=False)
        logger.info(f"Combined targets: {len(df)} (min_sources={min_sources})")
        return df

    def draw_venn(self, source_dict, output_file='venn.png'):
        """绘制Venn图（支持2-3个集合）"""
        sources = list(source_dict.keys())
        if len(sources) == 2:
            sets = [set(source_dict[sources[0]]), set(source_dict[sources[1]])]
            venn2(sets, set_labels=sources)
        elif len(sources) >= 3:
            # 只取前三个主要来源
            top3 = sources[:3]
            sets = [set(source_dict[top3[0]]), set(source_dict[top3[1]]), set(source_dict[top3[2]])]
            venn3(sets, set_labels=top3)
        else:
            logger.warning("Need at least 2 sources for Venn diagram")
            return
        plt.title('Target Overlap Across Sources')
        plt.savefig(f"{self.output_dir}/{output_file}")
        plt.close()
        logger.info(f"Venn diagram saved to {self.output_dir}/{output_file}")