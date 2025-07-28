from typing import Dict, List, Tuple, Callable, Any
import logging
from ..evaluators import register
logger = logging.getLogger(__name__)
@register("math")
def objective_math(preds: List[List[str]], ref: str, k: int = 1) -> bool:
    """
    给定k下的结果
    机械判定（Math）示例：
    只要 preds 前 k 个里有一个与 ref 完全相同 ⇒ 通过
    top k 判断
    TODO: 可替换成更严格的数值同一性判断
    """
    flag=False
    if len(preds) <k:
        logger.warning("小于k的返回值出现预测 %d", len(preds))
    k=min(k,len(preds)) ##防报错
    preds = [p for p in preds[:k]]##    前k个的若干possible ans
    ref   = ref.strip()
    for pred_ans in preds:
        for pred_piece in pred_ans: 
            flag = ref in pred_piece ## in 就行
            if flag:
                return flag
    return flag
