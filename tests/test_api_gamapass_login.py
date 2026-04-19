"""
API 測試：GamaPass 登入流程（api.accounts.gamania.com）。

GamaPass 登入分兩步：
  Step 1：POST /v1/verification/password  → 驗證帳密
  Step 2：POST /v1/login                  → 帶入 verificationToken 取得 accessToken

【重要：API 回應的業務設計】
- /v1/verification/password 永遠回傳 HTTP 200，用 body 的 isSuccess 欄位表示成敗。
  - 成功：isSuccess: true（若 isForce2FA: true 則需額外 OTP 流程才能取得 verificationToken）
  - 失敗：isSuccess: false + remainingTimes（剩餘嘗試次數）
- 這種設計稱為「業務錯誤走 HTTP 200，只用 HTTP 4xx/5xx 表示系統層錯誤」。
  與 dummyjson.com 直接回 400 的風格不同，屬於另一種常見的 API 設計模式。

【isForce2FA 說明】
測試帳號啟用了雙重驗證（isForce2FA: true），/v1/verification/password 成功後
需要再走 OTP 步驟才能取得 verificationToken。
TC-003 改為測試「帶入無效 verificationToken 直接呼叫 /v1/login」，
驗證後端對未授權請求的防護能力。

Base URL: https://api.accounts.gamania.com

Test ID 範圍：TC-API-GMS-001 ~ TC-API-GMS-004
  001 → Step 1 正確帳密驗證成功（isSuccess: true）
  002 → Step 1 錯誤密碼驗證失敗（isSuccess: false + remainingTimes）
  003 → Step 2 帶入無效 verificationToken，驗證後端拒絕
  004 → Step 1 空白 payload，驗證系統層錯誤處理（4xx）
"""
import os

import allure
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.accounts.gamania.com"

# ── 從 .env 讀取，測試啟動前就確認，少一個就明確報錯 ──────────────────────
_REQUIRED_ENV = [
    "GAMAPASS_TEST_PHONE",
    "GAMAPASS_TEST_COUNTRY_CODE",
    "GAMAPASS_TEST_PASSWORD",
    "GAMAPASS_APP_AUTH_TOKEN",
    "GAMAPASS_CLIENT_ID",
    "GAMAPASS_DEVICE_ID",
]
_missing = [k for k in _REQUIRED_ENV if not os.getenv(k)]
if _missing:
    pytest.exit(f"缺少必要環境變數，請確認 .env：{_missing}", returncode=1)

PHONE = os.getenv("GAMAPASS_TEST_PHONE")
COUNTRY_CODE = os.getenv("GAMAPASS_TEST_COUNTRY_CODE")
PASSWORD = os.getenv("GAMAPASS_TEST_PASSWORD")
DEVICE_ID = os.getenv("GAMAPASS_DEVICE_ID")

APP_HEADERS = {
    "authorization": os.getenv("GAMAPASS_APP_AUTH_TOKEN"),
    "x-client-id": os.getenv("GAMAPASS_CLIENT_ID"),
    "x-device-id": DEVICE_ID,
    "Content-Type": "application/json",
}


