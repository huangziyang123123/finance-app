import streamlit as st
import pandas as pd
import plotly.express as px

# ============ 队友的模块（目前用本地实现，队友交付后替换成 from utils import / from ai_helper import）============
def analyze_finance(df):
    """输入记账表格，返回总收入、总支出、结余"""
    if df is None or df.empty:
        raise ValueError("表格是空的，没有任何数据")

    # 兼容两种列名写法
    if "收支类型" in df.columns:
        col_type = "收支类型"
    elif "类型" in df.columns:
        col_type = "类型"
    else:
        raise ValueError("缺少『收支类型』列")
    if "金额" not in df.columns:
        raise ValueError("缺少『金额』列")

    total_in = df.loc[df[col_type] == "收入", "金额"].sum()
    total_out = df.loc[df[col_type] == "支出", "金额"].sum()
    return {"总收入": float(total_in), "总支出": float(total_out), "结余": float(total_in - total_out)}


def get_ai_advice(res, details, mode):
    """根据收支情况给出不同风格建议"""
    income, out, rest = res["总收入"], res["总支出"], res["结余"]
    top = details.split("、")[0] if details else "日常开销"

    if income <= 0:
        return "这个月收入为 0，先把收入情况录进来，不然没法判断你的花销水平哦。"

    rate = out / income * 100 if income else 0
    if mode == "毒舌":
        if rate >= 90:
            return f"支出占了收入的 {rate:.0f}%，基本是月光族的日薪水平了。花钱最多的还是{top}，先把这个口子堵上吧。"
        if rate >= 70:
            return f"花了 {rate:.0f}%，结余只剩 {rest:.0f} 元，看着不慌？{top}这块再这么花下去，下个月照样吃土。"
        return f"结余 {rest:.0f} 元还算及格，但别飘，{top}这类支出稍不注意就失控。"
    else:
        if rate >= 90:
            return f"这个月支出占比偏高（{rate:.0f}%），主要是{top}。试着给它设一个上限，压力会小很多，慢慢来就好。"
        if rate >= 70:
            return f"整体还算平稳，结余 {rest:.0f} 元。可以把{top}稍微收一收，存下一笔应急金会更安心哦。"
        return f"收支结构挺健康的，结余 {rest:.0f} 元。保持这个节奏，再给{top}留点弹性预算就更稳妥啦。"
# ========================================================================================

st.set_page_config(page_title="个人记账分析工具", layout="wide")
st.title("📊 个人记账分析工具")
st.caption("上传记账流水 → 自动统计收支 → AI 给出消费建议")

with st.sidebar:
    st.header("📁 上传记账表格")
    uploaded_file = st.file_uploader("上传 csv / xlsx 文件", type=["csv", "xlsx"])
    use_demo = st.checkbox("先用示例数据看一下效果")

df = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="gbk")
        else:
            df = pd.read_excel(uploaded_file)
    except Exception:
        st.error("❌ 文件读取失败：请确认是 csv / xlsx 文件，并且没有被其他程序占用。")
elif use_demo:
    df = pd.DataFrame({
        "日期": ["2026-09-01", "2026-09-01", "2026-09-02", "2026-09-03", "2026-09-05"],
        "分类": ["生活费", "购物", "餐饮", "餐饮", "娱乐"],
        "金额": [2000, 49, 13, 20, 45],
        "收支类型": ["收入", "支出", "支出", "支出", "支出"],
        "备注": ["家里转账", "洗衣液", "和室友聚餐", "黄焖鸡", "游戏充值"],
    })

if df is not None:
    try:
        res = analyze_finance(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 总收入", f"{res['总收入']:.2f} 元")
        col2.metric("💸 总支出", f"{res['总支出']:.2f} 元")
        col3.metric("📌 结余", f"{res['结余']:.2f} 元")

        st.divider()

        col_a, col_b = st.columns(2)

        with col_a:
            fig_pie = px.pie(
                values=[res["总收入"], res["总支出"]],
                names=["收入", "支出"],
                title="收支占比",
                color_discrete_sequence=["#2E8B57", "#D9534F"],
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            col_type = "收支类型" if "收支类型" in df.columns else "类型"
            spend = df[df[col_type] == "支出"]
            if not spend.empty:
                cat_sum = spend.groupby("分类")["金额"].sum().sort_values(ascending=False)
                fig_bar = px.bar(
                    x=cat_sum.values,
                    y=cat_sum.index,
                    orientation="h",
                    title="支出分类排名",
                    labels={"x": "金额（元）", "y": "分类"},
                )
                fig_bar.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("暂无支出记录")

        top3 = "、".join(cat_sum.index[:3]) if not spend.empty else ""
        st.caption(f"明细共 {len(df)} 条记录；支出主要花在：{top3}")

        st.divider()
        st.subheader("🤖 AI 消费建议")
        advice_mode = st.radio("选择 AI 风格", ["毒舌", "温柔"], horizontal=True)
        if st.button("生成消费建议"):
            with st.spinner("AI 思考中..."):
                st.success(get_ai_advice(res, top3, advice_mode))

    except Exception as e:
        st.error("❌ 文件处理失败：请检查表格是否为空、表头是否包含『日期 / 分类 / 金额 / 收支类型』。")
        st.caption(f"错误详情：{e}")
else:
    st.info("👈 请在左侧上传表格，或勾选「先用示例数据看一下效果」")
