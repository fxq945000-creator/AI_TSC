#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
短视频脚本分析工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import requests
import os
import json
from dotenv import load_dotenv
import threading
import webbrowser
import time

class CustomErrorDialog:
    """自定义错误对话框，支持复制错误信息"""
    def __init__(self, parent, title, message):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 错误信息文本框
        ttk.Label(main_frame, text="错误信息:").pack(anchor=tk.W, pady=(0, 5))
        
        self.text_frame = ttk.Frame(main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.error_text = tk.Text(self.text_frame, wrap=tk.WORD, height=10)
        self.error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.text_frame, command=self.error_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_text.config(yscrollcommand=scrollbar.set)
        
        # 插入错误信息
        self.error_text.insert(1.0, message)
        self.error_text.config(state=tk.NORMAL)  # 设置为可编辑，方便复制
        self.error_text.focus_set()
        
        # 全选文本
        self.error_text.tag_add(tk.SEL, "1.0", tk.END)
        self.error_text.mark_set(tk.INSERT, "1.0")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 关闭按钮
        self.close_button = ttk.Button(button_frame, text="关闭", command=self.dialog.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)
        
        # 复制按钮
        self.copy_button = ttk.Button(button_frame, text="复制", command=self.copy_error)
        self.copy_button.pack(side=tk.RIGHT, padx=5)
        
    def copy_error(self):
        """复制错误信息到剪贴板"""
        self.error_text.clipboard_clear()
        self.error_text.clipboard_append(self.error_text.get(1.0, tk.END).strip())
        # 可以添加一个临时提示
        self.dialog.bell()

class ConfigDialog:
    """API配置对话框"""
    def __init__(self, parent, api_key_var, api_url_var, model_var):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("API配置")
        self.dialog.geometry("600x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 配置变量
        self.api_key_var = api_key_var
        self.api_url_var = api_url_var
        self.model_var = model_var
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API密钥
        ttk.Label(main_frame, text="API密钥: ").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(main_frame, textvariable=api_key_var, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 显示/隐藏API密钥按钮
        self.show_key_var = tk.BooleanVar(value=False)
        self.toggle_key_button = ttk.Checkbutton(main_frame, text="显示密钥", variable=self.show_key_var, command=self.toggle_api_key)
        self.toggle_key_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # API URL
        ttk.Label(main_frame, text="API URL: ").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_url_entry = ttk.Entry(main_frame, textvariable=api_url_var)
        self.api_url_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # API帮助按钮
        self.help_button = ttk.Button(main_frame, text="?", width=3, command=self.show_api_help)
        self.help_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # 模型选择
        ttk.Label(main_frame, text="模型: ").grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.model_combobox = ttk.Combobox(main_frame, textvariable=model_var,
                                          values=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", 
                                                  "gemini-3-pro", "gemini-3-flash"])
        self.model_combobox.grid(row=1, column=4, sticky=tk.EW, padx=5, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=5, pady=10)
        
        # 重置默认按钮
        self.reset_button = ttk.Button(button_frame, text="重置默认", command=self.reset_defaults)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        self.save_button = ttk.Button(button_frame, text="保存", command=self.save_config)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.dialog.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 框架列权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(4, weight=1)
    
    def show_api_help(self):
        """显示API配置帮助"""
        help_text = """API配置说明：
1. OpenAI模型（gpt-*）：
   URL: https://api.openai.com/v1/chat/completions
   示例模型：gpt-3.5-turbo, gpt-4, gpt-4o
   
2. Google Gemini模型（gemini-*）：
   URL格式：https://generativelanguage.googleapis.com/v1beta/models/模型名称:generateContent
   示例：https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent
   支持模型：gemini-3-pro, gemini-3-flash
   
3. 第三方平台API（如"贞贞的AI工坊"等）：
   基础URL示例：https://ai.t8star.cn 或 https://api.comfly.chat
   系统会自动添加端点：/v1/chat/completions
   最终URL：https://ai.t8star.cn/v1/chat/completions
   支持模型：根据平台提供的模型列表选择

提示词说明：
默认提示词用于指导AI将剧本转化为分镜脚本，您可以自定义提示词来调整分镜生成的要求和格式。

提示词模板中的{script}会被实际的剧本内容替换。
   
注意事项：
- 确保API密钥与选择的模型和平台对应
- 第三方平台通常使用与OpenAI兼容的格式
- 如果遇到问题，请检查API密钥和模型名称是否正确
- 部分平台可能需要特殊配置，请参考平台文档"""
        messagebox.showinfo("API帮助", help_text)
        
    def toggle_api_key(self):
        """切换API密钥的显示/隐藏"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
            self.toggle_key_button.config(text="隐藏密钥")
        else:
            self.api_key_entry.config(show="*")
            self.toggle_key_button.config(text="显示密钥")
            
    def reset_defaults(self):
        """重置默认配置"""
        # 重置为OpenAI默认配置
        self.api_url_var.set("https://api.openai.com/v1/chat/completions")
        self.model_var.set("gpt-3.5-turbo")
        
        # 显示使用说明
        help_text = """API配置说明：
1. OpenAI模型（gpt-*）：
   URL: https://api.openai.com/v1/chat/completions
   示例模型：gpt-3.5-turbo, gpt-4, gpt-4o
   
2. Google Gemini模型（gemini-*）：
   URL格式：https://generativelanguage.googleapis.com/v1beta/models/模型名称:generateContent
   示例：https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent
   支持模型：gemini-3-pro, gemini-3-flash
   
3. 第三方平台API（如"贞贞的AI工坊"等）：
   基础URL示例：https://ai.t8star.cn 或 https://api.comfly.chat
   系统会自动添加端点：/v1/chat/completions
   最终URL：https://ai.t8star.cn/v1/chat/completions
   支持模型：根据平台提供的模型列表选择
   
提示词说明：
系统默认使用分镜生成提示词，会将您输入的剧本转化为包含场景、镜头号、角度、内容等详细信息的分镜脚本。
您可以在"提示词配置"中自定义生成要求。
   
注意事项：
- 确保API密钥与选择的模型和平台对应
- 第三方平台通常使用与OpenAI兼容的格式
- 如果遇到问题，请检查API密钥和模型名称是否正确
- 部分平台可能需要特殊配置，请参考平台文档"""
        messagebox.showinfo("配置说明", help_text)
            
    def save_config(self):
        """保存配置并关闭对话框"""
        self.dialog.destroy()


class SplitConfigDialog:
    """分解词配置对话框"""
    def __init__(self, parent, separators, bulk_add_func, prefix_var, suffix_var, add_number_var):
        self.parent = parent
        self.separators = separators
        self.bulk_add_func = bulk_add_func
        self.prefix_var = prefix_var
        self.suffix_var = suffix_var
        self.add_number_var = add_number_var
        
        # 添加中文数字选择变量
        self.use_chinese_numbers_var = tk.BooleanVar(value=False)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("分解词配置")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 一键添加功能区域
        bulk_frame = ttk.LabelFrame(main_frame, text="一键添加分解词", padding="10")
        bulk_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bulk_frame, text="前缀: ").pack(side=tk.LEFT, padx=5)
        self.prefix_entry = ttk.Entry(bulk_frame, textvariable=self.prefix_var, width=10)
        self.prefix_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(bulk_frame, text="后缀: ").pack(side=tk.LEFT, padx=5)
        self.suffix_entry = ttk.Entry(bulk_frame, textvariable=self.suffix_var, width=10)
        self.suffix_entry.pack(side=tk.LEFT, padx=5)
        
        self.add_number_check = ttk.Checkbutton(bulk_frame, text="添加数字", variable=self.add_number_var)
        self.add_number_check.pack(side=tk.LEFT, padx=5)
        
        # 添加中文数字选择框
        self.use_chinese_numbers_check = ttk.Checkbutton(bulk_frame, text="使用中文数字", variable=self.use_chinese_numbers_var)
        self.use_chinese_numbers_check.pack(side=tk.LEFT, padx=5)
        
        self.bulk_add_button = ttk.Button(bulk_frame, text="一键添加", command=self.bulk_add)
        self.bulk_add_button.pack(side=tk.LEFT, padx=5)
        
        # 分解词配置区域
        separator_frame = ttk.LabelFrame(main_frame, text="分解词配置", padding="10")
        separator_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建滚动区域
        scroll_frame = ttk.Frame(separator_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建8个分解词输入框
        self.separator_entries = []
        for i in range(8):
            # 标签
            ttk.Label(scrollable_frame, text=f"分解词 {i+1}: ").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            
            # 输入框
            entry = ttk.Entry(scrollable_frame, textvariable=self.separators[i], width=50)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            self.separator_entries.append(entry)
        
        # 设置列权重
        scrollable_frame.columnconfigure(1, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 保存按钮
        self.save_button = ttk.Button(button_frame, text="保存", command=self.save_config)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.dialog.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def bulk_add(self):
        """调用父窗口的一键添加功能"""
        use_chinese = self.use_chinese_numbers_var.get()
        self.bulk_add_func(use_chinese)
    
    def save_config(self):
        """保存配置并关闭对话框"""
        self.dialog.destroy()


class ScriptAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("短视频脚本分析工具")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 配置深色主题
        self.configure_dark_mode()
        
        # 加载环境变量
        load_dotenv()
        
        # API配置
        self.api_key = tk.StringVar(value=os.getenv("API_KEY", ""))
        self.api_url = tk.StringVar(value=os.getenv("API_URL", "https://ai.t8star.cn"))
        self.model = tk.StringVar(value=os.getenv("MODEL", "gpt-3.5-turbo"))
        
        # 提示词配置 (移除 {script} 占位符)
        self.prompt = tk.StringVar(value=os.getenv("PROMPT", """
请根据剧本内容，生成详细的电影分镜脚本。

要求：
1. 分镜需包含场景、镜头号、镜头角度、画面内容、台词、时长等关键信息
2. 分镜设计要考虑镜头语言和叙事节奏
3. 格式清晰，易于阅读和理解
"""))
        
        # 移除菜单栏，改为使用工具架
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        self.title_label = ttk.Label(self.main_frame, text="短视频脚本分析工具", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # 创建工具架（标签页控件）
        self.tool_frame = ttk.Notebook(self.main_frame)
        self.tool_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        
        # 创建配置标签页
        self.config_tab = ttk.Frame(self.tool_frame)
        self.tool_frame.add(self.config_tab, text="配置")
        
        # 添加API按钮
        self.api_button = ttk.Button(self.config_tab, text="API配置", command=self.show_api_config)
        self.api_button.grid(row=0, column=0, padx=10, pady=10)
        
        # 添加提示词按钮
        self.prompt_button = ttk.Button(self.config_tab, text="提示词配置", command=self.show_prompt_config)
        self.prompt_button.grid(row=0, column=1, padx=10, pady=10)
        
        # 移除多余的配置说明文字
        
        # 创建帮助标签页
        self.help_tab = ttk.Frame(self.tool_frame)
        self.tool_frame.add(self.help_tab, text="帮助")
        
        # 帮助按钮框架
        self.help_button_frame = ttk.Frame(self.help_tab)
        self.help_button_frame.pack(fill=tk.X, pady=10)
        
        # 添加帮助按钮
        self.help_button = ttk.Button(self.help_button_frame, text="使用帮助", command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 添加关于按钮
        self.about_button = ttk.Button(self.help_button_frame, text="关于", command=self.show_about)
        self.about_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 添加退出按钮
        self.exit_button = ttk.Button(self.help_button_frame, text="退出", command=self.root.quit)
        self.exit_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 创建全局滚动区域
        self.canvas_frame_container = ttk.Frame(self.main_frame)
        self.canvas_frame_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame_container, background='#2b2b2b', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定全局鼠标滚轮
        self.bind_mouse_wheel(self.root)
        
        # 创建主垂直分割窗口（调节上下高度）
        self.main_paned = ttk.PanedWindow(self.scrollable_frame, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建顶部水平分割窗口（调节左右宽度）
        self.top_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.top_paned, weight=1)
        
        # 左侧：剧本输入
        self.script_frame = ttk.LabelFrame(self.top_paned, text="剧本内容", padding="10")
        self.top_paned.add(self.script_frame, weight=1)
        
        # 脚本区域按钮
        self.script_button_frame = ttk.Frame(self.script_frame)
        self.script_button_frame.pack(fill=tk.X, pady=5)
        
        # 上传剧本按钮
        self.upload_button = ttk.Button(self.script_button_frame, text="上传剧本", command=self.upload_file)
        self.upload_button.pack(side=tk.LEFT, padx=2)
        
        # 分析剧本按钮
        self.analyze_button = ttk.Button(self.script_button_frame, text="分析剧本", command=self.start_analysis)
        self.analyze_button.pack(side=tk.LEFT, padx=2)
        
        # 清空剧本按钮
        self.clear_button = ttk.Button(self.script_button_frame, text="清空剧本", command=self.clear_content)
        self.clear_button.pack(side=tk.LEFT, padx=2)
        
        # 剧本文本框
        self.script_scrollbar = ttk.Scrollbar(self.script_frame)
        self.script_text = tk.Text(self.script_frame, wrap=tk.WORD, yscrollcommand=self.script_scrollbar.set, height=15,
                                  bg='#1e1e1e', fg='#ffffff', insertbackground='white')
        self.script_scrollbar.config(command=self.script_text.yview)
        self.script_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.script_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 中间：分析结果
        self.result_frame = ttk.LabelFrame(self.top_paned, text="分析结果", padding="10")
        self.top_paned.add(self.result_frame, weight=1)
        
        # 分析结果区域按钮
        self.result_button_frame = ttk.Frame(self.result_frame)
        self.result_button_frame.pack(fill=tk.X, pady=5)
        
        # 保存结果按钮
        self.save_button = ttk.Button(self.result_button_frame, text="保存结果", command=self.save_result)
        self.save_button.pack(side=tk.LEFT, padx=2)
        
        # 结果文本框
        self.result_scrollbar = ttk.Scrollbar(self.result_frame)
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, yscrollcommand=self.result_scrollbar.set, state=tk.DISABLED, height=15,
                                  bg='#1e1e1e', fg='#ffffff', insertbackground='white')
        self.result_scrollbar.config(command=self.result_text.yview)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 底部：结果分析拆分
        self.split_frame = ttk.LabelFrame(self.main_paned, text="结果分析拆分", padding="10")
        self.main_paned.add(self.split_frame, weight=1)
        
        # 创建分解词配置区域（简化版）
        self.separator_config_frame = ttk.Frame(self.split_frame)
        self.separator_config_frame.pack(fill=tk.X, pady=5)
        
        # 分析结果按钮
        self.analyze_result_button = ttk.Button(self.separator_config_frame, text="分析结果", command=self.analyze_result)
        self.analyze_result_button.pack(fill=tk.X, padx=5, pady=2)
        
        # 结果拆分选项
        self.split_options_button = ttk.Button(self.separator_config_frame, text="分解词配置", command=self.show_split_options)
        self.split_options_button.pack(fill=tk.X, padx=5, pady=2)
        
        # 创建网格排列的8个结果输出框
        self.result_output_frame = ttk.Frame(self.split_frame)
        self.result_output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 配置列权重，使两列等宽
        self.result_output_frame.columnconfigure(0, weight=1)
        self.result_output_frame.columnconfigure(1, weight=1)
        
        self.result_outputs = []
        self.result_texts = []
        
        for i in range(8):
            # 计算行和列 (2列布局)
            row = i // 2
            col = i % 2
            
            # 创建输出框框架
            output_frame = ttk.LabelFrame(self.result_output_frame, text=f"结果 {i+1}", padding="5")
            output_frame.grid(row=row, column=col, sticky=tk.NSEW, padx=3, pady=3)
            
            # 工具栏（保存按钮）
            toolbar_frame = ttk.Frame(output_frame)
            toolbar_frame.pack(fill=tk.X, pady=(0, 2))
            
            # 这里的 i 是循环变量，在lambda中需要捕获
            save_btn = ttk.Button(toolbar_frame, text="保存", width=6, command=lambda idx=i: self.save_single_split_result(idx))
            save_btn.pack(side=tk.RIGHT)
            
            # 创建文本框
            scrollbar = ttk.Scrollbar(output_frame)
            text_widget = tk.Text(output_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=8,
                                 bg='#1e1e1e', fg='#ffffff', insertbackground='white')
            scrollbar.config(command=text_widget.yview)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 设置文本框为只读
            text_widget.config(state=tk.DISABLED)
            
            self.result_outputs.append(output_frame)
            self.result_texts.append(text_widget)
        
        # 添加底部Padding，防止内容被遮挡
        ttk.Frame(self.split_frame, height=20).pack(fill=tk.X)
        
    def configure_dark_mode(self):
        """配置深色主题"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题作为基础，更容易自定义颜色
        
        # 定义颜色
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_bg = '#404040'
        active_bg = '#3c3f41'
        
        # 配置根窗口背景
        self.root.configure(bg=bg_color)
        
        # 配置通用样式
        style.configure('.', 
                        background=bg_color, 
                        foreground=fg_color,
                        fieldbackground='#1e1e1e',
                        darkcolor=bg_color,
                        lightcolor=bg_color,
                        troughcolor=bg_color,
                        selectbackground=select_bg,
                        selectforeground=fg_color)
        
        # 配置特定控件样式
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background='#3c3f41', foreground=fg_color, borderwidth=1)
        style.map('TButton',
                 background=[('active', '#505050'), ('pressed', '#606060')],
                 foreground=[('active', '#ffffff')])
        
        style.configure('TEntry', fieldbackground='#1e1e1e', foreground=fg_color, insertcolor='white')
        style.configure('TCombobox', fieldbackground='#1e1e1e', foreground=fg_color, arrowcolor='white')
        
        # 配置LabelFrame
        style.configure('TLabelframe', background=bg_color, foreground=fg_color, bordercolor='#505050')
        style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
        
        # 配置Notebook
        style.configure('TNotebook', background=bg_color, tabposition='n')
        style.configure('TNotebook.Tab', background='#3c3f41', foreground=fg_color, padding=[10, 2])
        style.map('TNotebook.Tab',
                 background=[('selected', '#505050')],
                 foreground=[('selected', '#ffffff')])
        
        # 配置PanedWindow
        style.configure('TPanedwindow', background=bg_color)
        style.configure('Sash', sashthickness=5, background='#505050', handlecolor='white')
        
    def upload_file(self):
        """上传脚本文件"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                title="选择脚本文件"
            )
            if file_path:
                self.status_var.set(f"正在打开文件: {file_path}")
                # 先测试文件是否存在
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"文件不存在: {file_path}")
                
                # 测试文件权限
                if not os.access(file_path, os.R_OK):
                    raise PermissionError(f"没有读取权限: {file_path}")
                
                # 尝试使用不同编码打开文件
                encodings = ['utf-8', 'gbk', 'gb2312', 'ascii']
                content = None
                used_encoding = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            content = f.read()
                        used_encoding = encoding
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise UnicodeDecodeError("无法解析文件编码", b"", 0, 0, "所有尝试的编码都失败")
                
                # 确保文本框可编辑
                self.script_text.config(state=tk.NORMAL)
                self.script_text.delete(1.0, tk.END)
                self.script_text.insert(1.0, content)
                # 滚动到顶部
                self.script_text.see(1.0)
                # 强制更新UI
                self.script_text.update_idletasks()
                
                self.status_var.set(f"已加载文件: {os.path.basename(file_path)} (编码: {used_encoding})")
        except Exception as e:
            CustomErrorDialog(self.parent, "错误", f"无法打开文件: {str(e)}")
            self.status_var.set(f"打开文件失败: {str(e)}")
            print(f"文件打开错误详情: {type(e).__name__}: {str(e)}")
            self.status_var.set("就绪")
    
    def start_analysis(self):
        """开始分析脚本"""
        script = self.script_text.get(1.0, tk.END).strip()
        if not script:
            messagebox.showwarning("警告", "请输入或上传脚本内容")
            return
        
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "请输入API密钥")
            return
        
        prompt = self.prompt.get().strip()
        if not prompt:
            messagebox.showwarning("警告", "请输入分析提示词")
            return
        
        # 禁用分析按钮
        self.analyze_button.config(state=tk.DISABLED)
        self.status_var.set("正在分析，请稍候...")
        
        # 在新线程中执行API调用
        threading.Thread(target=self.call_api, args=(script, prompt), daemon=True).start()
    
    def call_api(self, script, prompt):
        """调用API进行脚本分析"""
        try:
            # 添加详细调试日志
            print(f"\n=== 调试信息开始 ===")
            print(f"原始提示词完整内容: {repr(prompt)}")  # 使用repr显示所有特殊字符
            print(f"提示词中是否包含{{script}}占位符: {'{script}' in prompt}")
            print(f"脚本内容长度: {len(script)} 字符")
            
            # 构建完整提示词
            # 如果提示词中包含 {script} 占位符，则替换
            # 如果不包含，则将剧本内容附加到提示词后面
            if '{script}' in prompt:
                full_prompt = prompt.replace("{script}", script)
                print("已替换{script}占位符")
            else:
                full_prompt = f"{prompt}\n\n剧本内容：\n{script}"
                print("未找到占位符，已将剧本内容附加到末尾")
                
            print(f"替换后完整提示词长度: {len(full_prompt)} 字符")
            print(f"完整提示词预览: {full_prompt[:100]}...")
            
            current_model = self.model.get()
            api_url = self.api_url.get()
            api_key = self.api_key.get()

            
            print(f"当前模型: {current_model}")
            print(f"API URL: {api_url}")
            
            # 通用请求头
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 检查API URL是否包含必要的端点路径
            # 常见的API端点路径
            common_endpoints = [
                "/v1/chat/completions",
                "/chat/completions",
                "/api/chat/completions",
                "/v1/chatgpt/completions",
                "/api/v1/chat/completions"
            ]
            
            # 检查API URL是否已经包含常见端点
            url_has_endpoint = any(endpoint in api_url for endpoint in common_endpoints)
            
            # 如果API URL看起来像基础URL（没有端点），尝试添加合适的端点
            final_api_url = api_url
            if not url_has_endpoint:
                # 对于特定平台的特殊处理
                if "api.comfly.chat" in api_url or "anyroutes.cn" in api_url or "ai.t8star.cn" in api_url:
                    # "贞贞的AI工坊"等平台通常使用/v1/chat/completions端点
                    final_api_url = f"{api_url.rstrip('/')}/v1/chat/completions"
                elif "openai" in api_url.lower():
                    # OpenAI官方API
                    final_api_url = f"{api_url.rstrip('/')}/v1/chat/completions"
                elif current_model.startswith("gemini-"):
                    # Google Gemini API使用特定端点
                    if "/models/" not in api_url and "/generateContent" not in api_url:
                        final_api_url = f"{api_url.rstrip('/')}/generateContent"
            
            # 根据API URL或模型类型判断使用哪种请求格式
            # 支持常见的第三方平台API格式
            payload = None
            
            # 检查是否是Gemini API
            if current_model.startswith("gemini-"):
                # Google Gemini API格式
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": "你是一个专业的电影/短视频分镜脚本专家，擅长将文字剧本转化为详细的分镜脚本"},
                                {"text": full_prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 3000
                    }
                }
            # 检查是否是OpenAI兼容API（包括大多数第三方平台）
            elif "openai" in final_api_url.lower() or "chat/completions" in final_api_url.lower() or "api.comfly.chat" in final_api_url or "anyroutes.cn" in final_api_url or "ai.t8star.cn" in final_api_url:
                # OpenAI标准格式（适用于大多数第三方平台）
                payload = {
                    "model": current_model,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的电影/短视频分镜脚本专家，擅长将文字剧本转化为详细的分镜脚本"},
                        {"role": "user", "content": full_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                }
            else:
                # 默认使用OpenAI兼容格式（大多数第三方平台支持）
                payload = {
                    "model": current_model,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的电影/短视频分镜脚本专家，擅长将文字剧本转化为详细的分镜脚本"},
                        {"role": "user", "content": full_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000
                }
            
            # 输出最终API URL和请求体信息
            print(f"最终API URL: {final_api_url}")
            print(f"请求头包含Authorization: {'Bearer ' in str(headers)}")
            print(f"请求体类型: {type(payload)}")
            print(f"请求体预览: {json.dumps(payload, ensure_ascii=False)[:200]}...")
            
            # 发送API请求（添加重试机制）
            max_retries = 3
            retry_delay = 5  # 重试间隔秒数
            timeout = 60  # 增加超时时间到60秒
            response = None
            
            for retry in range(max_retries):
                try:
                    print(f"正在发送API请求 (尝试 {retry+1}/{max_retries})...")
                    response = requests.post(final_api_url, headers=headers, json=payload, timeout=timeout)
                    print(f"API响应状态码: {response.status_code}")
                    print(f"API响应头: {dict(response.headers)}")
                    
                    response.raise_for_status()
                    break  # 成功获取响应，跳出循环
                except requests.exceptions.Timeout:
                    print(f"API请求超时 (尝试 {retry+1}/{max_retries})，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    if retry == max_retries - 1:  # 最后一次尝试失败
                        raise ValueError(f"API请求超时，已尝试{max_retries}次，请检查网络连接或稍后重试")
                except Exception as e:
                    print(f"API请求错误 (尝试 {retry+1}/{max_retries}): {str(e)}")
                    if retry == max_retries - 1:  # 最后一次尝试失败
                        raise
            
            # 获取并检查响应内容
            response_content = response.text.strip()
            print(f"API响应内容长度: {len(response_content)} 字符")
            print(f"API响应内容预览: {response_content[:200]}...")
            
            if not response_content:
                raise ValueError("API返回了空响应")
            
            # 解析响应内容
            try:
                result = response.json()
                print(f"JSON解析成功: {json.dumps(result, ensure_ascii=False)[:200]}...")
                
                # 尝试多种响应格式解析
                analysis = None
                
                # 1. OpenAI格式
                try:
                    analysis = result["choices"][0]["message"]["content"]
                except KeyError:
                    pass
                
                # 2. Gemini格式
                if analysis is None:
                    try:
                        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
                    except KeyError:
                        pass
                
                # 3. 第三方平台可能的简化格式
                if analysis is None:
                    try:
                        analysis = result["data"]["content"]
                    except KeyError:
                        pass
                
                # 4. 直接内容格式
                if analysis is None:
                    try:
                        analysis = result["content"]
                    except KeyError:
                        pass
                
                # 5. 其他可能的格式
                if analysis is None:
                    try:
                        analysis = result["result"]
                    except KeyError:
                        pass
                
                # 如果还是无法解析，尝试直接返回响应内容或给出更详细的错误信息
                if analysis is None:
                    raise ValueError(f"无法解析API响应格式\n原始响应:\n{json.dumps(result, indent=2)}")
                    
            except json.JSONDecodeError as e:
                raise ValueError(f"API返回的不是有效的JSON格式: {str(e)}\n原始响应:\n{response_content}")
            except Exception as e:
                raise ValueError(f"解析API响应时出错: {str(e)}\n原始响应:\n{response_content}")
            
            # 更新结果
            self.root.after(0, self.update_result, analysis)
            self.root.after(0, self.update_status, "分析完成")
            
        except Exception as e:
            self.root.after(0, CustomErrorDialog, self.root, "分析失败", f"API调用失败: {str(e)}")
            self.root.after(0, self.update_status, "分析失败")
        finally:
            self.root.after(0, self.enable_analyze_button)
    
    def update_result(self, result):
        """更新分析结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        self.result_text.config(state=tk.DISABLED)
    
    def update_status(self, status):
        """更新状态"""
        self.status_var.set(status)
    
    def enable_analyze_button(self):
        """启用分析按钮"""
        self.analyze_button.config(state=tk.NORMAL)
    
    def analyze_result(self):
        """分析结果，将其拆分为8个部分"""
        # 获取原始分析结果
        raw_result = self.result_text.get(1.0, tk.END).strip()
        if not raw_result:
            messagebox.showwarning("警告", "没有可分析的结果")
            return
        
        # 获取所有分解词
        separators = [var.get().strip() for var in self.separators]
        
        # 检查分解词是否重复
        if len(set(separators)) != len(separators):
            messagebox.showwarning("警告", "分解词不能重复")
            return
        
        # 清空所有输出框
        for text_widget in self.result_texts:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
        
        # 查找所有分解词的位置
        positions = []
        for i, sep in enumerate(separators):
            if sep:
                start = raw_result.find(sep)
                if start != -1:
                    positions.append((start, start + len(sep), i, sep))
        
        # 按位置排序
        positions.sort()
        
        # 拆分结果
        last_pos = 0
        for i, (start, end, idx, sep) in enumerate(positions):
            # 处理上一个分解词到当前分解词之间的内容
            if i > 0:
                prev_end = positions[i-1][1]
                content = raw_result[prev_end:start].strip()
                prev_idx = positions[i-1][2]
                
                if content:
                    self.result_texts[prev_idx].config(state=tk.NORMAL)
                    self.result_texts[prev_idx].insert(1.0, content)
                    self.result_texts[prev_idx].config(state=tk.DISABLED)
                    
                    # 更新结果框标题
                    self.result_outputs[prev_idx].config(text=f"{separators[prev_idx]}")
            
            # 处理最后一个分解词到文本结尾的内容
            if i == len(positions) - 1:
                content = raw_result[end:].strip()
                if content:
                    self.result_texts[idx].config(state=tk.NORMAL)
                    self.result_texts[idx].insert(1.0, content)
                    self.result_texts[idx].config(state=tk.DISABLED)
                    
                    # 更新结果框标题
                    self.result_outputs[idx].config(text=f"{separators[idx]}")
            
            last_pos = end
        
        # 如果没有找到任何分解词，将整个结果显示在第一个输出框
        if not positions:
            self.result_texts[0].config(state=tk.NORMAL)
            self.result_texts[0].insert(1.0, raw_result)
            self.result_texts[0].config(state=tk.DISABLED)
            
            # 更新结果框标题
            self.result_outputs[0].config(text=f"{separators[0]}")
        
        messagebox.showinfo("分析完成", "结果已成功拆分")
    
    def save_result(self):
        """保存分析结果"""
        result = self.result_text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("警告", "没有可保存的分析结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存分析结果"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result)
                self.status_var.set(f"结果已保存到: {os.path.basename(file_path)}")
            except Exception as e:
                CustomErrorDialog(self.parent, "错误", f"保存文件失败: {str(e)}")
                self.status_var.set("就绪")
    
    def create_context_menus(self):
        """创建右键菜单"""
        # 创建通用的文本框右键菜单
        self.text_menu = Menu(self.root, tearoff=0)
        self.text_menu.add_command(label="复制", accelerator="Ctrl+C", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        self.text_menu.add_command(label="粘贴", accelerator="Ctrl+V", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
        self.text_menu.add_command(label="剪切", accelerator="Ctrl+X", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        self.text_menu.add_command(label="全选", accelerator="Ctrl+A", command=lambda: self.root.focus_get().event_generate("<<SelectAll>>"))
        self.text_menu.add_separator()
        self.text_menu.add_command(label="清除", command=lambda: self.root.focus_get().delete(1.0, tk.END) if hasattr(self.root.focus_get(), 'delete') else None)
        
        # 绑定右键菜单到各个文本框
        for text_widget in [self.script_text, self.result_text]:
            text_widget.bind("<Button-3>", self.show_text_menu)
    
    def show_text_menu(self, event):
        """显示右键菜单"""
        try:
            self.text_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_menu.grab_release()
    
    # 菜单栏功能已移除，改为使用工具架标签页
    
    def show_api_config(self):
        """显示API配置对话框"""
        ConfigDialog(self.root, self.api_key, self.api_url, self.model)
    
    def show_prompt_config(self):
        """显示提示词配置对话框"""
        # 创建提示词配置对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("提示词配置")
        dialog.geometry("600x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 应用深色主题到新对话框（如果是Toplevel，通常不需要额外设置，但为了保险）
        dialog.configure(bg='#2b2b2b')
        
        # 创建主框架
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 模板管理区域
        template_frame = ttk.LabelFrame(main_frame, text="提示词模板", padding="5")
        template_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 模板选择下拉框
        ttk.Label(template_frame, text="选择模板:").pack(side=tk.LEFT, padx=5)
        
        template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_frame, textvariable=template_var)
        template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 加载模板列表
        templates = self.load_prompt_templates()
        template_names = list(templates.keys())
        template_combo['values'] = template_names
        
        def load_selected_template(event=None):
            name = template_var.get()
            if name in templates:
                prompt_text.delete(1.0, tk.END)
                prompt_text.insert(1.0, templates[name])
        
        template_combo.bind("<<ComboboxSelected>>", load_selected_template)
        
        # 删除模板按钮
        def delete_template():
            name = template_var.get()
            if not name:
                return
            if name in templates:
                if messagebox.askyesno("确认", f"确定要删除模板 '{name}' 吗？"):
                    del templates[name]
                    self.save_prompt_templates(templates)
                    # 刷新列表
                    current_names = list(templates.keys())
                    template_combo['values'] = current_names
                    template_var.set("")
        
        delete_btn = ttk.Button(template_frame, text="删除", command=delete_template)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # 提示词说明
        ttk.Label(main_frame, text="分析提示词 (系统会自动在末尾附加剧本内容): ").pack(anchor=tk.W, pady=(0, 5))
        
        # 提示词文本框
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        prompt_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=10,
                             bg='#1e1e1e', fg='#ffffff', insertbackground='white')
        scrollbar.config(command=prompt_text.yview)
        prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 插入当前提示词
        prompt_text.insert(1.0, self.prompt.get())
        
        # 底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 保存为新模板区域
        save_template_frame = ttk.Frame(button_frame)
        save_template_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(save_template_frame, text="另存为模板:").pack(side=tk.LEFT, padx=5)
        new_template_name = tk.StringVar()
        ttk.Entry(save_template_frame, textvariable=new_template_name, width=15).pack(side=tk.LEFT, padx=5)
        
        def save_as_template():
            name = new_template_name.get().strip()
            content = prompt_text.get(1.0, tk.END).strip()
            if not name:
                messagebox.showwarning("警告", "请输入模板名称")
                return
            if not content:
                messagebox.showwarning("警告", "提示词内容不能为空")
                return
            
            templates[name] = content
            self.save_prompt_templates(templates)
            
            # 刷新列表
            current_names = list(templates.keys())
            template_combo['values'] = current_names
            template_var.set(name)
            messagebox.showinfo("成功", f"模板 '{name}' 已保存")
            
        ttk.Button(save_template_frame, text="保存模板", command=save_as_template).pack(side=tk.LEFT, padx=5)
        
        # 底部右侧按钮
        right_btn_frame = ttk.Frame(button_frame)
        right_btn_frame.pack(side=tk.RIGHT)
        
        # 应用并关闭按钮
        def apply_prompt():
            new_prompt = prompt_text.get(1.0, tk.END).strip()
            if new_prompt:
                self.prompt.set(new_prompt)
                dialog.destroy()
        
        ttk.Button(right_btn_frame, text="应用", command=apply_prompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(right_btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_prompt_templates(self):
        """加载提示词模板"""
        try:
            if os.path.exists("prompt_templates.json"):
                with open("prompt_templates.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载模板失败: {e}")
        return {}

    def save_prompt_templates(self, templates):
        """保存提示词模板"""
        try:
            with open("prompt_templates.json", "w", encoding="utf-8") as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存模板失败: {str(e)}")
            
    def show_split_options(self):
        """显示分解词配置对话框"""
        # 显示分解词配置对话框
        SplitConfigDialog(self.root, self.separators, self.bulk_add_separators, self.prefix_var, self.suffix_var, self.add_number_var)
    
    def create_split_options_dialog(self):
        """创建分解词配置对话框"""
        pass
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """短视频脚本分析工具使用帮助：

1. 在菜单栏中选择"配置" -> "API配置"设置您的API密钥和模型
2. 在左侧输入框中输入或上传短视频脚本
3. 点击"分析脚本"按钮或使用快捷键Ctrl+Enter开始分析
4. 分析结果将显示在右侧结果区域
5. 可以点击"保存结果"按钮将分析结果保存到本地文件

快捷键：
- Ctrl+O: 上传脚本文件
- Ctrl+S: 保存结果
- Ctrl+D: 清空内容
- Ctrl+Enter: 分析脚本
- Ctrl+Q: 退出程序
"""
        messagebox.showinfo("使用帮助", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """短视频脚本分析工具 v1.0

这是一个用于分析短视频脚本的工具，通过调用大语言模型API提供专业的脚本评估和改进建议。

技术特点：
- 可视化界面，操作简单直观
- 支持API配置自定义
- 提供丰富的快捷键支持
- 支持文件上传和结果保存
"""
        messagebox.showinfo("关于", about_text)
    
    def create_shortcuts(self):
        """创建快捷键"""
        # 分析脚本快捷键 Ctrl+Enter
        self.root.bind("<Control-Return>", lambda event: self.start_analysis())
        
        # 上传文件快捷键 Ctrl+O
        self.root.bind("<Control-o>", lambda event: self.upload_file())
        
        # 保存结果快捷键 Ctrl+S
        self.root.bind("<Control-s>", lambda event: self.save_result())
        
        # 清空内容快捷键 Ctrl+D
        self.root.bind("<Control-d>", lambda event: self.clear_content())
        
        # 退出快捷键 Ctrl+Q
        self.root.bind("<Control-q>", lambda event: self.root.quit())
    
    def bulk_add_separators(self, use_chinese_numbers=False):
        """一键添加分解词"""
        prefix = self.prefix_var.get()
        suffix = self.suffix_var.get()
        add_number = self.add_number_var.get()
        
        # 中文数字映射
        chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八']
        
        # 生成8个分解词
        for i in range(8):
            if add_number:
                # 根据参数选择数字格式
                if use_chinese_numbers:
                    separator = f"{prefix}{chinese_numbers[i]}{suffix}"
                else:
                    separator = f"{prefix}{i+1}{suffix}"
            else:
                separator = f"{prefix}{suffix}"
            self.separators[i].set(separator)
        
        if add_number:
            if use_chinese_numbers:
                self.status_var.set(f"已生成分解词: {prefix}{chinese_numbers[0]}{suffix} - {prefix}{chinese_numbers[7]}{suffix}")
            else:
                self.status_var.set(f"已生成分解词: {prefix}1{suffix} - {prefix}8{suffix}")
        else:
            self.status_var.set(f"已生成分解词: {prefix}{suffix} (重复8次)")
    
    def clear_content(self):
        """清空内容"""
        self.script_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # 清空所有结果输出框
        for text_widget in self.result_texts:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
            
        self.status_var.set("已清空")
    
    def bind_mouse_wheel(self, widget):
        """绑定鼠标滚轮事件"""
        # 使用 bind_all 确保在整个应用中都能捕获（除了被特定控件拦截的）
        # Windows
        widget.bind_all("<MouseWheel>", self._on_mouse_wheel)
        # Linux
        widget.bind_all("<Button-4>", self._on_mouse_wheel)
        widget.bind_all("<Button-5>", self._on_mouse_wheel)
    
    def _on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 获取当前鼠标下的控件
        widget = event.widget
        
        # 1. 如果控件不在主窗口中（例如在对话框中），不处理
        try:
            if widget.winfo_toplevel() != self.root:
                return
        except Exception:
            pass
            
        # 2. 智能滚动处理
        scroll_canvas = True
        
        try:
            if isinstance(widget, tk.Text) or "Text" in str(widget.winfo_class()):
                # 检查文本框是否需要滚动
                # yview() 返回 (top, bottom)，范围 0.0-1.0
                # 如果 (0.0, 1.0) 说明全部内容可见，不需要滚动文本框
                top, bottom = widget.yview()
                
                if top == 0.0 and bottom == 1.0:
                    # 内容完全可见，直接滚动页面
                    scroll_canvas = True
                else:
                    # 检查滚动方向
                    # Windows: delta > 0 是向上滚，delta < 0 是向下滚
                    # Linux: num 4 是向上滚，num 5 是向下滚
                    is_scrolling_up = (event.delta > 0) if hasattr(event, "delta") else (event.num == 4)
                    is_scrolling_down = (event.delta < 0) if hasattr(event, "delta") else (event.num == 5)
                    
                    if is_scrolling_up and top == 0.0:
                        # 已经在顶部且向上滚 -> 滚动页面
                        scroll_canvas = True
                    elif is_scrolling_down and bottom == 1.0:
                        # 已经在底部且向下滚 -> 滚动页面
                        scroll_canvas = True
                    else:
                        # 其他情况滚动文本框（让事件继续传播）
                        scroll_canvas = False
        except Exception:
            pass
            
        # 3. 执行主画布滚动
        if scroll_canvas:
            if event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
                self.canvas.yview_scroll(-1, "units")

    def save_single_split_result(self, index):
        """保存单个拆分结果"""
        try:
            content = self.result_texts[index].get(1.0, tk.END).strip()
            if not content:
                messagebox.showwarning("警告", "没有可保存的内容")
                return
            
            # 获取默认文件名（使用标题）
            default_name = self.separators[index].get()
            # 清理文件名中的非法字符
            default_name = "".join([c for c in default_name if c.isalnum() or c in (' ', '-', '_')]).strip()
            if not default_name:
                default_name = f"result_{index+1}"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"{default_name}.txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                title=f"保存 - {default_name}"
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_var.set(f"已保存: {os.path.basename(file_path)}")
        except Exception as e:
            # 使用 self.root 作为父窗口
            CustomErrorDialog(self.root, "错误", f"保存失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptAnalyzerGUI(root)
    root.mainloop()
