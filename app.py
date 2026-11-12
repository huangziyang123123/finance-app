import streamlit as st
import pandas as pd
import plotly.express as px

def analyze_finance(df):
    if df.empty:
        raise ValueError("表格是空的")
    if "类型" in df.columns and "金额" in df.columns:
        total_in = df.loc[df["类型"] == "收入", "金额"].sum()
        total_out = df.loc[df["类型"] == "支出", "金额"].sum()
    elif "金额" in df.columns:
        total_in = df[df["金额"] > 0]["金额"].sum()
        total_out = -df[df["金额"] < 0]["金额"].sum()
    else:
        raise ValueError("表格里找不到 类型/金额 列")
    return {"总收入": total_in, "总支出": total_out, "结余": total_in - total_out}

def get_ai_advice(mode):
    if mode == "毒舌":
        return "你这花钱速度，月底怕是要吃土了，收着点吧。"
    return "整体还不错~ 建议固定存一笔，剩下的放心花，慢慢来会更安心哦。"

st.set_page_config(page_title="个人记账分析", layout="wide")
st.title("📊 个人记账分析网页")

with st.sidebar:
    st.header("📁 上传记账表格")
    uploaded_file = st.file_uploader("上传 csv / xlsx", type=["csv", "xlsx"])
    use_demo = st.checkbox("先用示例数据试一下")

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    except Exception:
        st.error("❌ 文件读取失败：请检查文件格式是否为 csv / xlsx")
elif use_demo:
    df = pd.DataFrame({"类型": ["收入", "收入", "支出", "支出", "支出"],
                       "金额": [5000, 1200, 800, 350, 210]})

if df is not None:
    try:
        res = analyze_finance(df)
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 总收入", f"{res['总收入']:.2f}")
        col2.metric("💸 总支出", f"{res['总支出']:.2f}")
        col3.metric("📌 结余", f"{res['结余']:.2f}")

        fig = px.pie(values=[res["总收入"], res["总支出"]], names=["收入", "支出"], title="收支占比")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("🤖 AI 消费建议")
        advice_mode = st.radio("选择 AI 风格", ["毒舌", "温柔"], horizontal=True)
        if st.button("生成消费建议"):
            with st.spinner("AI 思考中..."):
                st.success(get_ai_advice(advice_mode))

    except Exception as e:
        st.error("❌ 文件处理失败！请检查表格是否为空、列名是否正确。")
        st.caption(f"错误详情：{e}")
else:
    st.info("👈 请在左侧上传表格，或勾选「先用示例数据试一下」")
