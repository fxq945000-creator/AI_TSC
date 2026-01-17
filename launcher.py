#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Video Script Analyzer Launcher
一键启动脚本
"""

import os
import sys
import subprocess
import time

def main():
    """主函数"""
    print("Starting AI Video Script Analyzer...")
    print(f"Python version: {sys.version}")
    print()
    
    # 获取当前脚本所在目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建main.py的路径
    main_script = os.path.join(project_dir, "main.py")
    
    # 使用正确的Python解释器路径
    python_exe = "C:/Users/Administrator/AppData/Local/Programs/Python/Python314/python.exe"
    
    try:
        # 启动主程序
        subprocess.run([python_exe, main_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the program: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Python interpreter not found at: {python_exe}")
        print("Please check the Python path in this script.")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