@allure.feature("GamaPass API 登入流程")
class TestGamaPassAPILogin:

    # ────────────────────────────────────────────────────────────
    # TC-API-GMS-001
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-API-GMS-001：Step 1 正確帳密驗證回傳 isSuccess: true")
    def test_tc_api_gms_001_verification_success(self):
        # Test ID: TC-API-GMS-001
        # Test Title: Step 1 正確帳密驗證回傳 isSuccess: true
        # Test Steps:
        #   1. 發送 POST /v1/verification/password，帶入正確手機號碼與密碼
        #   2. 驗證 HTTP 狀態碼為 200（此 API 永遠回傳 200）
        #   3. 驗證 body.isSuccess 為 true
        #   4. 驗證回應包含 phone 欄位（遮罩後的手機號碼）
        # Expected Result: 驗證成功，isSuccess: true，回應含遮罩 phone

        payload = {
            "phone": PHONE,
            "countryCode": COUNTRY_CODE,
            "deviceID": DEVICE_ID,
            "password": PASSWORD,
            "requestOrigin": 0,
            "checkForce2FA": True,
        }

        with allure.step("1. 發送 POST /v1/verification/password（正確帳密）"):
            response = requests.post(
                f"{BASE_URL}/v1/verification/password",
                json=payload,
                headers=APP_HEADERS,
            )

        with allure.step("2. 驗證狀態碼為 200"):
            assert response.status_code == 200, (
                f"預期 200，實際 {response.status_code}，回應：{response.text}"
            )

        with allure.step("3. 驗證 body.isSuccess 為 true"):
            body = response.json()
            assert "isSuccess" in body, f"回應中找不到 isSuccess 欄位：{body}"
            assert body["isSuccess"] is True, (
                f"預期 isSuccess: true，實際：{body}"
            )

        with allure.step("4. 驗證回應包含遮罩 phone 欄位"):
            assert "phone" in body, f"回應中找不到 phone 欄位：{body}"
            assert body["phone"], "phone 欄位不應為空"

    # ────────────────────────────────────────────────────────────
    # TC-API-GMS-002
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-API-GMS-002：Step 1 錯誤密碼回傳 isSuccess: false 及 remainingTimes")
    def test_tc_api_gms_002_verification_wrong_password(self):
        # Test ID: TC-API-GMS-002
        # Test Title: Step 1 錯誤密碼回傳 isSuccess: false 及 remainingTimes
        # Test Steps:
        #   1. 發送 POST /v1/verification/password，帶入錯誤密碼
        #   2. 驗證 HTTP 狀態碼仍為 200（業務錯誤不走 HTTP 4xx）
        #   3. 驗證 body.isSuccess 為 false
        #   4. 驗證回應包含 remainingTimes 欄位（剩餘嘗試次數）
        # Expected Result: 驗證失敗，HTTP 200 + isSuccess: false + remainingTimes
        #
        # 【設計觀察】此 API 用 HTTP 200 + isSuccess 欄位表達業務失敗，
        # 而非用 HTTP 4xx。測試 assertion 需依此設計調整，
        # 避免誤以為 200 代表「測試通過」。

        payload = {
            "phone": PHONE,
            "countryCode": COUNTRY_CODE,
            "deviceID": DEVICE_ID,
            "password": "WrongPassword999",
            "requestOrigin": 0,
            "checkForce2FA": True,
        }

        with allure.step("1. 發送 POST /v1/verification/password（錯誤密碼）"):
            response = requests.post(
                f"{BASE_URL}/v1/verification/password",
                json=payload,
                headers=APP_HEADERS,
            )

        with allure.step("2. 驗證狀態碼為 200（業務錯誤不走 HTTP 4xx）"):
            assert response.status_code == 200, (
                f"預期 200，實際 {response.status_code}，回應：{response.text}"
            )

        with allure.step("3. 驗證 body.isSuccess 為 false"):
            body = response.json()
            assert "isSuccess" in body, f"回應中找不到 isSuccess 欄位：{body}"
            assert body["isSuccess"] is False, (
                f"預期 isSuccess: false（密碼錯誤），實際：{body}"
            )

        with allure.step("4. 驗證回應包含 remainingTimes（剩餘嘗試次數）"):
            assert "remainingTimes" in body, (
                f"回應中找不到 remainingTimes 欄位：{body}"
            )
            assert isinstance(body["remainingTimes"], int), (
                f"remainingTimes 應為整數，實際：{body['remainingTimes']}"
            )

    # ────────────────────────────────────────────────────────────
    # TC-API-GMS-003
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-API-GMS-003：Step 2 帶入無效 verificationToken 後端應拒絕")
    def test_tc_api_gms_003_login_rejects_invalid_token(self):
        # Test ID: TC-API-GMS-003
        # Test Title: Step 2 帶入無效 verificationToken 後端應拒絕
        # Test Steps:
        #   1. 發送 POST /v1/login，帶入偽造的 verificationToken
        #   2. 驗證後端不允許此請求成功（HTTP 4xx 或 body.isSuccess: false）
        #   3. 驗證回應包含錯誤相關欄位
        # Expected Result: 後端拒絕無效 Token，不回傳 accessToken
        #
        # 【測試目的】驗證後端對 verificationToken 有實際驗證，
        # 避免繞過 Step 1 直接偽造 Token 登入。

        payload = {
            "phone": PHONE,
            "countryCode": COUNTRY_CODE,
            "password": PASSWORD,
            "deviceID": DEVICE_ID,
            "requestOrigin": 2,
            "rememberLoginStatus": False,
            "verificationToken": "invalid-token-00000000-0000-0000-0000-000000000000",
        }

        with allure.step("1. 發送 POST /v1/login（無效 verificationToken）"):
            response = requests.post(
                f"{BASE_URL}/v1/login",
                json=payload,
                headers=APP_HEADERS,
            )

        with allure.step("2. 驗證後端拒絕此請求"):
            body = response.json()
            # 此 API 可能回傳 4xx，或 200 + isSuccess: false
            is_rejected = (
                response.status_code >= 400
                or body.get("isSuccess") is False
            )
            assert is_rejected, (
                f"後端應拒絕無效 Token，實際狀態碼：{response.status_code}，回應：{body}"
            )

        with allure.step("3. 驗證回應不含 accessToken"):
            assert "accessToken" not in body, (
                f"無效 Token 不應取得 accessToken：{body}"
            )

    # ────────────────────────────────────────────────────────────
    # TC-API-GMS-004
    # ────────────────────────────────────────────────────────────
    @allure.title("TC-API-GMS-004：Step 1 空白 payload 驗證系統層錯誤")
    def test_tc_api_gms_004_verification_empty_payload(self):
        # Test ID: TC-API-GMS-004
        # Test Title: Step 1 空白 payload 驗證系統層錯誤
        # Test Steps:
        #   1. 發送 POST /v1/verification/password，不帶任何欄位
        #   2. 驗證 HTTP 狀態碼為 4xx（系統層驗證錯誤，不同於業務錯誤的 200）
        # Expected Result: 回傳 4xx，後端對缺少必要欄位有 schema 層保護

        with allure.step("1. 發送 POST /v1/verification/password（空白 payload）"):
            response = requests.post(
                f"{BASE_URL}/v1/verification/password",
                json={},
                headers=APP_HEADERS,
            )

        with allure.step("2. 驗證狀態碼為 4xx"):
            assert response.status_code >= 400, (
                f"空白 payload 應回傳 4xx，實際 {response.status_code}，回應：{response.text}"
            )
