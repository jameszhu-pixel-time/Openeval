##Recall the system prompt template:
# First write out each step in detail under "Thinking process:".
# Then, on the line starting with "Final answer:", provide the result.
from typing import List,Dict
import json
    
import re
from typing import List


import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import List, Set, Union

# ------------------------------------------------------------
# 帮助函数：把 “分数 / 小数 / 整数” → 统一转字符串，转不了就原样留着
# ------------------------------------------------------------
def _num_to_str(s: str) -> str:
    s = s.strip()
    try:
        if "/" in s and "." not in s:          # 分数形式 a/b
            return str(float(Fraction(s)))
        # 小数或整数
        return str(float(Decimal(s)))
    except (InvalidOperation, ZeroDivisionError, ValueError):
        return s                               # 不是纯数字就保持原样


# ------------------------------------------------------------
def extract_aime_line(f_line: str | List[str], thres: int = 4) -> List[str]:
    """
    提取 AIME 预测文本中的可能答案列表（去重，最多 thres 个）

    支持捕获格式：
        1. \\boxed{value}
        2. final answer: value   / Final answer：value
        3. 兜底：文本里最后一个数字（纯数字或分数）
    """
    # 允许既传 str 也传 token list
    text = " ".join(f_line) if isinstance(f_line, list) else str(f_line)

    answers: List[str] = []
    seen: Set[str]    = set()

    def _add(val: str):
        if len(answers) < thres:
            val = val.strip()
            if val and val not in seen:
                answers.append(val)
                seen.add(val)

    # ① \boxed{...}
    for m in re.finditer(r"\\boxed\{([^}]+)\}", text, flags=re.I):
        _add(m.group(1))

    # ② Final answer: ...
    if len(answers) < thres:
        for m in re.finditer(
            r"[Ff]inal\s+answer\s*[:：]?\s*([0-9A-Za-z\./+\-*^()]+)",
            text,
            flags=re.I,
        ):
            _add(m.group(1))

    # ③ 兜底：最后一个数字 / 分数
    if not answers:
        nums = re.findall(r"-?\d+(?:/\d+)?(?:\.\d+)?", text)
        if nums:
            _add(nums[-1])

    # 安全数值规范化（分数 -> 小数字符串；失败保持原样）
    answers = [_num_to_str(ans) for ans in answers]

    return answers

#--------
import re
from typing import List, Set, Union

# 更鲁棒的正则表达式
_PAT_BOX = re.compile(r"(?:\\)?boxed\s*[\{\(]?\s*([^\}\)\n]+?)\s*[\}\)]?", flags=re.I)
_PAT_FINAL = re.compile(
    r"[Ff]inal\s+answer\s*[:：]?\s*(?:\\boxed\s*[\{\(]?)?([^\}\)\n\$]+)",  # 不提 $ \n ) }
    flags=re.I
)
_PAT_NUM = re.compile(r"-?\d+(?:/\d+)?(?:\.\d+)?")

def _normalize(ans: str) -> str:
    ans = ans.strip()
    ans = ans.replace(",", "")
    ans = re.sub(r"\$|\\|\\boxed|boxed", "", ans)
    ans = re.sub(r"[\(\)\{\}=：:]*$", "", ans)
    ans = re.sub(r"[^\d\./\-]+", "", ans)
    return ans.strip()

def extract_math_line(f_line: Union[str, List[str]], thres: int = 10) -> List[str]:
    text = " ".join(f_line) if isinstance(f_line, list) else str(f_line)

    answers: List[str] = []
    seen: Set[str] = set()

    def _add(val: str):
        val = _normalize(val)
        if val and val not in seen and len(answers) < thres:
            answers.append(val)
            seen.add(val)

    for i, m in enumerate(_PAT_BOX.finditer(text)):
        _add(m.group(1))
        if i >= thres // 2:
            break

    for i, m in enumerate(_PAT_FINAL.finditer(text)):
        _add(m.group(1))
        if i >= thres // 2:
            break

    if not answers:
        nums = _PAT_NUM.findall(text)
        if nums:
            _add(nums[-1])

    return answers