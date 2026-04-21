"""
Unit Tests：send_report.py 核心邏輯驗證。

不啟動瀏覽器、不讀取真實檔案、不寄送 email。
所有外部 I/O 皆由 unittest.mock 替換，測試速度 < 100ms。

Test ID 範圍：TC-UNIT-RPT-001 ~ TC-UNIT-RPT-010
"""
import json
from unittest.mock import patch, mock_open, MagicMock

import pytest

from send_report import (
    _is_credentials_skip,
    _mask_email,
    _parse_receiver_list,
    _pick_local_report_html,
    get_detailed_report,
)


class TestIsCredentialsSkip:

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-001
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_001_credentials_skip_returns_true(self):
        # Test ID: TC-UNIT-RPT-001
        # Test Title: 帳密未設定的 skip 訊息應回傳 True
        # Test Steps:
        #   1. 傳入包含 BEANFUN_ 與「缺少」的訊息字串
        #   2. 呼叫 _is_credentials_skip()
        # Expected Result: 回傳 True，該 skip 應被排除在統計之外
        assert _is_credentials_skip("缺少 BEANFUN_TEST_ACCOUNT，請設定環境變數") is True

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-002
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_002_normal_skip_returns_false(self):
        # Test ID: TC-UNIT-RPT-002
        # Test Title: 一般環境限制的 skip（如 CAPTCHA）應回傳 False
        # Test Steps:
        #   1. 傳入不含 BEANFUN_ 關鍵字的 skip 訊息
        #   2. 呼叫 _is_credentials_skip()
        # Expected Result: 回傳 False，該 skip 應正常計入 locked 統計
        assert _is_credentials_skip("被鎖定：429 Too Many Requests") is False


class TestParseReceiverList:

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-003
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_003_comma_separated(self):
        # Test ID: TC-UNIT-RPT-003
        # Test Title: 逗號分隔的收件人字串應正確解析為列表
        # Test Steps:
        #   1. 傳入逗號分隔的 email 字串
        #   2. 呼叫 _parse_receiver_list()
        # Expected Result: 回傳含兩個 email 的列表，無多餘空白
        result = _parse_receiver_list("a@test.com, b@test.com")
        assert result == ["a@test.com", "b@test.com"]

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-004
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_004_semicolon_separated(self):
        # Test ID: TC-UNIT-RPT-004
        # Test Title: 分號分隔（Windows 常見格式）應與逗號等效
        # Test Steps:
        #   1. 傳入分號分隔的 email 字串
        #   2. 呼叫 _parse_receiver_list()
        # Expected Result: 回傳含兩個 email 的列表
        result = _parse_receiver_list("a@test.com;b@test.com")
        assert result == ["a@test.com", "b@test.com"]


class TestMaskEmail:

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-005
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_005_normal_email_is_masked(self):
        # Test ID: TC-UNIT-RPT-005
        # Test Title: 正常 email 應保留首尾字元並遮罩中間
        # Test Steps:
        #   1. 傳入標準格式 email
        #   2. 呼叫 _mask_email()
        # Expected Result: local part 首尾保留，中間替換為 ***，domain 不變
        result = _mask_email("johndoe@example.com")
        assert result == "j***e@example.com"

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-006
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_006_invalid_email_returns_placeholder(self):
        # Test ID: TC-UNIT-RPT-006
        # Test Title: 無效 email（缺少 @）應回傳佔位字串
        # Test Steps:
        #   1. 傳入不含 @ 的字串
        #   2. 呼叫 _mask_email()
        # Expected Result: 回傳 "(無效或未設定)"
        result = _mask_email("not-an-email")
        assert result == "(無效或未設定)"


