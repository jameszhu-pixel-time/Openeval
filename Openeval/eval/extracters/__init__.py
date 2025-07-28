from typing import Dict, List, Tuple, Callable, Any
EXTRACTOR_REGISTRY: Dict[str, Callable[[Dict], Tuple[List[str], str]]] = {}

def register(domain:str):
    def decorator(func):
        if func.__name__ is not None:
            if domain in EXTRACTOR_REGISTRY:
                raise ValueError(f"Domain '{domain}' 已存在，指向 {EXTRACTOR_REGISTRY[domain].__name__}")
            EXTRACTOR_REGISTRY[domain]=func
        else :  raise ValueError(f"Empty function name")
        return func
    return decorator