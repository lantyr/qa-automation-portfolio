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