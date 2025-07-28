from typing import List,Dict
import json
def load_predictions(file_path: str) -> List[Dict]:
    """
    读取 *.jsonl 推理结果
    ----------------------------------------------
    返回 List[dict]，每行原样解析，不做任何过滤
    """
    samples: List[Dict] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))
    return samples
