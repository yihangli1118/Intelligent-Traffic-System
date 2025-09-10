@echo off
chcp 65001 > nul

echo 正在停用 Conda 环境...
call conda deactivate

echo 正在激活虚拟环境...
call .venv\Scripts\activate

echo 进入 src 目录...
cd /d src

echo 设置 QT 插件路径...
set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0.venv\Lib\site-packages\PyQt5\Qt5\plugins

echo 启动主程序...
python main.py

pause
