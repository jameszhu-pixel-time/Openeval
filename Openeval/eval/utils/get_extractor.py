from typing import Dict, List, Tuple, Callable, Any
from ..extracters import EXTRACTOR_REGISTRY
from Openeval.datasets.data_info import Datadic
from ..extracters import math_extracters
def get_extractor(dataset_name: str) -> Callable[[Dict,str], Tuple[List[str], str]]:
    """依据数据集domain返回对应 extractor(对应prompt注意)"""
    domain = Datadic[dataset_name]["domain"]
    print(Datadic)
    if domain not in EXTRACTOR_REGISTRY:
        raise NotImplementedError(f"domain={domain} 没有 extractor 实现")
    return EXTRACTOR_REGISTRY[domain]
