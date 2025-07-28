from __future__ import annotations
from ..datasets.data_info import Datadic
from .postprocess.math.aime import extract_aime_line
import argparse
from ..infer.online_batch import start_vllm_server
import re
from ..datasets.data_info import Datadic,Promptdic
import  Openeval.utils.log       # 先初始化
import os
import logging
from pathlib import Path 
import glob
##先导入，注册才生效
import Openeval.eval.evaluators.math_judger,Openeval.eval.extracters.math_extracters,Openeval.eval.utils

"""
===========================================================
OpenEval ── 评测主入口（框架版）
===========================================================

✔ 单文件；执行示例：
    python -m Openeval.eval.eval_run \
        --eval_data predictions/aime24_pred.jsonl \
        --mode Objective \
        --output evaluations/aime24_eval.jsonl
-----------------------------------------------------------
"""


import argparse
import asyncio
import json
import re
from tqdm import tqdm

from pathlib import Path
import multiprocessing as mp, time, socket, sys
from pathlib import Path


from Openeval.datasets.data_info import Datadic

from .utils.data_loader import load_predictions
from .utils.coms import port_is_open, wait_port
from .utils.vllm_server import launch_vllm_bg
### ---- judger-----
from .evaluators.evaluate import evaluate_llm
from .evaluators.evaluate import evaluate_objective
logger = logging.getLogger(__name__)

def build_cli(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    评测 CLI 定义，供统一入口引用。
    """
    p = parser
    p.add_argument("--eval_data", "-e", default="predictions/aime25_pred.jsonl")
    p.add_argument("--eval_out_dir", default="./evaluations/aime25_eval.jsonl")
    p.add_argument("--mode", choices=["Objective", "LLM"], default="Objective")
    p.add_argument(
    "--k",                 # ：--k 1 8 16
    type=int,
    nargs="+",             #at least 1
    default=[1, 8],
    help="e.g. --k 1 8 16"
    )
    p.add_argument("-a","--model_abbr",default="qwen3")
    # debug
    p.add_argument("-ex","--extraction_path",default="./debugging/eval_extract/aime25.jsonl")

    # vLLM 服务相关（仅 LLM 模式用得到）
    p.add_argument("--judge_endpoint", default="http://10.200.250.35:7000/generate")
    p.add_argument("--judge_model", default="/DATA/disk1/wsh/DATA/disk1/wsh/MScache/models/Qwen/Qwen3-32B")
    p.add_argument("--judge_host", default="10.200.250.35")
    p.add_argument("--judge_port", type=int, default=7000)
    p.add_argument("--judge_tensor_parallel_size", "-jt", type=int, default=1)
    return p









# =========================================================
# 5️⃣  CLI 主入口
# =========================================================
def main(args: argparse.Namespace):
    # ---------- 识别数据集名 ----------
    
    # filename = os.path.basename(args.eval_data)
    # m = re.search(r"([^/]+?)_.*\.jsonl$", filename)
    # if not m:
    #     raise ValueError("eval_data 文件名需形如 xxx_pred.jsonl")
    # dataset_name = m.group(1)
    # if dataset_name not in Datadic:
    #     raise KeyError(f"{dataset_name} 不在 Datadic 中")

    # # ---------- 读取预测 ----------
    # proc=None
    # samples = load_predictions(args.eval_data)
    # logger.info('loading completes')
    matched_files = sorted(glob.glob(args.eval_data))
    proc=None
    if not matched_files:
        raise FileNotFoundError(f"No file matches: {args.eval_data}")
    
    for eval_file in matched_files:
        logger.info(f"Processing file: {eval_file}")

        filename = os.path.basename(eval_file)
        m = re.search(r"([^/]+?)_.*\.jsonl$", filename)
        if not m:
            raise ValueError("eval_data 文件名需形如 xxx_pred.jsonl")
        dataset_name = m.group(1)
        if dataset_name not in Datadic:
            raise KeyError(f"{dataset_name} 不在 Datadic 中")

        samples = load_predictions(eval_file)
        logger.info('loading completes')
        # ---------- 分支评测 ----------
        if args.mode == "Objective":
            result = evaluate_objective(
                samples,
                dataset_name,
                k=args.k,                 # 一次多个 k
                output=args.extraction_path
            )

        else:  # LLM 判定
            if not port_is_open(args.judge_host, args.judge_port):
                logger.warning("No active vLLM found — launching …")
                proc = launch_vllm_bg(args)
                if not wait_port(args.judge_host, args.judge_port, 30):
                    logger.error("vLLM failed to open port"); proc.terminate(); sys.exit(1)
                logger.info("vLLM is ready")
            else:
                logger.warning("Port already used, check the model running, the evaluation process will be based on that model")
            endpoint = args.judge_endpoint or f"http://{args.judge_host}:{args.judge_port}/generate"
            result = asyncio.run(
                evaluate_llm(
                    samples,
                    dataset_name,
                    endpoint,
                    k=args.k,
                    output=args.extraction_path
                )
            )

        ##补充model name
        result["model_name"]=args.model_abbr
        # ---------- 输出 ----------
        Path(os.path.join(args.eval_out_dir,dataset_name+"_"+args.model_abbr+'.jsonl')).parent.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(args.eval_out_dir,dataset_name+"_"+args.model_abbr+'.jsonl'), "w", encoding="utf-8") as fw:
            fw.write(json.dumps(result, ensure_ascii=False, indent=2))
        logger.info("✔ Eval finished")
    if proc is not None and proc.is_alive():
            logger.info("Shutting down vLLM subprocess…")
            proc.terminate()          
            proc.join(timeout=10)
            if proc.is_alive():
                logger.warning("vLLM did not exit in 10 s — killing")
                proc.kill()
            logger.info("vLLM subprocess exited")


# =========================================================
# 6️⃣  CLI 解析
# =========================================================
if __name__ == "__main__":
    parser=build_cli(argparse.ArgumentParser("OpenEval evaluation"))
    args=parser.parse_args()
    main(args)
