# 3) 一条龙：推理 + 评测 (pipeline)
# ──────────────────────────────────────────────────────────────
python -m Openeval.run pipeline \
  --data ./Openeval/datasets/test_data/aime24.jsonl \
  --batch_size 32 \
  --sampling_params '{"temperature":0.9,"top_p":0.85,"max_tokens":8192,"n":10,"presence_penalty":1,"repetition_penalty":1.2}' \
  --model /DATA/disk1/zhurui/Reasoning/StageI/Openeval/models/qwen2.5_instruct_7b \
  --tensor_parallel_size 1 \
  --mode Objective \
  --k 1 8 \
  --model_abbr checkpoint0724 \
  --eval_out_dir evaluations/checkpoint0724 \
  --judge_model /DATA/disk1/wsh/DATA/disk1/wsh/MScache/models/Qwen/Qwen3-32B \
  --difficulty_selection \

  
                                   
# --data:经过处理的数据，必须包含 prompt 加入过prompt的）与 answer（数值答案）
# --vllm 参数
# --mode Objective 客观评估 
# --difficulty_selection 模式： 你只能指定一个数据集， main 会讲多个prompt 分发给该dataset，注意，你需要使用 List[dict]
#,并储存至Openeval/datasets/prompts/difficult_selection.py
