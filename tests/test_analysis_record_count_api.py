# -*- coding: utf-8 -*-
"""
===================================
分析记录数量接口单元测试
===================================

职责：
1. 验证 GET /api/v1/analysis/records/count 返回已落库记录数量
2. 验证可按股票代码筛选
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Keep this test runnable when optional LLM runtime deps are not installed.
try:
    import litellm  # noqa: F401
except ModuleNotFoundError:
    sys.modules["litellm"] = MagicMock()

try:
    from fastapi.testclient import TestClient
    from api.app import create_app
except ModuleNotFoundError:
    TestClient = None
    create_app = None

from src.config import Config
from src.storage import DatabaseManager
from src.analyzer import AnalysisResult
import src.auth as auth


class AnalysisRecordCountAPITestCase(unittest.TestCase):
    """分析记录数量接口测试"""

    def setUp(self) -> None:
        """为每个用例初始化独立数据库"""
        auth._auth_enabled = False
        self._temp_dir = tempfile.TemporaryDirectory()
        self._db_path = os.path.join(self._temp_dir.name, "test_record_count.db")
        os.environ["DATABASE_PATH"] = self._db_path

        Config._instance = None
        DatabaseManager.reset_instance()
        self.db = DatabaseManager.get_instance()

    def tearDown(self) -> None:
        """清理资源"""
        DatabaseManager.reset_instance()
        self._temp_dir.cleanup()

    def _save_history(self, code: str, query_id: str) -> None:
        """保存一条测试历史记录。"""
        result = AnalysisResult(
            code=code,
            name="测试股票",
            sentiment_score=70,
            trend_prediction="看多",
            operation_advice="持有",
            analysis_summary="测试摘要",
        )
        saved = self.db.save_analysis_history(
            result=result,
            query_id=query_id,
            report_type="simple",
            news_content="新闻摘要",
            context_snapshot=None,
            save_snapshot=False,
        )
        self.assertEqual(saved, 1)

    def _client(self) -> "TestClient":
        static_dir = Path(self._temp_dir.name) / "empty-static"
        static_dir.mkdir(exist_ok=True)
        return TestClient(create_app(static_dir=static_dir))

    @patch("src.auth.is_auth_enabled", return_value=False)
    def test_record_count_returns_total_records(self, _mock_auth) -> None:
        """GET /records/count 无 code 时返回全部记录数量。"""
        if TestClient is None or create_app is None:
            self.skipTest("fastapi is not installed in this test environment")

        self._save_history("600519", "query_count_1")
        self._save_history("000001", "query_count_2")

        response = self._client().get("/api/v1/analysis/records/count")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNone(payload["code"])
        self.assertEqual(payload["days"], 30)
        self.assertEqual(payload["count"], 2)

    @patch("src.auth.is_auth_enabled", return_value=False)
    def test_record_count_filters_by_code(self, _mock_auth) -> None:
        """GET /records/count 带 code 时只统计该股票的记录。"""
        if TestClient is None or create_app is None:
            self.skipTest("fastapi is not installed in this test environment")

        self._save_history("600519", "query_count_a1")
        self._save_history("600519", "query_count_a2")
        self._save_history("000001", "query_count_b1")

        response = self._client().get("/api/v1/analysis/records/count", params={"code": "600519"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 2)


if __name__ == "__main__":
    unittest.main()
