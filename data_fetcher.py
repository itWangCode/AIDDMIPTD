"""
多源靶点数据采集
支持断点续传、自动重试、异常恢复
"""
import time
import requests
from bs4 import BeautifulSoup
from utils import logger, save_data, load_data

class TargetFetcher:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MIPTD/1.0'})

    def _request_with_retry(self, url, retries=3, delay=2):
        """带重试的GET请求"""
        for i in range(retries):
            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                return resp
            except Exception as e:
                logger.warning(f"Request failed ({i+1}/{retries}): {e}")
                time.sleep(delay * (i+1))
        return None

    def fetch_from_pubchem(self, cas):
        """从PubChem获取靶点（通过BioAssay关联）"""
        cache_file = f"{self.cache_dir}/pubchem_{cas}.pkl"
        data = load_data(cache_file)
        if data is not None:
            logger.info(f"Loaded PubChem data for {cas} from cache")
            return data

        # 先获取CID
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/cids/JSON"
        resp = self._request_with_retry(cid_url)
        if not resp:
            return []
        cid = resp.json()['IdentifierList']['CID'][0]

        # 获取关联的靶点（简化：取生物活性关联的基因）
        targets = []
        bio_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/assays/JSON"
        resp = self._request_with_retry(bio_url)
        if resp:
            assays = resp.json().get('Assays', [])
            for assay in assays:
                # 这里需要进一步解析，简化模拟
                targets.append(assay.get('Target', 'Unknown'))
        # 去重
        targets = list(set(targets))
        save_data(targets, cache_file)
        logger.info(f"PubChem: found {len(targets)} targets")
        return targets

    def fetch_from_swiss(self, smiles):
        """SwissTargetPrediction API"""
        cache_file = f"{self.cache_dir}/swiss_{smiles}.pkl"
        data = load_data(cache_file)
        if data is not None:
            logger.info(f"Loaded SwissTargetPrediction data from cache")
            return data

        url = "http://www.swisstargetprediction.ch/api/v1/predict"
        payload = {'smiles': smiles}
        try:
            resp = self.session.post(url, data=payload, timeout=30)
            resp.raise_for_status()
            results = resp.json()
            targets = [item['target'] for item in results.get('targets', [])]
            save_data(targets, cache_file)
            logger.info(f"SwissTargetPrediction: found {len(targets)} targets")
            return targets
        except Exception as e:
            logger.error(f"SwissTargetPrediction failed: {e}")
            return []

    def fetch_from_sea(self, smiles):
        """SEA (Similarity Ensemble Approach) API"""
        cache_file = f"{self.cache_dir}/sea_{smiles}.pkl"
        data = load_data(cache_file)
        if data is not None:
            return data

        # SEA服务需要注册，此处模拟返回空
        logger.warning("SEA API not implemented (requires registration). Returning empty.")
        targets = []
        save_data(targets, cache_file)
        return targets

    def fetch_from_chembl(self, smiles):
        """ChEMBL API"""
        cache_file = f"{self.cache_dir}/chembl_{smiles}.pkl"
        data = load_data(cache_file)
        if data is not None:
            return data

        # 使用ChEMBL web服务搜索相似分子并获取靶点
        # 简化：直接返回空
        logger.warning("ChEMBL API not fully implemented. Returning empty.")
        targets = []
        save_data(targets, cache_file)
        return targets

    def fetch_from_ppb2(self, cas):
        """PPB2数据库（示例）"""
        cache_file = f"{self.cache_dir}/ppb2_{cas}.pkl"
        data = load_data(cache_file)
        if data is not None:
            return data

        # 模拟爬取
        url = f"https://www.example.com/ppb2?cas={cas}"
        resp = self._request_with_retry(url)
        if not resp:
            return []
        # 解析HTML，这里简化
        soup = BeautifulSoup(resp.text, 'html.parser')
        targets = [tag.text for tag in soup.find_all('div', class_='target')]
        save_data(targets, cache_file)
        logger.info(f"PPB2: found {len(targets)} targets")
        return targets

    def fetch_all(self, cas, smiles):
        """整合所有来源的靶点"""
        results = {}
        # PubChem
        results['PubChem'] = self.fetch_from_pubchem(cas)
        # Swiss
        results['SwissTargetPrediction'] = self.fetch_from_swiss(smiles)
        # SEA
        results['SEA'] = self.fetch_from_sea(smiles)
        # ChEMBL
        results['ChEMBL'] = self.fetch_from_chembl(smiles)
        # PPB2
        results['PPB2'] = self.fetch_from_ppb2(cas)
        return results