#!/bin/bash
# 每日一诗脚本

# 导航到脚本目录
cd /Users/jack/Documents/Obsidian/AI_Vault

# 运行 quotes.py 脚本并获取每日一诗
poem=$(python3 _scripts/quotes.py --poem)

# 发送通知
if command -v osascript &> /dev/null; then
    # macOS 通知
    osascript -e "display notification \"$poem\" with title \"每日一诗\""
else
    # 其他系统或备用方法
    echo "$poem"
fi