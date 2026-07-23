# -*- coding: utf-8 -*-
"""Tests for the default watchlist summary endpoint: /api/v1/watchlist/summary."""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def _make_client():
    temp_dir = tempfile.TemporaryDirectory()
    return temp_dir, TestClient(create_app(static_dir=Path(temp_dir.name)))


class WatchlistEndpointTestCase(unittest.TestCase):
    """The watchlist summary endpoint should return 200 with the expected shape."""

    @classmethod
    def setUpClass(cls):
        cls._temp_dir, cls.client = _make_client()

    @classmethod
    def tearDownClass(cls):
        cls._temp_dir.cleanup()

    def test_watchlist_summary_returns_200(self):
        resp = self.client.get("/api/v1/watchlist/summary")
        self.assertEqual(resp.status_code, 200)

    def test_watchlist_summary_shape(self):
        body = self.client.get("/api/v1/watchlist/summary").json()
        self.assertIn("total", body)
        self.assertIn("groups", body)
        self.assertIn("items", body)
        self.assertIsInstance(body["groups"], list)
        self.assertIsInstance(body["items"], list)
        # total must match the number of returned items
        self.assertEqual(body["total"], len(body["items"]))
        self.assertGreater(body["total"], 0)

    def test_watchlist_items_have_expected_fields(self):
        body = self.client.get("/api/v1/watchlist/summary").json()
        first = body["items"][0]
        for field in ("code", "name", "market", "group"):
            self.assertIn(field, first)
        # every item's group must appear in the deduplicated groups list
        for item in body["items"]:
            self.assertIn(item["group"], body["groups"])


if __name__ == "__main__":
    unittest.main()
