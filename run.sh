# 3) 一条龙：推理 + 评测 (pipeline)
# ──────────────────────────────────────────────────────────────
python -m Openeval.run pipeline \
  --data ./Openeval/datasets/test_data/aime\*.jsonl \
  --batch_size 8 \
  --sampling_params '{"temperature":0.9,"top_p":0.85,"max_tokens":8192,"n":1,"presence_penalty":1,"repetition_penalty":1.2}' \
  --model /DATA/disk2/rlteam/models/checkpoint0724 \
  --tensor_parallel_size 1 \
  --mode Objective \
  --k 1 8 \
  --model_abbr checkpoint0724 \
  --eval_out_dir evaluations/checkpoint0724 \
  --judge_model /DATA/disk1/wsh/DATA/disk1/wsh/MScache/models/Qwen/Qwen3-32B
  
                                   
# --data:经过处理的数据，必须包含 prompt 加入过prompt的）与 answer（数值答案）
# --vllm 参数
# --mode Objective 客观评估
