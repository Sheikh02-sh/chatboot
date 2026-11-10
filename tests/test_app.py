"""Workflow tests. The OpenRouter call is mocked, so no API key or network is needed."""
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["OPENROUTER_API_KEY"] = "test-key"

import requests  # noqa: E402

import app as seo  # noqa: E402

GOOD = {
    "titles": [{"title": f"Minecraft Redstone Guide {i}", "angle": "how-to"} for i in range(5)],
    "description": "Learn redstone in Minecraft step by step.\n\nSubscribe for more.\n\n#minecraft #redstone",
    "keywords": ["minecraft redstone", "redstone tutorial", "minecraft for beginners"],
    "tags": ["minecraft", "redstone", "tutorial", "gaming"],
    "hashtags": ["#minecraft", "redstone"],
    "shorts": [
        {"hook": "Redstone made easy.", "script": "Redstone made easy. Here is how it works.", "on_screen_text": "Redstone 101"},
        {"hook": "Stop doing this.", "script": "Stop doing this with your torches.", "on_screen_text": ""},
    ],
}


class FakeResponse:
    def __init__(self, content, status=200):
        self.status_code = status
        self._content = content

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


class Tests(unittest.TestCase):
    def setUp(self):
        self.client = seo.app.test_client()

    def generate(self, payload, reply):
        with mock.patch.object(seo.requests, "post", return_value=reply):
            return self.client.post("/api/generate", json=payload)

    def test_pages(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Hookline", res.data)
        res.close()
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/api/config").get_json()["limits"]["topic"]["max"], 500)

    def test_validation(self):
        bad = [
            {"input": "", "mode": "topic"},
            {"input": "  ", "mode": "topic"},
            {"input": "hi", "mode": "topic"},
            {"input": "x" * 501, "mode": "topic"},
            {"input": "too short for a script", "mode": "script"},
            {"input": "x" * 12001, "mode": "script"},
            {"input": "A real topic", "mode": "other"},
            {"input": 5, "mode": "topic"},
        ]
        for payload in bad:
            self.assertEqual(self.client.post("/api/generate", json=payload).status_code, 400, payload)
        self.assertEqual(self.client.post("/api/generate", data="nope").status_code, 400)

    def test_success_and_normalization(self):
        res = self.generate({"input": "Beginner Minecraft redstone", "mode": "topic", "tone": "Energetic"},
                            FakeResponse(json.dumps(GOOD)))
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data["titles"]), 5)
        self.assertEqual(data["hashtags"], ["#minecraft", "#redstone"])
        self.assertEqual(data["tag_characters"], len(",".join(data["tags"])))
        self.assertEqual(len(data["shorts"]), 2)

    def test_script_mode_and_fenced_json(self):
        script = "Welcome back to the channel. Today we build a piston door in Minecraft."
        reply = FakeResponse("Sure!\n```json\n" + json.dumps(GOOD) + "\n```")
        self.assertEqual(self.generate({"input": script, "mode": "script"}, reply).status_code, 200)

    def test_tags_trimmed_to_500_characters(self):
        data = dict(GOOD, tags=[f"tag number {i:03d} " + "x" * 20 for i in range(40)])
        res = self.generate({"input": "Some topic", "mode": "topic"}, FakeResponse(json.dumps(data)))
        self.assertEqual(res.status_code, 200)
        self.assertLessEqual(res.get_json()["tag_characters"], 500)

    def test_bad_ai_output_rejected(self):
        cases = [
            "not json",
            json.dumps([GOOD]),
            json.dumps(dict(GOOD, titles=[{"title": "Only one", "angle": "x"}])),
            json.dumps(dict(GOOD, description="  ")),
            json.dumps(dict(GOOD, keywords=["one"])),
            json.dumps(dict(GOOD, shorts=[GOOD["shorts"][0]])),
            json.dumps({k: v for k, v in GOOD.items() if k != "tags"}),
        ]
        for content in cases:
            res = self.generate({"input": "Some topic", "mode": "topic"}, FakeResponse(content))
            self.assertEqual(res.status_code, 502, content)

    def test_upstream_failures(self):
        payload = {"input": "Some topic", "mode": "topic"}
        with mock.patch.object(seo.requests, "post", side_effect=requests.Timeout()):
            self.assertEqual(self.client.post("/api/generate", json=payload).status_code, 504)
        with mock.patch.object(seo.requests, "post", side_effect=requests.ConnectionError()):
            self.assertEqual(self.client.post("/api/generate", json=payload).status_code, 502)
        for status in (401, 402, 429, 500):
            res = self.generate(payload, FakeResponse("", status))
            self.assertEqual(res.status_code, 429 if status == 429 else 502)

    def test_missing_api_key(self):
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            res = self.client.post("/api/generate", json={"input": "Some topic", "mode": "topic"})
        self.assertEqual(res.status_code, 503)
        self.assertIn("OPENROUTER_API_KEY", res.get_json()["error"])

    def test_cors_for_live_server(self):
        origin = "http://127.0.0.1:5500"
        pre = self.client.options("/api/generate", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"})
        self.assertEqual(pre.headers["Access-Control-Allow-Origin"], origin)
        res = self.client.get("/api/config", headers={"Origin": "https://evil.example"})
        self.assertNotIn("Access-Control-Allow-Origin", res.headers)


if __name__ == "__main__":
    unittest.main()
