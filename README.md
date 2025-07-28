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
## How to List
### Full Pipeline:
  - Start with preprocessing datasets:  
    - all registered datasets are included in Openeval/datasets/data_info.py
    - when adding a new dataset, you need to update datadict and ./utils/data_format for its information(i.e. domains) and preprocessing functions
    - checkout what's in ./utils/data_format
    - You can run overview.py to get an overview of the dataset.
  ### Important: The processed data must at least contain:
    - question
    - answer
  - Infernce
    - Start a vllm engine
      - Openeval/infer/online_batch.py is the main logic; run_infer is the entry point
  - Evaluation