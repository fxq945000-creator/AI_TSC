#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI_TSC项目主程序入口
"""

import sys
import tkinter as tk

from src.script_analyzer import ScriptAnalyzerGUI


def main():
    """主函数"""
    print("欢迎使用短视频脚本分析工具！")
    print(f"Python版本: {sys.version}")
    
    # 创建主窗口
    root = tk.Tk()
    app = ScriptAnalyzerGUI(root)
    
    # 启动主循环
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())