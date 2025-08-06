from typing import Dict, List, Tuple, Callable, Any
import logging
from ..evaluators import register
import tempfile
import os
import subprocess
def execute_code(code: str, test_input: str, timeout: int = 2) -> str:
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python3", temp_path],
            input=test_input.encode("utf-8"),
            capture_output=True,
            timeout=timeout,
        )
        stdout = result.stdout.decode("utf-8").strip()
        return_code = result.returncode
        stderr = result.stderr.decode("utf-8").strip()

        if return_code != 0:
            # raise RuntimeError(f"Runtime Error:\n{stderr}")
            return "time out, no answer"
        return stdout

    finally:
        os.remove(temp_path)
        
@register("code")
def objective_code(preds: List[List[str,Dict]], ref: Any, k: int = 1) -> bool:
    """
    通过extra info 中的内容进行评测,
    answer可以装载对应i,o;
    """
    flag = False
    for pred in preds[:k]:
        code = pred[0]
        test_output = ref.get('output',ref).replace("\r\n","\n")
        test_input = ref.get('input',ref).replace("\r\n","\n")## if windows to unix
        result = execute_code(code,test_input)
        if result == test_output:
            flag = True
        
    return flag
        
   
        
        
        