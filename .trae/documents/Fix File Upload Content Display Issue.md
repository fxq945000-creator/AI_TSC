我将修改 `c:\AI\AI_TSC\src\script_analyzer.py` 以解决上传文件不显示和 Gemini API 调用失败的问题。

**计划详情：**

1.  **修复“上传剧本”内容不显示问题**:
    *   检查 `upload_file` 函数。虽然代码逻辑看起来包含读取和插入，但可能存在编码问题或 UI 更新未及时生效。
    *   **优化措施**：
        *   增加对文件读取内容的调试打印。
        *   确保在插入文本前 `self.script_text` 处于可编辑状态（虽然通常是可编辑的，但显式确认更安全）。
        *   强制执行 `self.script_text.update_idletasks()` 以确保界面立即刷新。

2.  **修复 Gemini-3-Pro API 调用失败问题**:
    *   **问题分析**：您使用的是第三方中转平台 (`ai.t8star.cn`)。当前代码检测到模型名包含 `gemini` 时，会自动切换为 Google 官方的原生 API 格式（`contents` 结构）和端点。
    *   **解决方案**：第三方中转平台通常统一使用 **OpenAI 兼容格式**（`messages` 结构）来转发所有模型的请求，包括 Gemini。
    *   **修改逻辑**：在 `call_api` 方法中，当检测到使用的是第三方 URL（如 `ai.t8star.cn`）时，**强制使用 OpenAI 格式** 构建请求体，而不管模型名称是什么。只有当 API URL 是 Google 官方地址时，才使用 Gemini 原生格式。

**修改文件**: `c:\AI\AI_TSC\src\script_analyzer.py`
