import multiprocessing as mp, socket, time, sys, logging
from Openeval.infer.online_batch import start_vllm_server
def launch_vllm_bg(args):
    """后台启动 vLLM；返回 Process 句柄"""
    ctx = mp.get_context("spawn")           # 避免 fork 的 GPU 句柄问题
    proc = ctx.Process(
        target=start_vllm_server,
        args=(args.judge_model, args.judge_port),
        kwargs=dict(tensor_parallel_size=args.judge_tensor_parallel_size)
    )
    proc.start()
    return proc