class TestGetDetailedReport:

    def _make_result(self, status, feature="登入功能", name="TC-001", steps=None):
        """建立符合 Allure JSON 格式的假測試結果。"""
        return {
            "name": name,
            "fullName": f"tests.test_login::{name}",
            "status": status,
            "labels": [{"name": "feature", "value": feature}],
            "steps": steps or [],
            "stop": 1000,
        }

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-007
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_007_passed_test_counted_correctly(self):
        # Test ID: TC-UNIT-RPT-007
        # Test Title: 一個 passed 測試應正確計入 summary
        # Test Steps:
        #   1. Mock glob.glob 回傳一個假路徑
        #   2. Mock open 回傳一個 passed 狀態的 Allure JSON
        #   3. 呼叫 get_detailed_report()
        # Expected Result: summary passed=1, failed=0, locked=0, 成功率 100%
        fake_json = json.dumps(self._make_result("passed"))

        with patch("glob.glob", return_value=["fake-result.json"]):
            with patch("builtins.open", mock_open(read_data=fake_json)):
                _, summary, rate = get_detailed_report("fake-dir")

        assert summary["passed"] == 1
        assert summary["failed"] == 0
        assert summary["locked"] == 0
        assert rate == 100.0

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-008
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_008_failed_test_counted_correctly(self):
        # Test ID: TC-UNIT-RPT-008
        # Test Title: 一個 failed 測試應正確計入 summary，成功率為 0%
        # Test Steps:
        #   1. Mock 回傳一個 failed 狀態的 Allure JSON
        #   2. 呼叫 get_detailed_report()
        # Expected Result: summary failed=1, 成功率 0%
        fake_json = json.dumps(self._make_result("failed"))

        with patch("glob.glob", return_value=["fake-result.json"]):
            with patch("builtins.open", mock_open(read_data=fake_json)):
                _, summary, rate = get_detailed_report("fake-dir")

        assert summary["failed"] == 1
        assert summary["passed"] == 0
        assert rate == 0.0

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-009
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_009_credentials_skip_excluded_from_summary(self):
        # Test ID: TC-UNIT-RPT-009
        # Test Title: 帳密未設定的 skip 應完全排除在統計與報告之外
        # Test Steps:
        #   1. Mock 回傳一個 skipped 狀態且訊息含 BEANFUN_/缺少 的 JSON
        #   2. 呼叫 get_detailed_report()
        # Expected Result: summary total=0，不計入任何欄位
        fake_data = self._make_result("skipped")
        fake_data["statusDetails"] = {"message": "缺少 BEANFUN_TEST_ACCOUNT，請設定環境變數"}
        fake_json = json.dumps(fake_data)

        with patch("glob.glob", return_value=["fake-result.json"]):
            with patch("builtins.open", mock_open(read_data=fake_json)):
                _, summary, _ = get_detailed_report("fake-dir")

        assert summary["total"] == 0

    # ────────────────────────────────────────────────────────────
    # TC-UNIT-RPT-010
    # ────────────────────────────────────────────────────────────
    def test_tc_unit_rpt_010_no_json_files_returns_warning(self):
        # Test ID: TC-UNIT-RPT-010
        # Test Title: allure-results 目錄無 JSON 時應回傳警告訊息
        # Test Steps:
        #   1. Mock glob.glob 回傳空列表（模擬 pytest 未執行）
        #   2. 呼叫 get_detailed_report()
        # Expected Result: 回傳含警告文字的字串，total=0
        with patch("glob.glob", return_value=[]):
            text, summary, rate = get_detailed_report("fake-dir")

        assert "找不到" in text
        assert summary["total"] == 0
        assert rate == 0


class TestPickLocalReportHtml:

    def test_prefers_complete_html_over_index(self):
        # complete.html（allure-combine 產生）優先於 index.html
        with patch("os.path.isfile", side_effect=lambda p: p.endswith("complete.html")):
            path, exists = _pick_local_report_html("/some/dir")
        assert path.endswith("complete.html")
        assert exists is True

    def test_falls_back_to_index_html(self):
        # 沒有 complete.html 時降級使用 index.html
        with patch("os.path.isfile", side_effect=lambda p: p.endswith("index.html")):
            path, exists = _pick_local_report_html("/some/dir")
        assert path.endswith("index.html")
        assert exists is True
