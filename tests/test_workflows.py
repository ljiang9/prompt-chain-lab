import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mock as M


class TestRuleFunctions(unittest.TestCase):
    def test_detect_language(self):
        self.assertEqual(M.detect_language("你好世界"), "zh")
        self.assertEqual(M.detect_language("hello world"), "en")

    def test_mock_translate(self):
        self.assertTrue(M.mock_translate("你好").startswith("[EN-translated]"))
        self.assertTrue(M.mock_translate("hello").startswith("[中译]"))

    def test_mock_polish_adds_punct(self):
        out = M.mock_polish("  你好  世界 ")
        self.assertTrue(out.endswith("。"))
        self.assertNotIn("  ", out)

    def test_mock_summarize_first_sentence(self):
        out = M.mock_summarize("第一句。第二句。第三句。")
        self.assertEqual(out, "第一句。")

    def test_split_sections(self):
        text = "第一段。\n\n第二段。\n\n第三段。"
        secs = M.split_sections(text)
        self.assertEqual(len(secs), 3)

    def test_process_section(self):
        out = M.process_section("abc")
        self.assertIn("abc", out)

    def test_decompose_and_worker(self):
        subs = M.decompose("任务一；任务二；任务三")
        self.assertEqual(len(subs), 3)
        out = M.worker(subs[0])
        self.assertIn("完成", out)

    def test_aggregate(self):
        out = M.aggregate(["a", "b"])
        self.assertIn("a", out)
        self.assertIn("b", out)


class TestRouting(unittest.TestCase):
    def test_routing_question(self):
        self.assertEqual(M.route_decision("你吃饭了吗？"), "qa_handler")
        self.assertEqual(M.route_decision("How are you?"), "qa_handler")

    def test_routing_zh(self):
        self.assertEqual(M.route_decision("这是一段中文陈述"), "zh_handler")

    def test_routing_en(self):
        self.assertEqual(M.route_decision("this is english statement"),
                         "en_handler")

    def test_route_handler_output(self):
        out = M.route_handler("zh_handler", "测试")
        self.assertIn("中文通道", out)


class TestVoting(unittest.TestCase):
    def test_majority_vote(self):
        self.assertEqual(M.majority_vote(["正面", "正面", "负面"]), "正面")
        self.assertEqual(M.majority_vote(["负面", "负面", "正面"]), "负面")

    def test_majority_vote_empty(self):
        self.assertEqual(M.majority_vote([]), "中性")

    def test_vote_pass_positive(self):
        votes = [M.vote_pass("非常好，很棒", i) for i in (1, 2, 3)]
        self.assertIn(M.majority_vote(votes), ("正面", "中性"))

    def test_vote_pass_negative(self):
        votes = [M.vote_pass("太差了，很糟糕", i) for i in (1, 2, 3)]
        self.assertEqual(M.majority_vote(votes), "负面")


if __name__ == "__main__":
    unittest.main()
