python -m Openeval.run eval \
  --eval_data  predictions/difficult_new/qwen2.5_instruct_7b/deduped_questions_00_of_03_promptid_4_qwen2.5_7b_pred.jsonl \
  --mode       Objective \
  --k          1 \
  -a           qwen2.5_7b \
  --eval_out_dir     ./evaluations/difficult_new/qwen2.5_instruct_7b/deduped_questions_00_of_03_promptid_4_qwen2.5_7b_pred.jsonl \
  --judge_endpoint http://10.200.250.35:7000/generate \
  --judge_model     /DATA/disk1/wsh/DATA/disk1/wsh/MScache/models/Qwen/Qwen3-32B \
  --judge_host      10.200.250.35 \
  --judge_port      7000 \
  --judge_tensor_parallel_size 4 \
  -ex ./debugging/eval_extract/qwen2.5_8b/difficult_new/qwen2.5_instruct_7b/deduped_questions_00_of_03_promptid_4_qwen2.5_7b_pred.jsonl




# merged_top90_filtered_promptid_1_qwen2.5_7b_pred
# merged_top90_filtered_promptid_2_qwen2.5_7b_pred
# merged_top90_filtered_promptid_3_qwen2.5_7b_pred
# merged_top90_filtered_promptid_4_qwen2.5_7b_pred