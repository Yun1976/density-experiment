@echo off
chcp 65001 >nul
title NoteBase 信息价值评估器 微调训练
echo ============================================
echo   NoteBase · 信息存活价值评估器 · 微调训练
echo   (5060 Ti / Windows / 16GB)
echo ============================================
echo.
echo [1/4] 安装 PyTorch (CUDA 12.8 版, 支持Blackwell/5060Ti, 约3GB, 首次5-10分钟)...
pip install torch --index-url https://download.pytorch.org/whl/cu128
if errorlevel 1 echo [警告] PyTorch 安装可能有问题, 继续尝试...
echo.
echo [2/4] 安装其他依赖...
pip install -r requirements.txt
echo.
echo [3/4] 开始训练 (首次会下载模型约6GB + 训练5-15分钟)...
echo       期间黑窗滚动文字是正常的, 请耐心等待...
echo.
python train.py
echo.
echo ============================================
if exist output (
    echo ✓ 训练完成! 把 output 文件夹拷回 U 盘
    echo   (可选: 再运行 python predict.py 看考多少分)
) else (
    echo ✗ 训练似乎没完成, 请看上面的报错信息
)
echo ============================================
pause
