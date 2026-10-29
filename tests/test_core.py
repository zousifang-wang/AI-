import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from core import complete, make_messages


class TutoringTests(unittest.TestCase):
    def test_sources_and_history_budget(self):
        history = [{"role": "user", "content": "x" * 17000}, {"role": "assistant", "content": "y"}]
        messages = make_messages("数据结构", "栈\n队列", history, "请解释")
        self.assertIn("2: 队列", messages[1]["content"])
        self.assertFalse(any(m["content"] == history[0]["content"] for m in messages))
        self.assertEqual(messages[-1]["content"], "请解释")

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("core.request.urlopen")
    def test_api_request_and_response(self, transport):
        transport.return_value.__enter__.return_value = io.BytesIO(json.dumps({"choices": [{"message": {"content": "先想一想边界条件"}}]}).encode())
        answer = complete(make_messages("算法", "", [], "怎么做"))
        self.assertIn("边界", answer)
        req = transport.call_args.args[0]
        self.assertEqual(req.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(json.loads(req.data)["messages"][-1]["content"], "怎么做")

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("core.request.urlopen", side_effect=HTTPError("url", 401, "secret response", {}, None))
    def test_errors_do_not_expose_raw_response(self, transport):
        with self.assertRaisesRegex(RuntimeError, "密钥无效"):
            complete([])

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": ""})
    def test_missing_key(self):
        with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
            complete([])

    def test_material_limit(self):
        with self.assertRaises(ValueError):
            make_messages("课程", "a" * 20001, [], "问题")


if __name__ == "__main__":
    unittest.main()
