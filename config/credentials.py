import os
from dotenv import load_dotenv

# 自動尋找並載入專案根目錄的 .env 檔案
load_dotenv()

def require_beanfun_credentials():
    """從 .env 讀取帳號與密碼"""
    account = os.getenv("BEANFUN_TEST_ACCOUNT")
    password = os.getenv("BEANFUN_TEST_PASSWORD")

    if not account or not password:
        raise ValueError("缺少帳號密碼！請確認 .env 檔案中有設定 BEANFUN_TEST_ACCOUNT 與 BEANFUN_TEST_PASSWORD")

    return account, password

def get_beanfun_otp():
    """從 .env 讀取 OTP 驗證碼 (如果有需要的話)"""
    return os.getenv("BEANFUN_TEST_OTP", "000000")

def get_pure_credentials():
    """純點帳（Yahoo，同視窗密碼流程）"""
    account = os.getenv("BEANFUN_PURE_ACCOUNT")
    password = os.getenv("BEANFUN_PURE_PASSWORD")
    if not account or not password:
        raise ValueError("缺少純點帳帳密，請設定 BEANFUN_PURE_ACCOUNT / BEANFUN_PURE_PASSWORD")
    return account, password

def get_gp_credentials():
    """GP點帳（有綁定 GamaPass，有雲端背包）。回傳 list，含備援帳號。"""
    account = os.getenv("BEANFUN_GP_ACCOUNT")
    password = os.getenv("BEANFUN_GP_PASSWORD")
    if not account or not password:
        raise ValueError("缺少 GP 帳密，請設定 BEANFUN_GP_ACCOUNT / BEANFUN_GP_PASSWORD")
    backup_account = os.getenv("BEANFUN_GP_BACKUP_ACCOUNT")
    backup_password = os.getenv("BEANFUN_GP_BACKUP_PASSWORD")
    candidates = [(account, password)]
    if backup_account and backup_password:
        candidates.append((backup_account, backup_password))
    return candidates

def get_star_credentials():
    """星帳（有雲端背包）"""
    account = os.getenv("BEANFUN_STAR_ACCOUNT")
    password = os.getenv("BEANFUN_STAR_PASSWORD")
    if not account or not password:
        raise ValueError("缺少星帳帳密，請設定 BEANFUN_STAR_ACCOUNT / BEANFUN_STAR_PASSWORD")
    return account, password
def get_bf_bound_credentials():
    """綁bf!點帳（尚未完成開通，需手機6碼OTP驗證）"""
    account = os.getenv("BEANFUN_BF_ACCOUNT")
    password = os.getenv("BEANFUN_BF_PASSWORD")
    if not account or not password:
        raise ValueError("缺少綁bf!帳密，請設定 BEANFUN_BF_ACCOUNT / BEANFUN_BF_PASSWORD")
    return account, password

def get_bf_bound_otp():
    """綁bf!點帳手機驗證碼（6碼）"""
    return os.getenv("BEANFUN_BF_OTP", "999999")

def get_gp_otp():
    """GP 點帳 beanfun SMS OTP（6碼，用於 OID-003）"""
    return os.getenv("BEANFUN_GP_OTP", "999999")

def get_gp_gamapass_otp():
    """GP 點帳 GamaPass OTP（4碼，用於 OID-004）"""
    return os.getenv("BEANFUN_GP_GAMAPASS_OTP", "9999")

def get_gp_phone():
    """GP 點帳綁定手機號（GamaPass 登入頁使用）"""
    phone = os.getenv("BEANFUN_GP_PHONE")
    if not phone:
        raise ValueError("缺少 GP 手機號，請設定 BEANFUN_GP_PHONE")
    return phone

def get_oid_gp_gamapass_credentials():
    """OID-004 專用 GamaPass 登入帳密（手機號 + 密碼，與 PC 測試帳號分離）。"""
    phone = os.getenv("OID_GP_GAMAPASS_PHONE")
    password = os.getenv("OID_GP_GAMAPASS_PASSWORD")
    if not phone or not password:
        raise ValueError("缺少 OID GamaPass 帳密，請設定 OID_GP_GAMAPASS_PHONE / OID_GP_GAMAPASS_PASSWORD")
    return phone, password

def get_oid_gp_credentials():
    """OID 專用 GP 點帳（lilia23060801，與 PC 測試帳號分離，用於 OID-003 / OID-004）。"""
    account = os.getenv("OID_GP_ACCOUNT")
    password = os.getenv("OID_GP_PASSWORD")
    if not account or not password:
        raise ValueError("缺少 OID GP 帳密，請設定 OID_GP_ACCOUNT / OID_GP_PASSWORD")
    return account, password

def get_oid_pure_verified_credentials():
    """OID 專用純點帳已綁手機（lilia26012001，與 PC 測試帳號分離，用於 OID-001）。"""
    account = os.getenv("OID_PURE_VERIFIED_ACCOUNT")
    password = os.getenv("OID_PURE_VERIFIED_PASSWORD")
    if not account or not password:
        raise ValueError("缺少 OID 純點帳帳密，請設定 OID_PURE_VERIFIED_ACCOUNT / OID_PURE_VERIFIED_PASSWORD")
    return account, password

def get_star_otp():
    """星帳 beanfun SMS OTP 驗證碼（6碼，用於 OID-005）"""
    return os.getenv("BEANFUN_STAR_OTP", "999999")

def get_openid_login_url():
    """OPEN ID 登入測試 URL（含 OTT，可能過期需更新）"""
    url = os.getenv("OPENID_LOGIN_URL")
    if not url:
        raise ValueError("缺少 OPEN ID URL，請設定 OPENID_LOGIN_URL")
    return url

def get_pure_verified_credentials():
    """純點帳已綁手機（認證會員），用於 SP-017。"""
    account = os.getenv("BEANFUN_PURE_VERIFIED_ACCOUNT")
    password = os.getenv("BEANFUN_PURE_VERIFIED_PASSWORD")
    if not account or not password:
        raise ValueError("缺少已綁手機純點帳帳密，請設定 BEANFUN_PURE_VERIFIED_ACCOUNT / BEANFUN_PURE_VERIFIED_PASSWORD")
    return account, password
