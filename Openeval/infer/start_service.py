import subprocess
import logging
def launch_vllm_server(
    model: str = '/DATA/disk1/zhurui/Reasoning/StageI/Openeval/models/qwen2.5_instruct_32b',
    host: str = "0.0.0.0",
    port: str = '7000',
    tensor_parallel: int =4,
    max_model_len: int = None,
    cuda_devices: str = "0,1"
):
    cmd = [
        "vllm", "serve", model,
        "--host", host,
        "--port", str(port),
        "--tensor-parallel-size", str(tensor_parallel),
    ]
    logging.info(f"debug:{cmd},{type(cmd[4])}")
    if max_model_len is not None:
        cmd += ["--max-model-len", str(max_model_len)]

    logging.info(f"[INFO] Launching: {' '.join(cmd)}")
    process = subprocess.Popen(cmd)
    return process  # 可供后续使用，如 terminate()

# 示例调用
if __name__ == "__main__":
    process = launch_vllm_server()