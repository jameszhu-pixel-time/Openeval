from typing import Dict, List, Tuple, Callable, Any
from ..postprocess.math.aime import extract_math_line, extract_aime_line
from tqdm import tqdm
from ..extracters import register
import re

@register('code')
def extract_code_blocks(sample: Dict,dataset_name: str) -> Tuple[List[List[str|None]], Any]:
    """
    提取 prediction 中所有 <code>...</code> 包裹的代码块。
    优先剥离 ```python``` 包裹。
    注意，ref 是测试案例的答案，这里先
    """
    preds: List[str] = sample["prediction"] ## return n
    ref: str =str(sample.get("answer","")).strip()
    code_blocks_post = [] ## returns ["code1","code2"]
    for prediction in preds:
        matches = re.findall(r"<code>(.*?)</code>", prediction, re.DOTALL | re.IGNORECASE)
        if matches is None:
            return [None],ref
        block=matches[-1]
        # 去掉 markdown code block 包裹
        code = block.strip()
        code = re.sub(r"^```python\s*", "", code, flags=re.IGNORECASE)
        code = re.sub(r"```$", "", code)
        code_blocks_post.append([code.strip()])

    return code_blocks_post ,ref
