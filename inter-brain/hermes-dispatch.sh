#!/bin/bash
# 观自在 - Hermes 调度脚本
# 将任务分派给 Hermes Agent（右脑/深度思考）
# 用法: bash hermes-dispatch.sh "任务描述" [priority]

set -e

WORK_DIR="D:/AI WORK"
INBOX_DIR="$WORK_DIR/inter-brain/inbox-hermes"
OUTBOX_DIR="$WORK_DIR/inter-brain/outbox"
ARCHIVE_DIR="$WORK_DIR/inter-brain/archive"

# 参数检查
if [ -z "$1" ]; then
    echo "用法: bash hermes-dispatch.sh \"任务描述\" [priority]"
    echo "  priority: critical|high|normal|low (默认 normal)"
    exit 1
fi

PROMPT="$1"
PRIORITY="${2:-normal}"
TASK_ID="ib-$(date +%Y%m%d-%H%M%S)-$$"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# 创建任务文件
TASK_FILE="$INBOX_DIR/$TASK_ID.json"
cat > "$TASK_FILE" << EOF
{
  "id": "$TASK_ID",
  "from": "openclaw",
  "to": "hermes",
  "type": "think",
  "priority": "$PRIORITY",
  "status": "pending",
  "created": "$TIMESTAMP",
  "timeout": 300,
  "payload": {
    "prompt": "$PROMPT"
  },
  "result": null
}
EOF

echo "[OK] 任务已创建: $TASK_ID"
echo "  文件: $TASK_FILE"
echo "  优先级: $PRIORITY"
echo ""

# 尝试直接调用 Hermes
echo "[INFO] 尝试直接调用 Hermes..."
export PATH="$PATH:/c/Users/user/AppData/Roaming/Python/Python314/Scripts"

if command -v hermes &> /dev/null; then
    echo "[INFO] Hermes 可用，执行任务..."
    hermes --yolo --accept-hooks -z "$PROMPT" 2>&1
    RESULT=$?

    if [ $RESULT -eq 0 ]; then
        # 更新任务状态为完成
        STATUS="done"
        echo "[OK] Hermes 任务完成"
    else
        STATUS="failed"
        echo "[ERROR] Hermes 任务失败 (exit code: $RESULT)"
    fi

    # 移动到 archive
    mv "$TASK_FILE" "$ARCHIVE_DIR/$TASK_ID.json" 2>/dev/null || true
else
    echo "[WARN] Hermes 不可用，任务已放入队列等待处理"
    echo "  任务将由 OpenClaw 在下次调度时处理（降级模式）"
fi
