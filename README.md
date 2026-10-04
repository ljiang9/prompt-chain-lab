# Prompt Workflow 演示集（prompt-chain-lab）

一个 **零第三方依赖** 的 Python 小项目，演示四种经典 LLM prompt workflow 模式。
有 OpenAI 兼容 Key 时每步调 LLM；无 key 时自动用内置规则函数模拟，完整可跑。

## 四种模式

| 模式 | 说明 |
|------|------|
| `chaining` | 翻译 → 润色 → 摘要，三步串联，后一步以前一步输出为输入 |
| `routing` | 按输入语言 / 是否问句路由到 `zh_handler` / `en_handler` / `qa_handler` |
| `parallelization` | ① `sectioning`：分段并行处理后合并；② `voting`：多路独立投票后多数表决 |
| `orchestrator-worker` | 主控把大任务拆成子任务，并行分发给 worker，最后汇总 |

并行使用标准库 `concurrent.futures.ThreadPoolExecutor`。

## 快速开始

环境要求：Python 3.10+（验证于 3.12），无需安装任何依赖。

```bash
git clone https://github.com/ljiang9/prompt-chain-lab.git
cd prompt-chain-lab
```

## 使用示例（无 key，纯规则）

```bash
python3 cli.py --mode chaining --text "人工智能正在改变世界。它影响医疗和教育。"
python3 cli.py --mode routing --text "你好，请问今天天气怎么样？"
python3 cli.py --mode sectioning --text $'第一段内容。\n\n第二段内容。\n\n第三段。'
python3 cli.py --mode voting --text "这个产品非常好，我很喜欢"
python3 cli.py --mode orchestrator --text "写摘要；润色开头；检查错别字"
```

每一步都会打印中间结果。

## 有 key 时启用 LLM

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"   # 可选
export OPENAI_MODEL="gpt-4o-mini"                    # 可选
python3 cli.py --mode chaining --text "..." --llm
```

LLM 调用失败会自动降级回内置规则，并打印 `[warn]`。

## 目录结构

```
prompt-chain-lab/
├── cli.py            # 命令行入口（--mode 选择模式）
├── workflows.py     # 四种 workflow 编排
├── mock.py          # 内置规则函数 + 可选 LLM 调用
├── tests/
│   └── test_workflows.py
├── README.md
├── LICENSE           # MIT
└── .gitignore
```

## 运行测试

```bash
python3 -m unittest discover -s tests
```

## 许可证

MIT License，见 [LICENSE](./LICENSE)。
