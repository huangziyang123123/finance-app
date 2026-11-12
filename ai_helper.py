import requests

def get_ai_advice(consumption_data, style="毒舌犀利"):
    """
    调用大模型 API 生成财务建议
    """
    
    # ⚠️ 注意：请使用者在此处填入自己申请的智谱 API Key
    api_key = "请在这里填入您的API-key"
    
    # 防止使用者忘记填 Key 导致报错
    if "请在此处替换" in api_key:
        return "⚠️ 提示：请先在 ai_helper.py 中填入你的智谱 API Key 才能使用智能点评功能哦！"
    
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"你是一个{style}的理财顾问。以下是大学生消费数据：{consumption_data}。请用一段话总结并点评，字数在300字左右，要求提及消费数据里的统计和分类结果，并贴合大学生的生活，语言生动，使用口语化的语言.注意输出对象是单个用户。"
    
    data = {
        "model": "glm-4-flash",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    # 这里开始是请求与解析，我已经帮你把缩进全部对齐了
    try:
        # 1. 像服务器发送请求，把包装好的数据寄出去
        response = requests.post(url, headers=headers, json=data)
        
        # 2. 把服务器返回的结果，转换成 Python 能看懂的字典（dict）格式
        result_data = response.json()
        
        # 3. 像剥洋葱一样，一层层把 AI 说的话提取出来
        choices_list = result_data["choices"] # 第一层：获取所有结果
        first_choice = choices_list[0]        # 第二层：拿第一个结果
        message_dict = first_choice["message"]# 第三层：找到对话内容
        ai_reply = message_dict["content"]    # 第四层：拿到最终的纯文本
        
        # 4. 把 AI 的回复交还给主程序
        return ai_reply
        
    except Exception as e:
        # 如果断网了、或者 API Key 填错了，就会走到这里
        return "哎呀，AI 顾问开小差了，请检查你的网络或 API Key 是否正确哦！"