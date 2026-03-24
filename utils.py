"""
通用工具函数：CAS转SMILES、文件IO、日志等
"""
import os
import json
import pickle
import logging
import requests
from tqdm import tqdm
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cas_to_smiles(cas, cache_dir='cache'):
    """
    将CAS号转换为SMILES字符串
    优先使用本地缓存，否则调用PubChem API
    """
    cache_file = Path(cache_dir) / f"{cas}_smiles.pkl"
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/property/CanonicalSMILES/JSON"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        smiles = data['PropertyTable']['Properties'][0]['CanonicalSMILES']
        # 缓存结果
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, 'wb') as f:
            pickle.dump(smiles, f)
        logger.info(f"CAS {cas} -> SMILES: {smiles}")
        return smiles
    except Exception as e:
        logger.error(f"Failed to convert CAS {cas}: {e}")
        return None

def save_data(data, filename, use_json=False):
    """保存数据到文件（pickle或json）"""
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    if use_json:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

def load_data(filename, use_json=False):
    """从文件加载数据"""
    if not os.path.exists(filename):
        return None
    if use_json:
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        with open(filename, 'rb') as f:
            return pickle.load(f)