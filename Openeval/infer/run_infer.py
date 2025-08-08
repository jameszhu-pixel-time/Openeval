#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
High-throughput inference runner for vLLM HTTP server.
"""

import argparse, asyncio, json, logging, os, sys
from pathlib import Path
from typing import Dict, List,Union
import subprocess

import httpx
from tqdm.asyncio import tqdm  # pip install tqdm
from Openeval.infer.online_batch import start_vllm_server
from Openeval.datasets.utils.load_data import read_jsonl
from Openeval.datasets.utils.load_data import load_data_with_prompt  # ← 根据你的包路径调整
from Openeval.datasets.utils.load_data import load_data_with_ds_prompt
# Openeval/infer/run_infer.py  （放在文件最顶部 import 之后）
from Openeval.infer.start_service import launch_vllm_server
from Openeval.infer.mp import generate_mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging 
import openai as op
logger = logging.getLogger(__name__) 
#-----------------------------------------------------------------------
import multiprocessing as mp, socket, time, logging

def port_open(host, port) -> bool:
    with socket.socket() as s:
        return s.connect_ex((host, port)) == 0

def wait_port(host, port, timeout=30):
    for _ in range(timeout):
        if port_open(host, port):
            return True
        time.sleep(1)
    return False

def launch_vllm_proc(model, host, port, tp):
    ctx = mp.get_context("spawn")          # 避免 fork CUDA 问题
    p   = ctx.Process(target=start_vllm_server,
                      args=(model,),
                      kwargs=dict( port=port,
                                  tensor_parallel_size=tp
                                 ),
                ) 
    p.start()
    return p

import psutil, signal, os, time

def _kill_proc_tree(pid: int, sig=signal.SIGTERM, timeout=5):
    """杀掉 pid 及其所有子进程；超时后改用 SIGKILL"""
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for c in children:           # 先温柔
        c.send_signal(sig)
    parent.send_signal(sig)

    gone, alive = psutil.wait_procs(children + [parent], timeout=timeout)
    if alive:                    # 还活着就强杀
        for p in alive:
            p.kill()
        psutil.wait_procs(alive, timeout=2)

# ----------------------------------------------------------------------
async def infer_batch(
    prompts: Union[List[str],List[Dict]],
    endpoint: str,
    sampling_params: Dict,
    client: httpx.AsyncClient,
    retry: int = 3, ## debugging
) -> List[str]:
    """Post a batch & return list[str] predictions with simple retry."""
    openai = endpoint.split("/")[-1]=='generate_openai'
    try:
        if not openai:
            payload = {"prompt": prompts, "sampling_params": sampling_params}
            for attempt in range(retry):
                try:
                    resp = await client.post(endpoint, json=payload, timeout=None)
                    resp.raise_for_status()
                    return resp.json()["text"]
                except Exception as e:
                    if attempt == retry - 1:
                        raise
                    await asyncio.sleep(2.0)
                    logging.getLogger(__name__).warning("Retry %s/%s: %s", attempt + 1, retry, e)
    except httpx.HTTPStatusError as e:
        if e.response.status_code in {400, 422, 500}:      # 都打印一下
            logging.error("SERVER-%s detail: %s",
                        e.response.status_code, e.response.text)

# ----------------------------------------------------------------------
async def run_single_file(
    src_path: Path,
    endpoint: str,
    sampling_params: Dict,
    batch_size: int,
    output_dir: Path,
    model: str,
    args ,
    code : bool = True,
    processed : bool = False,
) -> str:
    logger = logging.getLogger(__name__)
    name = src_path.stem
    dst_path = output_dir / f"{name}_{model}_pred.jsonl"
    logger.info(f"save to {dst_path} ")
    output_dir.mkdir(parents=True, exist_ok=True)

    if processed==True:
        data : List[Dict] = read_jsonl(str(src_path)) ##直接读
    else:
        data: List[Dict] = load_data_with_prompt(str(src_path),False)  # List[dict]做预处理
        logger.info("load_data with prompt")
        
    openai = endpoint.split("/")[-1]=='generate_openai'
    if not openai:
        async with httpx.AsyncClient(timeout=None) as client:
            with dst_path.open("w", encoding="utf-8") as wf:
                pbar = tqdm(total=len(data), desc=f"Infer {name}", unit="q")
                for i in range(0, len(data), batch_size):
                    chunk = data[i : i + batch_size]
                    prompts = [item["prompt"] for item in chunk]
                    preds = await infer_batch(prompts, endpoint, sampling_params, client)
                    logger.info('______DEBUGGING______')
                    logger.info(f"preds:{len(preds)}")
                    logger.info(f"{len(preds[0])}")
                    logger.info(f"chunk:{len(chunk)}")
                    logger.info(f"chunk id{[i['id'] for i in chunk]}")
                    # 写结果
                    for item, pred in zip(chunk, preds):
                    # pred: 可能是 str 也可能是 list[str]
                        if isinstance(pred, str):
                            pred_list = [pred.strip()]               # n == 1 → 包成 list
                        else:
                            pred_list = [p.strip() for p in pred]    # n >= 1 → 保留全部候选

                        out = {
                            "id": item["id"],
                            "prompt": item["prompt"],
                            "prediction": pred_list,   # 统一写 list
                        }
                        if "answer" in item:
                            out["answer"] = item["answer"]
                        if code: ##代替attr判定逻辑
                            for key,v in item.items():
                                if key in ["extra_info"]:
                                    out[key]=item[key]
                        wf.write(json.dumps(out, ensure_ascii=False) + "\n")
                    pbar.update(len(chunk))
                pbar.close()
            logger.info(" %s done, saved to %s", name, dst_path)
            return dst_path
    else :
        logging.getLogger(__name__).info("Debug mode with openai completion")
        openai_api_key = "EMPTY"
        openai_api_base = endpoint.replace('generate_openai','v1')
        client = op.OpenAI(
            api_key=openai_api_key,
            base_url=openai_api_base,
        )
        logging.info(f"saving to {dst_path}")
        with dst_path.open("w", encoding="utf-8") as wf:
            pbar = tqdm(total=len(data), desc=f"Infer {name}", unit="q")
            for i in range(0, len(data), batch_size):
                chunk = data[i : i + batch_size]
                prompts = [item["prompt"] for item in chunk]
                with ProcessPoolExecutor(max_workers=batch_size) as executor:
                    futures = [
                        executor.submit(generate_mp, prompt, args.model, sampling_params, args.host, args.port)
                        for prompt in prompts
                    ]
                    preds = [f.result() for f in futures]
                logger.info('______DEBUGGING______')
                logger.info(f"preds:{len(preds)}")
                logger.info(f"{len(preds[0])}")
                logger.info(f"chunk:{len(chunk)}")
                logger.info(f"chunk id{[i['id'] for i in chunk]}")
                for item, pred in zip(chunk, preds):
                    # pred: 可能是 str 也可能是 list[str]
                        if isinstance(pred, str):
                            pred_list = [pred.strip()]               # n == 1 → 包成 list
                        else:
                            pred_list = [p.strip() for p in pred]    # n >= 1 → 保留全部候选

                        out = {
                            "id": item["id"],
                            "prompt": item["prompt"],
                            "prediction": pred_list,   # 统一写 list
                        }
                        if "answer" in item:
                            out["answer"] = item["answer"]
                        if code: ##代替attr判定逻辑
                            for key,v in item.items():
                                if key in ["extra_info"]:
                                    out[key]=item[key]
                        wf.write(json.dumps(out, ensure_ascii=False) + "\n")
                pbar.update(len(chunk))
            pbar.close()
            logger.info(" %s done, saved to %s", name, dst_path)
            
        return dst_path
           
# ----------------------------------------------------------------------
async def main(args: argparse.Namespace,return_paths:bool = True)->List:
    sampling_params: Dict = json.loads(args.sampling_params)
    if args.difficulty_selection == True: ##改主函数，统一load 后返回file_paths再分发
        _,files = load_data_with_ds_prompt(args.data,output=True)
    else:
        files = [Path(p) for pat in args.data.split() for p in Path().glob(pat)]
        logger.info(f"prompts loaded (ds) {files}")
    if not files:
        logger.error("No file matched %s", args.data)
        sys.exit(1)
    ## 协程
    proc=None ##自身开启的进程
    output_files=[]
    ##新接口引入：
    openai = args.endpoint.split("/")[-1]=='generate_openai'
    try:
        if not port_open(args.host, args.port):
            
            if not openai:## vllm 
                logger.info("No active vLLM found — launching vllm")
                proc = launch_vllm_proc(args.model, args.host,
                                        args.port, args.tensor_parallel_size)
            else:
                logger.info("No active vLLM found — launching Openai-based vllm")
                proc = launch_vllm_server(args.model, args.host,
                                        args.port, args.tensor_parallel_size)## 不传maxtoken 防止爆

            if not wait_port(args.host, args.port, 180):
                logger.error("vLLM failed to open port in 180s")
                proc.terminate(); sys.exit(1)
            logger.info("vLLM is ready")
        ## 协程
        else:
            logger.info("Reuse existing vLLM on %s:%d", args.host, args.port)
        for fp in files:
            dst = await run_single_file(
                        fp,
                        endpoint=args.endpoint,
                        sampling_params=sampling_params,
                        batch_size=args.batch_size,
                        output_dir=Path(args.prediction_dir),
                        model=args.m_abbr,
                        processed=args.processed or args.difficulty_selection,
                        args=args
            )
            if return_paths:
                output_files.append(dst)
            
    finally:
        if proc is not None and psutil.pid_exists(proc.pid):
            logger.info("Shutting down vLLM subprocess group …")
            _kill_proc_tree(proc.pid)

            if isinstance(proc, subprocess.Popen):
                if proc.poll() is None:
                    logger.warning("vLLM did not exit in 10 s — killing")
                    proc.kill()
            else :
                if proc.is_alive():
                    logger.warning("vLLM multiprocessing.Process did not exit in 10 s — killing")
                    proc.terminate()
            logger.info("vLLM subprocess exited")
    return output_files

# ----------------------------------------------------------------------
def build_cli(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    给统一入口的 sub-parser 添加推理参数。
    直接复用这里的默认值，保持与单独运行 run_infer.py 一致。
    """
    defaultsp='{"temperature":0.9,"top_p":0.85,"max_tokens":4096,"n":12,"presence_penalty": 1,"repetition_penalty":1.2}'
    parser.add_argument("-d","--data", default='./Openeval/datasets/test_data/aime24.jsonl', help="Raw JSONL or glob (e.g. data/*.jsonl)")
    parser.add_argument("--endpoint", default="http://10.200.250.35:7005/generate")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--prediction_dir", default="predictions")
    parser.add_argument("--sampling_params", default=defaultsp)
    parser.add_argument("--loglevel", default="INFO")
    parser.add_argument("--model", type=str, help="Path to the model",default="/DATA/disk1/wsh/DATA/disk1/wsh/MScache/models/Qwen/Qwen3-8B")
    parser.add_argument("--host", type=str, default="10.200.250.35", help="Host IP")
    parser.add_argument("--port", type=int, default=7005, help="Port number")
    parser.add_argument("-t","--tensor_parallel_size", type=int, default=1, help="Tensor parallel size")
    parser.add_argument("--m_abbr", type=str, default='qwen2.5_7b', help="abbr model_name")
    parser.add_argument("--processed", action="store_true", help="read from processed file")
    parser.add_argument("--difficulty_selection", action="store_true", help="perform difficulty selection")
    return parser

if __name__ == "__main__":
    parser=build_cli(argparse.ArgumentParser("High-throughput vLLM inference"))
    args=parser.parse_args()
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("Interrupted ⌃C")