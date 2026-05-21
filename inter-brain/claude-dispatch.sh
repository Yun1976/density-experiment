#!/bin/bash
# 观自在 - Claude Code 调度脚本
# 将任务分派给 Claude Code（右脑/系统维护）
# 用法: bash claude-dispatch.sh "任务描述" [priority]

set -e

WORK_DIR="D:/AI WORK"
INBOX_DIR="$WORK_DIR/inter-brain/inbox-claude"
OUTBOX_DIR="$WORK_DIR/inter-brain/outbox"
ARCHIVE_DIR="$WORK_DIR/inter-brain/archive"

# 参数检查
if [ -z "$1" ]; then
    echo "用法: bash claude-dispatch.sh \"任务描述\" [priority]"
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
  "to": "claude",
  "type": "code",
  "priority": "$PRIORITY",
  "status": "pending",
  "created": "$TIMESTAMP",
  "timeout": 600,
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

# 调用 Claude Code
echo "[INFO] 调用 Claude Code..."
if command -v claude &> /dev/null; then
    claude -p "$PROMPT" --workdir "$WORK_DIR" 2>&1
    RESULT=$?

    if [ $RESULT -eq 0 ]; then
        echo "[OK] Claude Code 任务完成"
    else
        echo "[ERROR] Claude Code 任务失败 (exit code: $RESULT)"
    fi

    # 移动到 archive
    mv "$TASK_FILE" "$ARCHIVE_DIR/$TASK_ID.json" 2>/dev/null || true
else
    echo "[ERROR] Claude Code 不可用"
    exit 1
fi
