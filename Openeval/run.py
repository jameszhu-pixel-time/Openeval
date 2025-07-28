# Openeval/run.py
"""
============================================================
OpenEval 统一入口
------------------------------------------------------------
sub-commands:
  • infer     —— 仅跑推理 (wrap run_infer)
  • eval      —— 仅跑评测 (wrap run_eval)
  • pipeline  —— 推理 + 评测
============================================================
"""

from __future__ import annotations
import argparse, importlib, sys, shutil, json
from pathlib import Path
import asyncio
import logging

# ----------------------------------------------------------------------
# 直接复用子模块里的 main() / 函数
run_infer = importlib.import_module("Openeval.infer.run_infer")
run_eval  = importlib.import_module("Openeval.eval.run_eval")

# ----------------------------------------------------------------------
def add_infer_args(sp: argparse.ArgumentParser):
    """复用 run_infer 的 CLI 定义"""
    run_infer.build_cli(sp)          # 在 run_infer.py 里写一个 build_cli(parser)

def add_eval_args(sp: argparse.ArgumentParser):
    run_eval.build_cli(sp)           # 在 run_eval.py 里写一个 build_cli(parser)

# ----------------------------------------------------------------------
def cmd_infer(args):
    """只跑推理"""
    asyncio.run(run_infer.main(args))            # 直接把 Namespace 透传即可

def cmd_eval(args):
    """只跑评测"""
    run_eval.main(args)

def cmd_pipeline(args):
    """
    1) 调 run_infer，得到预测文件 (列表)
    2) 按同名规则调用 run_eval
    """
    # ---------- 步骤 1：推理 ----------
    logging.info("==> [Pipeline] Stage-1: Inference")
    preds = asyncio.run(run_infer.main(args, return_paths=True)) # 改写 run_infer.main 支持返回路径 list

    # ---------- 步骤 2：评测 ----------
    logging.info("==> [Pipeline] Stage-2: Evaluation")
    # 公共 eval 参数直接复用 CLI，但要改 eval_data / model_abbr
    for pred_fp in preds:
        eval_args = argparse.Namespace(**vars(args))  # 浅复制
        eval_args.eval_data = str(pred_fp)
        # 结果文件默认放 evaluations/xxx_eval.jsonl
        name = Path(pred_fp).stem.replace("_pred", "")
        eval_args.output = str(Path(args.eval_out_dir) /
                               f"{name}_eval.jsonl")
        run_eval.main(eval_args)

# ----------------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("OpenEval unified entry",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    sub = p.add_subparsers(dest="cmd", required=True,help="choose infer,eval or pipeline")

    # ---- infer
    sp_inf = sub.add_parser("infer", help="only run inference")
    add_infer_args(sp_inf)
    sp_inf.set_defaults(func=cmd_infer)

    # ---- eval
    sp_evl = sub.add_parser("eval", help="only run evaluation")
    add_eval_args(sp_evl)
    sp_evl.set_defaults(func=cmd_eval)

    # ---- pipeline
    sp_pipe = sub.add_parser("pipeline", help="inference + evaluation")
    add_infer_args(sp_pipe)              # 同时需要 infer & eval 参数
    add_eval_args(sp_pipe)
    sp_pipe.set_defaults(func=cmd_pipeline)

    return p

# ----------------------------------------------------------------------
def main():
    parser = build_arg_parser()
    args   = parser.parse_args()
    # 子命令分派
    args.func(args)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()