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
---
## Quick Start
- run `conda env create -f environment.yml`  or `pip install -r requirements.txt` to set up the environment.
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
      - `Openeval/infer/online_batch.py` is the main logic; `run_infer.py` is the entry point
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
  - Logs:
    - view logs in `./logs`
