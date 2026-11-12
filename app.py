# 导入需要的工具包
import streamlit as st
import pandas as pd
import plotly.express as px
# 导入队友写好的两个功能
from utils import analyze_finance
from ai_helper import get_ai_advice

# 网页标题、布局设置
st.set_page_config(page_title="记账工具", layout="wide")
st.title("📊个人记账分析网页")

# ========== 1. 左边侧边栏：文件上传（任务第一条）==========
with st.sidebar:  # with st.sidebar 代表：里面所有东西都放在页面左边
    st.header("📁上传记账表格")
    # 上传按钮，可以传csv或者excel
    uploaded_file = st.file_uploader("上传流水文件", type=["csv","xlsx"])

# ========== 2. 如果用户上传了文件，就开始处理 ==========
if uploaded_file is not None:
    # try 和 except 就是容错！任务第四条重点！
    # try：试着跑里面代码；如果出错（空表、格式不对），直接跳到except友好提示，不崩溃
    try:
        # 判断是csv还是excel，读取表格
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 调用队友写好的函数，自动算出收入支出结余
        result = analyze_finance(df)
        income = result["总收入"]
        expend = result["总支出"]
        rest = result["结余"]

        # st.metric 并排展示三个数字（任务第二条）
        col1,col2,col3 = st.columns(3) # 分成3列并排
        with col1:
            st.metric("总收入", f"{income:.2f}")
        with col2:
            st.metric("总支出", f"{expend:.2f}")
        with col3:
            st.metric("结余", f"{rest:.2f}")

        # 画饼图
        fig = px.pie(values=[income,expend], names=["收入","支出"], title="收支占比")
        st.plotly_chart(fig, use_container_width=True)

        # ========== 3. AI交互部分（任务第三条）==========
        st.subheader("🤖 AI消费建议")
        # 单选框：二选一，温柔 / 毒舌
        select_style = st.radio("选择AI风格", ["毒舌","温柔"])
        # 按钮
        click_btn = st.button("生成AI建议")
        if click_btn: # 当按钮被按下的时候
            advice = get_ai_advice(select_style)
            st.success(advice)

    # 出错的时候执行这里，友好提示，不会爆红报错
    except Exception:
        st.error("❌ 文件出错啦！检查一下表格是不是空的、格式对不对！")

# 没有上传文件的时候，页面提示
else:
    st.info("👈 在左边上传你的记账流水表格")
