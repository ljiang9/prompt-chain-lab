from __future__ import annotations

import json
import os
import re
import urllib.request


def has_llm():
    return bool(os.environ.get("OPENAI_API_KEY"))


def llm(prompt, system="你是一个有帮助的助手。"):
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = (os.environ.get("OPENAI_BASE_URL")
                or "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise RuntimeError("未设置 OPENAI_API_KEY")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }
    req = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + api_key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def detect_language(text):
    return "zh" if _CJK_RE.search(text) else "en"


def mock_translate(text):
    if detect_language(text) == "zh":
        return "[EN-translated] " + text
    return "[中译] " + text


def mock_polish(text):
    t = re.sub(r"\s+", " ", text.strip())
    if t and t[-1] not in "。.!?！？":
        t += "。"
    return t


def mock_summarize(text):
    parts = re.split(r"(?<=[。！？!?])", text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts[0] if parts else text.strip()


def route_decision(text):
    s = text.strip()
    if s.endswith("?") or s.endswith("？"):
        return "qa_handler"
    return "zh_handler" if detect_language(s) == "zh" else "en_handler"


def route_handler(channel, text):
    table = {
        "zh_handler": "【中文通道】已按中文规则处理：" + text,
        "en_handler": "【English channel】handled: " + text,
        "qa_handler": "【问答通道】已生成简答：" + text,
    }
    return table.get(channel, "【默认通道】" + text)


def split_sections(text):
    return [s.strip() for s in re.split(r"\n\s*\n", text) if s.strip()]


def process_section(section):
    return "<section " + str(len(section)) + "字> " + section.strip()


_POS_HINT = ("好", "棒", "优秀", "great", "good", "happy")
_NEG_HINT = ("差", "糟", "坏", "bad", "terrible", "awful")


def vote_pass(text, pass_idx):
    score = 0
    for w in _POS_HINT:
        if w in text:
            score += 1
    for w in _NEG_HINT:
        if w in text:
            score -= 1
    offset = (pass_idx - 1) * 0.3
    s = score + offset
    if s > 0.5:
        return "正面"
    if s < -0.5:
        return "负面"
    return "中性"


def majority_vote(results):
    from collections import Counter
    if not results:
        return "中性"
    return Counter(results).most_common(1)[0][0]


def decompose(task):
    parts = re.split(r"[。；;\n]+", task)
    return [p.strip() for p in parts if p.strip()]


def worker(subtask):
    return "[完成] " + subtask + "（" + str(len(subtask)) + "字）"


def aggregate(results):
    return "；".join(results)
