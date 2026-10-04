from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import mock as M


def _step(use_llm, prompt, system, mock_fn, *args):
    if use_llm and M.has_llm():
        try:
            return M.llm(prompt, system=system)
        except Exception as exc:
            print("  [warn] LLM 失败，降级规则：" + str(exc))
    return mock_fn(*args)


def run_chaining(text, use_llm=True):
    print("[1/3] 翻译中...")
    translated = _step(use_llm, "把下面文本翻译为目标语言：" + text,
                       "你是翻译。", M.mock_translate, text)
    print("  -> " + translated)

    print("[2/3] 润色中...")
    polished = _step(use_llm, "润色下面文本：" + translated,
                    "你是润色编辑。", M.mock_polish, translated)
    print("  -> " + polished)

    print("[3/3] 摘要中...")
    summary = _step(use_llm, "请摘要：" + polished,
                    "你是摘要助手。", M.mock_summarize, polished)
    print("  -> " + summary)
    return summary


def run_routing(text, use_llm=True):
    channel = M.route_decision(text)
    print("路由判定 -> " + channel)
    if use_llm and M.has_llm():
        try:
            out = M.llm("请处理以下输入（通道 " + channel + "）：" + text,
                        system="你是 " + channel + " 的处理助手。")
            print("  -> " + out)
            return out
        except Exception as exc:
            print("  [warn] LLM 失败，降级规则：" + str(exc))
    out = M.route_handler(channel, text)
    print("  -> " + out)
    return out


def run_sectioning(text, use_llm=True):
    sections = M.split_sections(text)
    print("切分为 %d 个 section，并行处理..." % len(sections))

    def _process(sec):
        return _step(use_llm, "处理这段：" + sec,
                     "你是分段处理助手。", M.process_section, sec)

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(_process, sections))
    for i, r in enumerate(results, 1):
        print("  section%d -> %s" % (i, r))
    merged = "\n".join(results)
    print("合并结果：\n" + merged)
    return merged


def run_voting(text, passes=3, use_llm=True):
    print("启动 %d 路并行投票..." % passes)

    def _vote(i):
        if use_llm and M.has_llm():
            try:
                return M.llm("判断情感（第" + str(i) + "次独立判断）：" + text,
                             system="只回答 正面/负面/中性。")
            except Exception:
                pass
        return M.vote_pass(text, i)

    with ThreadPoolExecutor(max_workers=passes) as ex:
        votes = list(ex.map(_vote, range(1, passes + 1)))
    for i, v in enumerate(votes, 1):
        print("  投票%d -> %s" % (i, v))
    final = M.majority_vote(votes)
    print("多数表决 -> " + final)
    return final


def run_orchestrator(task, use_llm=True):
    subtasks = M.decompose(task)
    print("主控拆出 %d 个子任务：" % len(subtasks))
    for i, st in enumerate(subtasks, 1):
        print("  子任务%d: %s" % (i, st))

    def _work(st):
        if use_llm and M.has_llm():
            try:
                return M.llm("完成这个子任务：" + st, system="你是 worker。")
            except Exception:
                pass
        return M.worker(st)

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(_work, subtasks))
    for i, r in enumerate(results, 1):
        print("  worker%d -> %s" % (i, r))
    final = M.aggregate(results)
    print("主控汇总 -> " + final)
    return final
