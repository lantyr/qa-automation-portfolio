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
    """GP點帳（有綁定 GamaPass，有雲端背包）"""
    account = os.getenv("BEANFUN_GP_ACCOUNT")
    password = os.getenv("BEANFUN_GP_PASSWORD")
    if not account or not password:
        raise ValueError("缺少 GP 帳密，請設定 BEANFUN_GP_ACCOUNT / BEANFUN_GP_PASSWORD")
    return account, password

def get_star_credentials():
    """星帳（有雲端背包）"""
    account = os.getenv("BEANFUN_STAR_ACCOUNT")
    password = os.getenv("BEANFUN_STAR_PASSWORD")
    if not account or not password:
        raise ValueError("缺少星帳帳密，請設定 BEANFUN_STAR_ACCOUNT / BEANFUN_STAR_PASSWORD")
    return account, password
def get_pure_verified_credentials():
    """純點帳已綁手機（認證會員），用於 SP-017。"""
    account = os.getenv("BEANFUN_PURE_VERIFIED_ACCOUNT")
    password = os.getenv("BEANFUN_PURE_VERIFIED_PASSWORD")
    if not account or not password:
        raise ValueError("缺少已綁手機純點帳帳密，請設定 BEANFUN_PURE_VERIFIED_ACCOUNT / BEANFUN_PURE_VERIFIED_PASSWORD")
    return account, password
