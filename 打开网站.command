#!/bin/bash
# 双击这个文件就能在本机预览网站。关掉这个终端窗口就停止。
cd "$(dirname "$0")"
PORT=8899
# 端口被占就换一个
while lsof -i :$PORT >/dev/null 2>&1; do PORT=$((PORT+1)); done
echo ""
echo "  网站已启动：http://localhost:$PORT"
echo "  浏览器会自动打开。关掉这个窗口即停止。"
echo ""
( sleep 1; open "http://localhost:$PORT" ) &
python3 -m http.server $PORT
