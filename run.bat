@echo off
chcp 65001 >nul

echo 正在激活Python虚拟环境...
call conda deactivate
call .venv\Scripts\activate

echo 切换到src目录...
cd ./src

echo 设置QT环境变量...
set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0.venv\Lib\site-packages\PyQt5\Qt5\plugins

echo 启动主程序...
python main.py

exit