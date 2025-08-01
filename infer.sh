python -m Openeval.run infer \
  --data ./Openeval/datasets/test_data/aime24.jsonl \
  --batch_size 32 \
  --endpoint http://10.200.250.35:7004/generate_openai \
  --prediction_dir predictions/openai/qwen2.5_instruct_7b \
  --sampling_params '{"temperature":0.9,"top_p":0.85,"max_tokens":8192,"n":10,"presence_penalty":0,"repetition_penalty":0.8}' \
  --loglevel INFO \
  --model /DATA/disk1/zhurui/Reasoning/StageI/Openeval/models/qwen2.5_instruct_7b \
  --port 7004 \
  --tensor_parallel_size 1 \
  --host 10.200.250.35 \
  --m_abbr qwen2.5_7b \
  #先format ，只load formatted data
  