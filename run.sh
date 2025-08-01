# 3) 一条龙：推理 + 评测 (pipeline)
# ──────────────────────────────────────────────────────────────
python -m Openeval.run pipeline \
  --data ./Openeval/datasets/test_data/aime24.jsonl \
  --batch_size 16 \
  --sampling_params '{"temperature":0.85,"top_p":0.85,"max_tokens":8192,"n":8,"presence_penalty":1,"repetition_penalty":1.2}' \
  --model /DATA/disk1/zhurui/Reasoning/StageI/Openeval/models/qwen2.5_instruct_7b \
  --endpoint http://10.200.250.35:7004/generate_openai \
  --port 7004 \
  --tensor_parallel_size 2 \
  --mode Objective \
  --k 1 8 \
  --model_abbr qwen7B \
  --eval_out_dir evaluations/qwen7b \
  --judge_model /DATA/disk1/wsh/DATA/disk1/wsh/MScache/models/Qwen/Qwen3-32B \
  --difficulty_selection \
  --m_abbr qwen2.5_7b \
  -ex ./debugging/qwen7b

  
                                   
# --data:经过处理的数据，必须包含 prompt 加入过prompt的）与 answer（数值答案）
# --vllm 参数
# --mode Objective 客观评估 
# --difficulty_selection 模式： 你只能指定一个数据集， main 会讲多个prompt 分发给该dataset，注意，你需要使用 List[dict]
#,并储存至Openeval/datasets/prompts/difficult_selection.py
##使用本地openai 接口 --endpoint http://10.200.250.35:7004/generate_openai 
