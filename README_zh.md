# Openeval（中文说明）
**推理任务的评测与推理执行框架**

[English Version](./README.md) | **中文说明**

---

## 🚀 进展

- **推理后端**：✔️ 已实现  
- **数学任务支持**：✔️ 已实现

---

## 🗂️ 待办事项（TODO）

### 1. 推理（Inference）
- 支持**多数据集**
  - 设计高层 **registry** 注册接口来管理所有数据集

### 2. 评测（Evaluation）
- **代码评审框架**
- **代码判题**
  - 调研并集成**安全沙箱**
  - 构建或配置沙箱环境
- **数学判题**
  - 基于正则的答案核对器
- **LLM 作为判题**
  - 参考 [OpenCompass](https://github.com/OpenCompass) 的集成方式

---

## 📅 里程碑（Milestones）

| 截止日期 | 交付物 |
|---|---|
| **7月7日** | 完成数据集加载模块 |
| **7月8日** | 完成 Math & GPQA 评测 |
| **7月9日** | 开始设计弹性的 registry 函数 |
| **7月12日** | 打通端到端流水线；准备 HF API Demo |
| **7月28日** | 在 pipeline 中加入“难度选择”功能 |
| **8月1日** | 在推理流水线中加入 OpenAI API 适配 |

---

## 快速开始（Quick Start）
- 运行 `conda env create -f environment.yml` 或 `pip install -r requirements.txt` 安装依赖  
  - 注：可能需要从源码安装 `vllm`，因为最新版可能与当前代码不兼容
- 查看 `run/eval/infer.sh` 获取快速启动示例，替换为你的模型或数据集路径
- 直接执行 `./run.sh` 快速启动
- 主入口为 `Openeval/run.py`，支持 **infer / eval / pipeline** 三种模式
- 想查看数据集：把你的数据集放到 `Openeval/datasets/test_data`，然后运行  
  ```bash
  python -m Openeval.datasets.overview