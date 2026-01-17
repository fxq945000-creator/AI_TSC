import requests
import json

def test_third_party_api():
    """测试第三方平台API调用"""
    try:
        # 模拟用户可能输入的API URL（没有端点）
        api_url = "https://api.comfly.chat"
        api_key = "your_api_key_here"  # 用户的API密钥
        model = "gpt-4"
        script = "测试脚本内容"
        prompt = "分析以下脚本：{script}"
        
        full_prompt = prompt.replace("{script}", script)
        
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
            if "api.comfly.chat" in api_url or "anyroutes.cn" in api_url:
                # "贞贞的AI工坊"等平台通常使用/v1/chat/completions端点
                final_api_url = f"{api_url.rstrip('/')}/v1/chat/completions"
            elif "openai" in api_url.lower():
                # OpenAI官方API
                final_api_url = f"{api_url.rstrip('/')}/v1/chat/completions"
            elif model.startswith("gemini-"):
                # Google Gemini API使用特定端点
                if "/models/" not in api_url and "/generateContent" not in api_url:
                    final_api_url = f"{api_url.rstrip('/')}/generateContent"
        
        print(f"原始API URL: {api_url}")
        print(f"最终API URL: {final_api_url}")
        
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求payload
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个专业的短视频脚本分析专家"},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        print(f"请求头: {headers}")
        print(f"请求体: {json.dumps(payload, indent=2)}")
        
        # 注意：这里我们不实际发送请求，只是模拟构建过程
        # 如果要实际测试，请取消下面的注释并提供有效的API密钥
        
        # response = requests.post(final_api_url, headers=headers, json=payload, timeout=30)
        # response.raise_for_status()
        # 
        # print(f"\n响应状态码: {response.status_code}")
        # print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")

if __name__ == "__main__":
    test_third_party_api()