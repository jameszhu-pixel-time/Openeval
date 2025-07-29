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
import glob
import os
# ----------------------------------------------------------------------
# 直接复用子模块里的 main() / 函数
run_infer = importlib.import_module("Openeval.infer.run_infer")
run_eval  = importlib.import_module("Openeval.eval.run_eval")
OUTCOME = './outcome'
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
    """只跑评测,
        路径支持通配符
    """
    matched_files = sorted(glob.glob(args.eval_data))
    if not matched_files:
        raise FileNotFoundError(f"No file matches: {args.eval_data}")
    args.matched_files = matched_files
    run_eval.main(args)
    ##逻辑

def cmd_pipeline(args):
    """
    1) 调 run_infer，得到预测文件 (列表)
    2) 按同名规则调用 run_eval
    #TODO eval for difficulty selection
    """
    # ---------- 步骤 1：推理 ----------
    logging.info("==> [Pipeline] Stage-1: Inference")
    preds = asyncio.run(run_infer.main(args, return_paths=True)) # 改写 run_infer.main 支持返回路径 list
    ## 从paths 中一个个读取
    # ---------- 步骤 2：评测 ----------
    logging.info("==> [Pipeline] Stage-2: Evaluation")
    # 公共 eval 参数直接复用 CLI，但要改 eval_data / model_abbr
    for pred_fp in preds:
        logging.info(f"strat evaluating {pred_fp} ")
        eval_args = argparse.Namespace(**vars(args))  # 浅复制
        eval_args.eval_data = str(pred_fp)
        # 结果文件默认放 evaluations/xxx_eval.jsonl
        name = Path(pred_fp).stem.replace("_pred", "")
        eval_args.matched_files = [eval_args.eval_data] ## 循环在外面
        out_fp = run_eval.main(eval_args)
    if args.difficulty_selection:
        statistic = None  # 避免变量未定义
        for i, fp in enumerate(out_fp):
            with open(fp, mode='r') as f:
                data = json.load(f)
                try:
                    items = data["pass@1 detailed id"]
                except (KeyError, TypeError):
                    logging.warning(f"文件 {fp} 中没有 pass@1 detailed id 字段或格式错误")
                    continue

                length = len(items)
                if i == 0:
                    statistic = {idx: 0 for idx in range(length)}

                for j, item in enumerate(items):
                    if item == 'true':
                        statistic[j] += 1

        if statistic is not None:
           
            out = os.path.join(OUTCOME, args.model_abbr + '.jsonl')
            Path(OUTCOME).mkdir(parents=True,exist_ok=True)
            with open(out, mode='w', encoding='utf-8') as f:
                for key, value in statistic.items():
                    f.write(json.dumps({key: value}) + '\n')
            logging.info(f'result write to {out}')
        else:
            logging.warning("没有任何文件成功统计，未写出结果")
                    
            


# ----------------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("OpenEval unified entry",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    sub = p.add_subparsers(dest="cmd", required=True,help="choose infer,eval or pipeline")
    #cmd 触发的sub
    # ---- infer
    sp_inf = sub.add_parser("infer", help="only run inference") #返回解析器，Argument parser
    add_infer_args(sp_inf)##为sp_inf 添加参数，改变对象并返回
    sp_inf.set_defaults(func=cmd_infer)#自动调度 args.func(args) 绑定： cmd_sth(args)

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