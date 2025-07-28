from typing import Dict, List, Tuple, Callable, Any
from ..postprocess.math.aime import extract_math_line, extract_aime_line
from tqdm import tqdm
from ..extracters import register
import re

@register('code')
def extract_code_blocks(prediction: str) -> list[str]:
    """
    提取 prediction 中所有 <code>...</code> 包裹的代码块。
    优先剥离 ```python``` 包裹。
    """
    matches = re.findall(r"<code>(.*?)</code>", prediction, re.DOTALL | re.IGNORECASE)
    code_blocks = []

    for block in matches:
        # 去掉 markdown code block 包裹
        code = block.strip()
        code = re.sub(r"^```python\s*", "", code, flags=re.IGNORECASE)
        code = re.sub(r"```$", "", code)
        code_blocks.append(code.strip())

    return code_blocks