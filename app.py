import streamlit as st
import pandas as pd
import plotly.express as px

# ============ 统计计算模块（逻辑不动）============
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


def get_review_text(res, details, mode):
    """消费复盘文字，重写，去掉AI味道"""
    income, out, rest = res["总收入"], res["总支出"], res["结余"]
    top_list = details.split("、") if details else []
    top = top_list[0] if top_list else "日常开销"

    if income <= 0:
        return "目前还没有登记收入记录，暂时没法客观评估你的开销节奏。可以先把生活费、兼职、红包这些进账都记进去，收入是预算的基础，补齐之后，再看钱花得合不合适才更有意义。等收入记录完整，就能算出各项开销占比，帮你找到可以调整的地方，慢慢找到适合自己存钱的节奏。"

    rate = out / income * 100 if income else 0
    if mode == "直白提醒":
        if rate >= 90:
            return f"现在支出占到收入的{rate:.0f}%，几乎留不下钱，结余只有{rest:.0f}元。花钱大头是{top}，其次还有{('、'.join(top_list[1:])) if len(top_list)>1 else '其他零散开销'}，这样的消费状态容错空间很小。一旦遇到临时需要用钱的情况，很容易紧张。优先给{top}这项设一个花钱上限，买东西前多想一想是不是刚需。大学生正是建立消费习惯的时候，一直接近月光，很难攒下属于自己的备用金。"
        if rate >= 70:
            return f"本月开销占收入{rate:.0f}%，结余{rest:.0f}元，表面上还撑得住，但已经快要踩线了。主要花费在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '和一些零碎支出'}。很多小钱单独看不多，攒在一起就吃掉一大半收入。再多一笔意外支出就容易超支。可以给{top}定好每月额度，同时留意奶茶、网购这类不起眼的小额消费，积少成多影响不小。存钱别等月底剩下多少，尽量先预留一部分再安排消费。"
        return f"当前结余{rest:.0f}元，整体收支还算稳妥，但不能松懈。大额支出集中在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '以及其他日常花费'}。现在看着宽裕，很容易慢慢提高花钱标准，之后再收紧就难了。区分刚需和享受型消费，必要的优先，非急需的可以延后。坚持定期看账单复盘，慢慢把能存下来的比例拉高，手里有余钱才更踏实。"
    else:
        if rate >= 90:
            return f"这个月开销占收入{rate:.0f}%，比例偏高，花钱集中在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '和一些零散支出'}，结余{rest:.0f}元。不用一下子压缩所有开销，可以慢慢调整。先从占比最高的{top}入手，设置一个舒服的上限，减少冲动下单。想买东西可以放一天再决定，避开情绪消费。慢慢攒一点备用小金库，不用一次存很多，每月结余优先放进去，应对突发支出会从容很多。记账本身就是慢慢摸清自己花钱习惯的过程，一点点调整就好。"
        if rate >= 70:
            return f"收支整体还算平稳，结余{rest:.0f}元，开销主要是{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '等项目'}。还有优化空间，不用大幅度改变日常。可以适当控制{top}这类弹性消费，分清必须要买和用来放松享受的部分，享受可以有，但控制好频率。随手花的小额消费很容易被忽略，长期也是一笔不小的数目。试着养成先存后花的习惯，每个月固定留一部分作为储蓄，再安排其余开销，定期回看账单，找到适合自己舒服的节奏。"
        return f"很棒，目前收支状态比较健康，结余{rest:.0f}元，主要花费在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '以及其他日常支出'}。保持现在节奏的同时还可以再优化。{top}这类休闲支出可以保留一部分预算，不用完全克制，合理消费不是压抑自己。结余可以分成灵活备用钱和长期储蓄两部分。继续坚持记账复盘，避免不知不觉越花越多。稳定的金钱习惯是慢慢养出来的，既能好好生活，也能稳步攒钱。"


# ===================== 页面配置 =====================
st.set_page_config(page_title="我的记账本", layout="wide")

