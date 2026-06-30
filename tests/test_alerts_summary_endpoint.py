# -*- coding: utf-8 -*-
"""Tests for the alerts-summary endpoint (/summary)."""

import unittest

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from api.v1.endpoints.alerts_summary import router as alerts_summary_router


def _make_client() -> TestClient:
    # 直接挂载该模块自身的路由进行测试
    app = FastAPI()
    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(
        alerts_summary_router,
        prefix="/alerts-summary",
        tags=["AlertsSummary"],
    )
    app.include_router(api_router)
    return TestClient(app)


class AlertsSummaryEndpointTestCase(unittest.TestCase):
    """告警概览接口应返回 200 及有效的分级统计。"""

    @classmethod
    def setUpClass(cls):
        cls.client = _make_client()

    def test_summary_returns_200(self):
        resp = self.client.get("/api/v1/alerts-summary/summary")
        self.assertEqual(resp.status_code, 200)

    def test_summary_payload_shape(self):
        resp = self.client.get("/api/v1/alerts-summary/summary")
        body = resp.json()
        self.assertIn("total", body)
        self.assertIn("by_level", body)
        self.assertEqual(body["levels"], ["critical", "warning", "info"])
        self.assertEqual(
            body["total"],
            sum(body["by_level"].values()),
        )


if __name__ == "__main__":
    unittest.main()
