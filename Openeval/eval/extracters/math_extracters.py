
from typing import Dict, List, Tuple, Callable, Any
from ..postprocess.math.aime import extract_math_line, extract_aime_line
from tqdm import tqdm
from ..extracters import register
# =========================================================
# 提取答案（以 Math 为示例，其余领域照此扩展）
# =========================================================
@register('math')
def extract_answer_math(sample: Dict,dataset_name: str) -> Tuple[List[List[str]], str]:
    """
    解析一条数学样本，返回：
        (候选答案列表   prediction_list,
         标准答案字符串 reference)

    - prediction_list 已 strip()，仍保持原字符格式
    - 允许该列表长度 < k，因为 vLLM 去重
    """
    preds: List[str] = sample["prediction"]  
    preds_post=[]#returns:[[ans1,2,3.. from response1],[ans1... from response2]]
    
    #### Post process to different datasets
    for response in preds:
        ps=extract_math_line(response)## returns:[ans1,2,3.. from response1]
        preds_post.append(ps)
    ref: str = str(sample.get("answer", "")).strip()
    return preds_post, ref

