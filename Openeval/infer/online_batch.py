import argparse
from vllm import LLM, SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.utils import random_uuid
import asyncio
from typing import List,Union,Dict
import os
from asyncio import Semaphore, gather
import logging
import openai
from Openeval.infer.mp import generate_mp
from concurrent.futures import ProcessPoolExecutor, as_completed
def start_vllm_server(model_path, host="0.0.0.0", port=7000, tensor_parallel_size=1):
    """Starts a vLLM server."""

    engine_args = AsyncEngineArgs(
        model=model_path,
        tensor_parallel_size=tensor_parallel_size,
        gpu_memory_utilization=0.95,  # Adjust as needed
        # swap_space_size=4,  # Adjust as needed (in GiB)
        disable_log_stats=True,
        max_num_seqs=256,
        max_num_batched_tokens=8192,
    )
    engine = AsyncLLMEngine.from_engine_args(engine_args)

        
    async def generate(prompts: Union[str, List[str]], sp) -> List[List[str]]:
        if isinstance(prompts, str):
            prompts = [prompts]

        async def one_prompt(p: str) -> List[str]:
            req_id = random_uuid()
            async for out in engine.generate(p, sp, req_id):
                if out.finished:
                    return [o.text for o in out.outputs]

        return await asyncio.gather(*(one_prompt(p) for p in prompts))
    


    import asyncio
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel

    class GenerationRequest(BaseModel):
        prompt: Union[str, List[str]]
        sampling_params: dict = {}

    app = FastAPI()

    @app.post("/generate")
    async def generate_endpoint(request: GenerationRequest):
        try:
            sampling_params = SamplingParams(**request.sampling_params)
            flag = isinstance(request.prompt, list)
            result = await generate(request.prompt, sampling_params)
            return JSONResponse({"text": result})
        except ValueError as e:               # 参数不合法
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e: 
            if e.response.status_code == 500:# 其他未知错误
                logging.error("SERVER-500 detail: %s", e.response.text)
            raise HTTPException(status_code=500, detail=str(e))
    #-----
    
    
    @app.post("/generate_openai")
    async def generate_openai_endpoint(request: GenerationRequest):
        from concurrent.futures import ProcessPoolExecutor

        prompts = request.prompt
        if isinstance(prompts, str):
            prompts = [prompts]
        response = [None] * len(prompts)
        host = "10.200.250.35"
        with ProcessPoolExecutor(max_workers=len(prompts)) as pool:
            fut_to_id = {
                pool.submit(generate_mp, p, model_path, request.sampling_params, host, port): idx
                for idx, p in enumerate(prompts)
            }
            for fut in fut_to_id:
                response[fut_to_id[fut]] = fut.result()

        return JSONResponse({'text': response})
                
            
            
            
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vLLM Server")
    parser.add_argument("--model", type=str, help="Path to the model",default="/DATA/disk1/zhurui/Reasoning/StageI/Openeval/models/qwen2.5_instruct_7b")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP")
    parser.add_argument("--port", type=int, default=7005, help="Port number")
    parser.add_argument("-t","--tensor_parallel_size", type=int, default=1, help="Tensor parallel size")
    args = parser.parse_args()

    start_vllm_server(args.model, args.host, args.port, args.tensor_parallel_size)