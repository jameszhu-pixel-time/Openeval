import httpx
from tqdm import tqdm
from typing import Dict, List, Tuple, Callable, Any
import logging
from pathlib import Path 
import json
##--prompt



logger=logging.getLogger(__name__)

async def llm_judge(client: httpx.AsyncClient, endpoint: str,
                    pred: List[str], ref: str, prompt_tmpl: str,question:str) -> int:
    """
    LLM 判定器：
    给 LLM 一个统计/判分 prompt，让它输出 yes/no，然后解析
    TODO: 根据实际模板补充 sampling_params
    """
    payload = {
        "prompt": [prompt_tmpl["system"]+prompt_tmpl["user"].format(pred=pred, ref=ref,question=question)],
        "sampling_params": {"temperature": 0, "max_tokens": 8192,"stop":['<A>','<a>','<B>','<b>'],'include_stop_str_in_output':True}
    }
    resp = await client.post(endpoint, json=payload, timeout=None)
    resp.raise_for_status()
    texts  = resp.json()["text"]         # 不要再改名
    if isinstance(texts[0], list):
        texts = texts[0]                    # 取批中第一组候选

    for ans in texts:                       # ans 一定是 str
        ans_lc = ans.lower()
        if "<a>" in ans_lc:
            return 1                    # <A> / <a> 判正确
        if "<b>" in ans_lc:
            return 0                   # <B> / <b> 判错误
    return 2                       # 都没出现，视为空
    ## 优化逻辑
    