# 标题区，加一点样式感
st.markdown("""
<div style="padding:16px; background:#f7f9fc; border-radius:12px; border-left:6px solid #4682B4;">
    <h2 style="margin:0; color:#2c3e50;">我的记账本</h2>
    <p style="margin:6px 0 0; color:#555;">上传账单表格，查看收支汇总，梳理自己的花钱节奏</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# 侧边栏
with st.sidebar:
    st.markdown("### 📂 账单文件")
    uploaded_file = st.file_uploader("上传表格", type=["csv", "xlsx"], help="表头需要包含：日期、分类、金额、收支类型")
    use_demo = st.checkbox("打开示例账单预览效果")
    st.markdown("""
    <div style="background:#f0f4f8; padding:10px; border-radius:8px; font-size:13px; color:#444;">
    💡 小提示<br>
    - 支持 csv / xlsx<br>
    - 收支类型填：收入 / 支出
    </div>
    """, unsafe_allow_html=True)


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
        st.error("❌ 文件读取失败，检查文件格式，不要在WPS/Excel里打开占用着文件。")
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
        # 账单明细区块
        st.markdown("#### 📝 账单明细（可以直接修改）")
        with st.expander("点开查看、编辑每一笔记录", expanded=False):
            df = st.data_editor(df, use_container_width=True)

        st.divider()

        # 收支卡片，美化三块指标
        res = analyze_finance(df)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style="background:#e8f5e9; padding:20px; border-radius:10px; text-align:center;">
                <div style="font-size:14px; color:#333;">总收入</div>
                <div style="font-size:26px; font-weight:bold; color:#2e7d32;">{:.2f} 元</div>
            </div>
            """.format(res["总收入"]), unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:#ffebee; padding:20px; border-radius:10px; text-align:center;">
                <div style="font-size:14px; color:#333;">总支出</div>
                <div style="font-size:26px; font-weight:bold; color:#c62828;">{:.2f} 元</div>
            </div>
            """.format(res["总支出"]), unsafe_allow_html=True)
        with c3:
            rest_color = "#2e7d32" if res["结余"]>=0 else "#c62828"
            st.markdown("""
            <div style="background:#f5f5f5; padding:20px; border-radius:10px; text-align:center;">
                <div style="font-size:14px; color:#333;">当前结余</div>
                <div style="font-size:26px; font-weight:bold; color:{};">{:.2f} 元</div>
            </div>
            """.format(rest_color, res["结余"]), unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 📈 收支图表")
        col_a, col_b = st.columns(2)
        with col_a:
            fig_pie = px.pie(
                values=[res["总收入"], res["总支出"]],
                names=["收入", "支出"],
                title="收入和支出占比",
                color_discrete_sequence=["#43a047", "#e53935"],
                hole=0.2
            )
            fig_pie.update_layout(title_x=0.5)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            col_type = "收支类型" if "收支类型" in df.columns else "类型"
            spend = df[df[col_type] == "支出"]
            cat_sum = None
            if not spend.empty:
                cat_sum = spend.groupby("分类")["金额"].sum().sort_values(ascending=False)
                fig_bar = px.bar(
                    x=cat_sum.values,
                    y=cat_sum.index,
                    orientation="h",
                    title="各类开销排行",
                    labels={"x": "金额（元）", "y": "分类"},
                    color_discrete_sequence=["#5c6bc0"]
                )
                fig_bar.update_layout(yaxis=dict(autorange="reversed"), title_x=0.5)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("目前还没有支出记录")

        top3 = "、".join(cat_sum.index[:3]) if (cat_sum is not None and not cat_sum.empty) else ""
        st.markdown(f"<div style='color:#666;'>一共 {len(df)} 条账单｜主要开销方向：{top3}</div>", unsafe_allow_html=True)

        st.divider()
        # 复盘区域，改名，去掉AI字眼
        st.markdown("#### 📖 消费复盘参考")
        review_style = st.radio("选择复盘语气", ["直白提醒", "温和建议"], horizontal=True)
        run_review = st.button("生成复盘文字")

        if run_review:
            st.markdown("""
            <div style="background:#f8f9fa; padding:18px; border-radius:10px; border:1px solid #e2e8f0;">
            """, unsafe_allow_html=True)
            st.write(get_review_text(res, top3, review_style))
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error("❌ 账单处理出错，请检查表头：需要日期、分类、金额、收支类型")
        st.caption(f"详情：{e}")
else:
    st.markdown("""
    <div style="background:#f0f4f8; padding:24px; border-radius:12px; text-align:center; color:#444;">
    <p style="font-size:16px;">👈 在左侧上传你的记账表格，或者勾选示例账单先看看效果</p>
    </div>
    """, unsafe_allow_html=True)
