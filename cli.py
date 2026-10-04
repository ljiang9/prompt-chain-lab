from __future__ import annotations

import argparse
import sys

import workflows as W


def build_parser():
    p = argparse.ArgumentParser(
        prog="prompt-chain-lab",
        description="四种 prompt workflow 演示（chaining/routing/parallelization/orchestrator-worker）",
    )
    p.add_argument("--mode", required=True,
                   choices=["chaining", "routing", "sectioning", "voting",
                            "orchestrator"],
                   help="选择要运行的 workflow 模式")
    p.add_argument("--text", required=True, help="输入文本")
    p.add_argument("--llm", action="store_true", help="有 key 时尝试调用 LLM")
    p.add_argument("--no-llm", action="store_true", help="强制只走内置规则")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    use_llm = args.llm and not args.no_llm

    dispatch = {
        "chaining": W.run_chaining,
        "routing": W.run_routing,
        "sectioning": W.run_sectioning,
        "voting": W.run_voting,
        "orchestrator": W.run_orchestrator,
    }
    fn = dispatch[args.mode]
    print("=== mode: " + args.mode + " ===")
    fn(args.text, use_llm=use_llm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
