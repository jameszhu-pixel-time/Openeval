python -m Openeval.run infer \
  --data ./Openeval/datasets/test_data/aime\*.jsonl \
  --batch_size 8 \
  --endpoint http://10.200.250.35:7005/generate \
  --prediction_dir predictions/qwen2.5_instruct_7b \
  --sampling_params '{"temperature":0.9,"top_p":0.85,"max_tokens":8192,"n":1,"presence_penalty":0.8,"repetition_penalty":0.8}' \
  --loglevel INFO \
  --model /DATA/disk2/rlteam/models/checkpoint0724\
  --port 7005 \
  --tensor_parallel_size 1 \
  --host 10.200.250.35 \
  --m_abbr qwen2.5_7b \
  #先format ，只load formatted data
  