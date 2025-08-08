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

#---copy from verl
def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[: len(left)] == left
        return s[len(left) :]

    left = "\\boxed{"

    # assert s[: len(left)] == left ,s
    # assert s[-1] == "}" ,s
    if s[: len(left)] != left:
        print(f"invalid last boxed string: {s[:min(10,len(s))]}")
        return None
    if s[-1] != "}":
        print(f"invalid last boxed string: {s[:min(10,len(s))]}")
        return None
    return s[len(left) : -1]

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break #匹配的braces 个数
        i += 1

    retval = None if right_brace_idx is None else string[idx : right_brace_idx + 1]

    return retval


def fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:  # noqa: E722
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


def fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:  # noqa: E722
        return string


def remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string


def fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0]
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string


def strip_string(string):
    # linebreaks
    string = string.replace("\n", "")

    # remove inverse spaces
    string = string.replace("\\!", "")

    # replace \\ with \
    string = string.replace("\\\\", "\\")

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")

    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")

    # remove units (on the right)
    string = remove_right_units(string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")  # noqa: W605

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2 and len(string.split("=")[0]) <= 2:
        string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1).
    # Also does a/b --> \\frac{a}{b}
    string = fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = fix_a_slash_b(string)

    return string

def extract_boxed_line(f_line: Union[str, List[str]])-> List[str]:
    text = " ".join(f_line) if isinstance(f_line, list) else str(f_line)
    result = "No answer"
    string_in_last_boxed = last_boxed_only_string(text)
    if string_in_last_boxed is not None:
        result = remove_boxed(string_in_last_boxed)
    return [result]