python -m Openeval.run eval \
  --eval_data  predictions/openai/qwen2.5_instruct_7b/aime24_qwen2.5_7b_pred.jsonl \
  --mode       Objective \
  --k          1 8\
  -a           qwen2.5_7b \
  --eval_out_dir     ./evaluations/openai \
  --judge_endpoint http://10.200.250.35:7001/generate \
  --judge_model     /DATA/disk2/rlteam/models/checkpoint0724\
  --judge_host      10.200.250.35 \
  --judge_port      7001 \
  --judge_tensor_parallel_size 1 \
  -ex ./debugging/qwen7




# merged_top90_filtered_promptid_1_qwen2.5_7b_pred
# merged_top90_filtered_promptid_2_qwen2.5_7b_pred
# merged_top90_filtered_promptid_3_qwen2.5_7b_pred
# 对齐输出路径，即model_abbr后缀与preditcion
# 匹配路径与endpoint
# merged_top90_filtered_promptid_4_qwen2.5_7b_pred