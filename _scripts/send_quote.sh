#!/bin/bash

# 脚本功能：获取一句随机名言、诗词、歌词或影视台词并发送到当前聊天

# 获取随机引用
QUOTE=$(python3 /Users/jack/Documents/Obsidian/AI_Vault/_scripts/quotes.py --random)

# 使用nanobot的message功能发送到当前聊天（Telegram）
python3 /Users/jack/Documents/Obsidian/AI_Vault/_scripts/message.py --content "${QUOTE}" --channel "telegram" --chat_id "6684292977"

echo "Quote sent successfully: ${QUOTE}"
