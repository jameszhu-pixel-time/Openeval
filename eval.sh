python -m Openeval.run eval \
  --eval_data /DATA/disk1/zhurui/Reasoning/Openeval/predictions/math500\*.jsonl \
  --mode       Objective \
  --k          1 8\
  -a           debug \
  --eval_out_dir     ./evaluations/debug \
  --judge_endpoint http://10.200.250.35:7001/generate \
  --judge_model     /DATA/disk2/rlteam/models/checkpoint0724\
  --judge_host      10.200.250.35 \
  --judge_port      7001 \
  --judge_tensor_parallel_size 1 \
  --difficulty_selection_eval 8\
  -ex ./debugging/debug




# merged_top90_filtered_promptid_1_qwen2.5_7b_pred
# merged_top90_filtered_promptid_2_qwen2.5_7b_pred
# merged_top90_filtered_promptid_3_qwen2.5_7b_pred
# 对齐输出路径，即model_abbr后缀与preditcion
# 匹配路径与endpoint
# merged_top90_filtered_promptid_4_qwen2.5_7b_pred
# 现在也支持difficulty selection
# --difficulty_selection_eval 8\ 指定pass@8 rate的结果作为难度选择