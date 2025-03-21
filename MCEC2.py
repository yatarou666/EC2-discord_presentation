import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")

url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"

headers = {
    "Authorization": f"Bot {DISCORD_TOKEN}",
    "Content-Type": "application/json"
}

# /start コマンド（オプション: インスタンスタイプ）
start_command = {
    "name": "start",
    "description": "EC2インスタンスを起動",
    "options": [
        {
            "name": "type",
            "description": "インスタンスタイプを選択（デフォルトsmall）",
            "type": 3,  # STRING
            "required": False,
            "choices": [
                {"name": "small", "value": "t4g.small"},
                {"name": "medium", "value": "t4g.medium"},
                {"name": "large", "value": "t4g.large"}
            ]
        }
    ]
}

# /stop コマンド
stop_command = {
    "name": "stop",
    "description": "EC2インスタンスを停止",
    "options": [
        {
            "name": "backup",
            "description": "backupの作成（デフォルトoff）",
            "type": 3,  # STRING
            "required": False,
            "choices": [
                {"name": "on", "value": "on"},
                {"name": "off", "value": "off"},
            ]
        }
    ]
}

# /status コマンド
status_command = {
    "name": "status",
    "description": "EC2インスタンスの状態を確認"
}

# コマンドを登録
for cmd in [start_command, stop_command, status_command]:
    r = requests.post(url, headers=headers, json=cmd)
    print(f"{cmd['name']} status: {r.status_code} {r.text}")
