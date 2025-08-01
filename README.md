# Openeval
# Reasoning: Evaluation & Inference

A repository for evaluating and running inference on reasoning tasks using LLMs.

---

## 🚀 Progress

- **Inference backend**: ✔️ Realized  
- **Math support**: ✔️ Implemented

---

## 🗂️ TODO

### 1. Inference

- Support multiple datasets  
  - Design a high-level **registry** interface to register and manage all datasets  

### 2. Evaluation

- **Code review framework**  
- **Code judges**  
  - Research and integrate a secure sandbox environment  
  - Build or configure the sandbox  
- **Math judges**  
  - Regex-based solution checkers  
- **LLM as judge**  
  - Explore [OpenCompass](https://github.com/OpenCompass) as an example integration  

---

## 📅 Milestones

| Due Date   | Deliverable                                    |
|------------|------------------------------------------------|
| **July 7** | Complete dataset loading module                |
| **July 8** | Finish evaluation for Math & GPQA tasks        |
| **July 9** | Begin design of flexible registry functions    |
| **July 12**| Build end-to-end pipeline; prepare HF API demo |
| **July 28**| add difficult selection to pipeline function   |
| **August 1**| add Openai API for infernence pipeline        |
---
## Quick Start
- run `conda env create -f environment.yml`  or `pip install -r requirements.txt` to set up the environment.
  - Note: you may need to install `vllm` from source, as the latest version may not be compatible with the current code.
- view `run/eval/infer.sh` for quick start. Replace the path to your own model or datasets
- run ```./run.sh ``` for quick start
- `Openeval/run.py` is the main entry point, supporting infer,eval, and pipeline three modes
- to view datasets, locate your dataset to ```Openeval/datasets/test_data``` and run  ```python -m Openeval.datasets.overview ```
---
## How to List
### Full Pipeline:
  - Start with preprocessing datasets:  
    - all registered datasets are included in ```Openeval/datasets/data_info.py```
    - when adding a new dataset, you need to update datadict and `./utils/data_format` for its information(i.e. domains) and preprocessing functions
    - checkout what's in `./utils/data_format`
    - You can run overview.py to get an overview of the dataset. If output post-processing is delcared in `load_data.py`, view it in `Openeval/datasets/formatted_data`
  ### Important: The processed data must at least contain:
    - question
    - answer
  - Infernce
    - Start a vllm engine
      - Openeval/infer/online_batch.py is the main logic; run_infer is the entry point
      - Remember to align local host endpoint with point: i.e [http](http://0.0.0.0:7005/generate) vs --port 7005
    - run_infer:
      - `run_infer.py` check all files in the given directory and run inference on them sequentially.
      - parameter follows vllm's apis.
      - if you process data manually by running load_data.py, set  `--process_data = True` and `--data <formatted_data directory>`;
      - if you want run on raw data(registerd datasets),set `--process_data = False` and `--data <test_data directory>`
      - Path supports single file_path and glob pattern.
  - Evaluation
    - Process: extract from perdiction -> judge with LLM/Objective judge -> get score
    - Components:
      - Evaluator: handles the evaluation logic, supports LLM judger and Objective judger.
      - Extractor: handles the extraction logic, supports Objective extractor.
    - Check entry point at` Openeval/eval/run_eval.py`
    - Extractor result will be saved to debug directory, you can check both extractors and evaluations to validate the result
  - Logs:
    - view logs in `./logs`
## New
 - Vllm async Engine somehow have lower computing speed and it somtimes failed to stop at an early stage, therefore openai api is implemented for 
 - Want to use Openai apis? we have update new features now:
 - To use Openai apis ,just set the config endpoint to:
 ```http://local_host:port/generate_openai```
    - then it will automatically start the local or online model service on your machine

