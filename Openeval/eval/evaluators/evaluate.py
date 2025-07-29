from ..utils.get_extractor import get_extractor
from ...datasets.data_info import Datadic
from typing import Dict, List, Tuple, Callable, Any
from ..evaluators.llm_judger import llm_judge
import logging
from pathlib import Path
import json
import httpx
from tqdm import tqdm
from ...datasets.prompts.llm_math_jd import grader_prompt_temp
logger = logging.getLogger(__name__)
from ..evaluators import OBJECTIVE_REGISTRY
import os
#========================================== ===============
#  主评测逻辑 1. 客观评测
# =========================================================

def evaluate_objective(details: List[Dict], dataset_name: str,
                       output: str, file_name: str ,k: List[int]= [1]) -> Dict[str, Any]:
    extractor = get_extractor(dataset_name)
    judge     = OBJECTIVE_REGISTRY[Datadic[dataset_name]["domain"]]

    
    result={}
    result[file_name]=[]
    if output :
        ex_record={f"pass@{k_}":[] for k_ in k}
    for k_ in k:
        idx=[]
        total, correct = 0, 0
        for sample in tqdm(details,desc=f'start evaluating {file_name}'):
            preds, ref = extractor(sample,dataset_name) ##单个prompt下的所有回答，返回的是[回答1，回答2，回答3...],ans
            flag=False
            if judge(preds, ref, k_):
                correct += 1
                flag=True
            total += 1
            idx.append(flag)
            if output:
                ex_record[f"pass@{k_}"].append({'preds':preds,'ref':ref})
        result[file_name].append({"acc@%d" % k_: correct / total if total else 0.0,
        "total": total, "correct": correct}) ##统计 str：Dict
        result[f"pass@{k_} detailed id"]=idx
            
    if output :  
        Path(os.path.join(output,file_name)).parent.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(output,file_name)+'.jsonl', "w", encoding="utf-8") as fw:
            fw.write(json.dumps(ex_record, ensure_ascii=False, indent=2))
        logger.info("output extraction finished:", result)
        logger.info(f"debugging mode: output extraction file to{os.path.join(output,file_name)} ")
    return result
#2.LLM 评测:

async def evaluate_llm(details: List[Dict], dataset_name: str,
                       endpoint: str,output: str,file_name: str ,k: List[int]= [1],) -> Dict[str, Any]:
    extractor = get_extractor(dataset_name)
    prompt_tmpl = grader_prompt_temp ### grader prompt
    logger.info("start LLM evaluation!")
    if output :
        ex_record={f"pass@{k_}":[] for k_ in k}
    async with httpx.AsyncClient(timeout=None) as client:
        for k_ in k:
            logger.info(f"Evaluating pass@{k_} ")
            total, correct = 0, 0   
            result={}
            result[file_name]=[]
            for idx,sample in tqdm(enumerate(details), desc="LLM judging"):
                preds, ref = extractor(sample,dataset_name)
                logger.info(f"Remaining {len(details)-idx}")
                # 只让 LLM 判前 k_ 个候选,中的每一个可能答案
                checks = [await llm_judge(client, endpoint, p, ref, prompt_tmpl,sample['prompt'])
                         for p in preds[:k_]]
                ok = any([check==1 for check in checks])
                
                if ok:
                    correct += 1
                total += 1
                if output:
                    wrong= checks.count(0)
                    empty= checks.count(2)
                    A=checks.count(1)
                    ex_record[f"pass@{k_}"].append({'preds':preds,'ref':ref,'correct':A,'wrong':wrong,'empty':empty})
                    logger.info(f"ex_recording:{ex_record}")
            result[file_name].append({"acc@%d" % k_: correct / total if total else 0.0,"total": total, "correct": correct}) ##统计 str：Dict
    if output :  
        Path(os.path.join(output,file_name)).parent.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(output,file_name), "w", encoding="utf-8") as fw:
            fw.write(json.dumps(ex_record, ensure_ascii=False, indent=2))
        logger.info("output extraction finished:", result)
        logger.info(f"debugging mode: output extraction file to{os.path.join(output,file_name)} ")
    return result





