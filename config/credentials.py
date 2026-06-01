import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass(frozen=True)
class Credentials:
    report_sender_email: str = os.getenv("REPORT_SENDER_EMAIL", "")
    report_sender_pwd: str = os.getenv("REPORT_SENDER_PWD", "")
    report_receiver_email: str = os.getenv("REPORT_RECEIVER_EMAIL", "")
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
    gdrive_folder_id: str = os.getenv("GDRIVE_FOLDER_ID", "")


credentials = Credentials()
