"""
One-time Google Drive OAuth2 authorisation flow.

Reads credentials from client_secret.json (downloaded from Google Cloud Console)
and writes token.json to the project root for subsequent use by send_report.py.

Usage:
    python utils/report/gdrive_auth.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CLIENT_SECRET = ROOT / "client_secret.json"
TOKEN_FILE = ROOT / "token.json"


def main() -> None:
    if not CLIENT_SECRET.exists():
        print(
            f"[gdrive_auth] client_secret.json not found at {CLIENT_SECRET}\n"
            "Download it from Google Cloud Console → APIs & Services → Credentials."
        )
        return

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"[gdrive_auth] Token saved → {TOKEN_FILE}")


if __name__ == "__main__":
    main()
