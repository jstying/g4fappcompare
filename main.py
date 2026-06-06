from flask import Flask, render_template, request, jsonify  # 从 flask 库导入应用基础类和请求处理函数
import requests  # 导入用于发送 HTTP 请求的 requests 库

app = Flask(__name__)  # 创建 Flask 应用实例

# 字典中存放了各个提供商及其对应的 API 请求地址, 但这些提供商失效了, 无法使用
PROVIDERS = {
    "You.com": "https://api.you.com/v1/chat",
    "HuggingChat": "https://huggingface.co/api/chat",
    "Phind": "https://api.phind.com/v1/chat",
    "DeepAI": "https://api.deepai.org/v1/chat",
    "OpenAssistant": "https://api.open-assistant.io/v1/chat"
}

@app.route("/")  # 定义网站根目录的路由
def index():  # 定义主页渲染函数
    return render_template("index.html", providers=list(PROVIDERS.keys()))  # 将提供商列表传递给网页模板

@app.route("/compare", methods=["POST"])  # 定义处理对比请求的路由，仅接受 POST 方法
def compare():  # 定义对比功能的处理函数
    data = request.json  # 获取前端发送的 JSON 数据
    message = data.get("message")  # 从数据中获取用户输入的问题
    selected_providers = data.get("providers", [])  # 获取用户勾选的提供商列表

    if not message or not selected_providers:  # 检查输入是否合法
        return jsonify({"error": "Message and providers are required"}), 400  # 如果缺失数据则返回错误信息

    responses = {}  # 初始化存储响应结果的字典
    for provider in selected_providers:  # 遍历用户选中的每一个提供商
        url = PROVIDERS.get(provider)  # 获取对应提供商的接口地址
        if not url:  # 如果找不到地址则跳过
            responses[provider] = "Invalid provider"
            continue

        try:  # 尝试向接口发送请求
            payload = {  # 构建请求数据体
                "model": "gpt-4",
                "prompt": message,
                "max_tokens": 150
            }
            # 发送 POST 请求并设置超时时间为 30 秒
            res = requests.post(url, json=payload, timeout=30)
            res.raise_for_status()  # 检查请求是否出现 HTTP 错误
            ai_text = res.json().get("text", "No response")  # 从返回的 JSON 中提取文本
            responses[provider] = ai_text  # 保存成功的结果
        except requests.exceptions.RequestException as e:  # 捕获请求过程中出现的异常
            responses[provider] = f"Error: {str(e)}"  # 将错误信息保存到结果中

    return jsonify({"results": responses})  # 将所有响应结果打包成 JSON 返回

if __name__ == "__main__":  # 判断程序是否直接运行
    app.run(host="0.0.0.0", port=8080)  # 在指定端口启动 Web 服务