"""
執行一次：python gdrive_auth.py
會開啟瀏覽器讓你登入 Google，授權後自動儲存 token 到 credentials/gdrive_token.json。
之後排程腳本自動用這個 token，不需要再登入。
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CLIENT_SECRET = "credentials/client_secret_551167974925-5gvkfcu1qfl7hdp7t67o8k18ni8jdtca.apps.googleusercontent.com.json"
TOKEN_PATH = "credentials/gdrive_token.json"

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
creds = flow.run_local_server(port=0)

with open(TOKEN_PATH, "w") as f:
    f.write(creds.to_json())

print(f"授權完成，token 已儲存：{TOKEN_PATH}")
