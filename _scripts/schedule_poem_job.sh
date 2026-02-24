#!/bin/bash
# 使用 launchd 调度每日一诗任务（macOS 系统）

cat <<EOF > ~/Library/LaunchAgents/com.jack.daily_poem.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jack.daily_poem</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/jack/Documents/Obsidian/AI_Vault/_scripts/daily_poem.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/jack/Documents/Obsidian/AI_Vault/logs/daily_poem.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jack/Documents/Obsidian/AI_Vault/logs/daily_poem_error.log</string>
</dict>
</plist>
EOF

# 加载并启动任务
launchctl load ~/Library/LaunchAgents/com.jack.daily_poem.plist
launchctl start com.jack.daily_poem

echo "每日一诗定时任务已成功创建并启动"
echo "任务会在每天早上8点自动执行"
echo "日志文件位于: /Users/jack/Documents/Obsidian/AI_Vault/logs/"