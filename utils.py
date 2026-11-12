import pandas as pd

# ================= 1. 自动分类引擎 =================
def auto_categorize(merchant_name):
    """
    根据商户名/备注，自动猜测消费分类
    """
    if pd.isna(merchant_name): return "其他"
    
    # 建立一个关键词字典
    keywords = {
        "餐饮": ["瑞幸", "星巴克", "食堂", "美团", "饿了么", "面", "饭", "麻辣烫", "奶茶", "包子", "小吃", "水果","美团商户"],
        "交通": ["滴滴", "公交", "地铁", "高铁", "哈啰", "单车", "打车", "车费"],
        "购物": ["淘宝", "京东", "拼多多", "超市", "便利店", "商城", "百货"],
        "娱乐": ["电影", "KTV", "游戏", "腾讯", "爱奇艺"]
    }
    
    for category, words in keywords.items():
        for word in words:
            if word in str(merchant_name):
                return category
    return "其他" # 如果没匹配上，就归类为其他

# ================= 2. 微信账单清洗引擎 =================
def clean_wechat_bill(file_path):
    """
    智能清洗微信账单：自动寻找真实的表头位置
    """
    try:
        # 第一步：我们自己打开文件，逐行找“交易时间”在哪
        header_row = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # 只要这一行里有“交易时间”，说明真正的表头在这里！
                if "交易时间" in line:
                    header_row = i
                    break  # 找到了就立刻停止寻找
        
        # 第二步：告诉 Pandas，跳过前面所有的废话（header_row），直接从表头开始读
        df = pd.read_csv(file_path, skiprows=header_row, encoding='utf-8')

        # 下面就和之前一样了，提取需要的列并重命名
        cleaned_df = pd.DataFrame()
        cleaned_df['日期'] = df['交易时间']
        cleaned_df['收支类型'] = df['收/支']
        # 清洗金额前面的 ¥ 符号
        cleaned_df['金额'] = df['金额(元)'].astype(str).str.replace('¥', '').astype(float)
        cleaned_df['备注'] = df['交易对方']
        
        # 过滤掉无效行
        cleaned_df = cleaned_df[cleaned_df['收支类型'].isin(['收入', '支出'])]
        
        # 自动分类
        cleaned_df['分类'] = cleaned_df['备注'].apply(auto_categorize)
        
        return cleaned_df
        
    except Exception as e:
        return {"error": f"解析失败：{e}"}

# ================= 3. 核心统计函数（稍作修改，让它既能读文件，也能接收DataFrame） =================
def analyze_finance(data_source):
    """
    输入: csv文件路径 或 清洗好的 DataFrame
    """
    try:
        if isinstance(data_source, str):
            df = pd.read_csv(data_source, encoding='utf-8')
        else:
            df = data_source # 如果传入的已经是表格，直接用
            
        # 确保金额列是数字格式
        df["金额"] = pd.to_numeric(df["金额"], errors="coerce").fillna(0)

        # 核心统计计算
        income_df = df[df["收支类型"] == "收入"]
        expense_df = df[df["收支类型"] == "支出"]
        
        total_income = income_df["金额"].sum()
        total_expense = expense_df["金额"].sum()
        balance = total_income - total_expense

        category_sum = expense_df.groupby("分类")["金额"].sum().to_dict()
        
        if category_sum:
            max_category = max(category_sum, key=category_sum.get)
            max_amount = category_sum[max_category]
            percentage = round((max_amount / total_expense) * 100, 1) if total_expense > 0 else 0
        else:
            max_category, max_amount, percentage = "无", 0, 0

        next_month_budget = round(balance * 0.8, 2) if balance > 0 else 0
        
        feature_text = (
            f"本月总收入 {total_income} 元，总支出 {total_expense} 元，结余 {balance} 元。"
            f"支出中占比最高的是【{max_category}】，金额 {max_amount} 元，占总支出的 {percentage}%。"
            f"各类支出明细为：{category_sum}。"
            f"建议下个月预算控制在 {next_month_budget} 元左右。"
        )
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "category_data": category_sum,
            "max_category": max_category,
            "next_budget": next_month_budget,
            "feature_text": feature_text
        }
    except Exception as e:
        return {"error": f"统计失败：{e}"}