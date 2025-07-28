
from typing import Dict, List, Tuple, Callable, Any
import logging

logger = logging.getLogger(__name__)
OBJECTIVE_REGISTRY: Dict[str, Callable[[List[str], str, int], bool]] = {}



#注册函数
def register(domain:str):
    def decorator(func):
        if func.__name__ is not None:
            if domain in OBJECTIVE_REGISTRY:
                raise ValueError(f"Domain '{domain}' 已存在，指向 {EXTRACTOR_REGISTRY[domain].__name__}")
            OBJECTIVE_REGISTRY[domain]=func
        else :  raise ValueError(f"Empty function name")
        return func
    return decorator