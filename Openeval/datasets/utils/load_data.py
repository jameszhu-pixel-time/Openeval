##load_data from test_datasets:*.jsonl
##default_datasets_path:../test_data/*.jsonl
##TODO GENERALIZATION
import argparse
import glob
import json
import re
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from ..data_info import Datadic,Promptdic
from .data_format import data_format
from pathlib import Path
import os
import logging
import Openeval.utils.log
logger = logging.getLogger(__name__) 
##format
# from .datasets.data_info import Datadic
from ..prompts import rule_prompt_utils_code, rule_prompt_utils_gpqa, rule_prompt_utils_math
PROMPT_MODULES = [
    rule_prompt_utils_code, 
    rule_prompt_utils_gpqa,
    rule_prompt_utils_math,
]
#from ..prompts.difficulty import prompt_aime24,prompt_difficulty

def read_jsonl(file_path: str) -> List[Dict]:
    """读取单个 JSONL 文件，返回字典列表"""
    data = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data
#def fit_prompt_difficulty(domain:str): ##
    return prompt_difficulty

def pick_prompt_module(domain: str):
    """从 PROMPT_MODULES 中挑出名称含有 domain 的那个模块"""
    for m in PROMPT_MODULES:
        if domain in m.__name__:
            return m
    raise ValueError(f"No prompt module found for domain={domain}")

def load_data_with_prompt(file_path: str, output: str | bool = False) -> List[List[Dict]]:
    """
    读取 JSONL → 渲染 system/user prompt → 返回 [{'id','prompt','answer'?}, ...]
    若 output 为字符串目录 / Path，则把结果写入 <output>/<dataset>.jsonl
    """

    fp = Path(file_path)
    logger.info("开始处理 %s", fp)

    # ---------- 1) 读原始 JSONL ----------
    try:
        records = [json.loads(l) for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()]
    except json.JSONDecodeError:
        logger.exception("JSON 解析失败: %s", fp)
        raise

    # ---------- 2) 数据集名 & domain ----------
    name = fp.stem                              # e.g. "aime24"
    if name not in Datadic:
        raise KeyError(f"{name} 不在 Datadic 定义里")
    domain = Datadic[name]["domain"]

    # ---------- 3) 取 prompt 模块 ----------###
    prompt_mod = pick_prompt_module(domain) ##修改
    
    tpl_dict   = prompt_mod.system_prompt_temp   # 已确认是 {"system": "...", "user": "..."}
    # out_list=[]
    # for idx,tpl_dict in enumerate(tpl_dict_list):
    #     # ---------- 4) LangChain 模板 ----------
    #     system_tpl = PromptTemplate.from_template(tpl_dict["system"])
    #     user_tpl   = PromptTemplate.from_template(tpl_dict["user"])
    #     needed_vars = set(user_tpl.input_variables)

    #     # ---------- 5) 预处理数据 ----------
    #     records_fmt = data_format(name, records)

    #     # ---------- 6) 渲染 ---------------------
    #     out: List[Dict] = []
    #     for rec in records_fmt:
    #         try:
    #             user_vars   = {k: v for k, v in rec.items() if k in needed_vars}
    #             prompt_text = system_tpl.format() + "\n\n" + user_tpl.format(**user_vars)
    #             item = {"prompt_id":idx,"prompt_template":tpl_dict,"id": rec.get("id"), "prompt": prompt_text}
    #             if "answer" in rec:
    #                 item["answer"] = rec["answer"]
    #             out.append(item)
    #         except Exception:
    #             logger.exception("渲染记录失败 id=%s", rec.get("id"))
    #             raise

    #     logger.info("完成 %s：共渲染 %d 条 prompt", name+f'_promptid_{idx}', len(out))
    # ---------- 4) LangChain 模板 ----------
    system_tpl = PromptTemplate.from_template(tpl_dict["system"])
    user_tpl   = PromptTemplate.from_template(tpl_dict["user"])
    needed_vars = set(user_tpl.input_variables)

    # ---------- 5) 预处理数据 ----------
    records_fmt = data_format(name, records)

    # ---------- 6) 渲染 ---------------------
    out: List[Dict] = []
    for rec in records_fmt:
        try:
            user_vars   = {k: v for k, v in rec.items() if k in needed_vars}##填充
            prompt_text = system_tpl.format() + "\n\n" + user_tpl.format(**user_vars)
            item = {"prompt_template":tpl_dict,"id": rec.get("id"), "prompt": prompt_text}
            if "answer" in rec:
                item["answer"] = rec["answer"]
            if "extra_info" in rec:
                item["extra_info"] = rec["extra_info"]##rec_["extra_info"][key]=v
            out.append(item)
        except Exception:
            logger.exception("渲染记录失败 id=%s", rec.get("id"))
            raise

    logger.info("完成 %s：共渲染 %d 条 prompt", name, len(out))

        # ---------- 7) 可选写文件 ---------------
    if output:
        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_fp = out_dir / f"{name}.jsonl"

        with out_fp.open("w", encoding="utf-8") as wf:
            for obj in out:
                wf.write(json.dumps(obj, ensure_ascii=False) + "\n")

        logger.info("结果已写入 %s", out_fp)
    

    return out

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load data and render prompts")
    parser.add_argument(
        "-p", "--path",
        default="Openeval/datasets/unregistered_datasets/codeforces.jsonl",
        help="Glob 模式，匹配 JSONL 文件"
    )
    parser.add_argument(
        "-o", "--output",
        default='Openeval/datasets/formatted_data/codeforces.jsonl',
        help="输出后处理prompt格式文件"
    )
    args = parser.parse_args()

    files = glob.glob(args.path)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    for f in glob.glob(args.path):
        lst = load_data_with_prompt(f,output=args.output)
        print(f"{f} -> {len(lst)} 条 prompt，示例首行：{lst[0]['prompt'].splitlines()[0]}")

        # name = Path(f).stem
        # out_fp = out_dir / f"{name}.jsonl"
        # with out_fp.open("w", encoding="utf-8") as wf:
        #     for obj in lst:
        #         wf.write(json.dumps(obj, ensure_ascii=False) + "\n")