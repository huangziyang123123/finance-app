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
    """根据收支情况给出不同风格建议，字数≥300"""
    income, out, rest = res["总收入"], res["总支出"], res["结余"]
    top = details.split("、")[0] if details else "日常开销"
    top_list = details.split("、") if details else []

    if income <= 0:
        return "目前你的收入记录为0，暂时没办法评估你的消费结构和存钱能力。建议你先把所有收入来源都录入到记账表格里，包括生活费、兼职收入、红包等，只有完整记录收入，我们才能客观判断你的开销是否合理，后续的消费规划才有参考意义。记账不只是记花出去的钱，收入才是整个预算的根基，缺少收入数据，所有的分析都会失真。等你补全收入信息之后，系统就可以帮你计算支出占比、识别高消费项目，给你适配的存钱方案，帮你慢慢养成稳定的储蓄习惯。"

    rate = out / income * 100 if income else 0
    if mode == "毒舌":
        if rate >= 90:
            return f"你现在支出已经占到收入的{rate:.0f}%，几乎是月光状态，结余只剩下{rest:.0f}元。花钱最多的项目是{top}，其次还有{('、'.join(top_list[1:])) if len(top_list)>1 else '其他零散开销'}，这个消费模式风险非常高。一旦遇到突发情况，比如生病、需要购买必需品，你手里没有备用资金，很容易陷入资金紧张的困境。不要觉得当下有钱花就没有问题，这种高消耗的消费习惯会慢慢吞噬你存钱的可能性。优先把{top}这一项的开销压缩，给自己设置硬性上限，每一笔支出之前先想一想，这个东西是不是必须要买。很多消费都是一时冲动带来的，你现在不控制，后续每个月都要重复月光的循环，很难攒下属于自己的积蓄。大学生阶段本来就是积累资金、建立消费观念的黄金时期，现在放任自己随意消费，等到之后有需要用钱的时候，你就会明白没有存款有多被动。"
        if rate >= 70:
            return f"这个月支出占收入{rate:.0f}%，结余只有{rest:.0f}元，看着好像还能维持，但是隐患已经很大了。你的主要开销集中在{top}，搭配{('、'.join(top_list[1:])) if len(top_list)>1 else '各类小额支出'}，这些零散消费叠加在一起，悄悄吃掉了你大部分收入。很多人就是觉得单次花钱不多，没有放在心上，最后月底一算才发现钱早就花光了。你现在的状态属于临界状态，稍微多一笔额外消费，就直接变成超支。建议你给{top}设置月度预算，每次消费前对照预算看看剩余额度，同时留意那些不起眼的小额支出，奶茶、零食、小件网购，日积月累也是一笔不小的数目。不要抱着“下个月再存钱”的想法，存钱要从当下开始，一点点收紧不必要的开支，慢慢把结余比例拉高，给自己留出应对意外的缓冲资金。"
        return f"目前结余{rest:.0f}元，整体消费暂时及格，但绝对不能放松警惕。你的大额支出集中在{top}，还有{('、'.join(top_list[1:])) if len(top_list)>1 else '其他日常花费'}，现在看着收支平衡，但是很容易因为一次冲动消费直接打乱节奏。很多人就是在这种平稳的状态下放松管控，慢慢提高自己的消费阈值，之后想要再降下来就很难。消费习惯是一点点养出来的，不要因为现在还有结余就随便放宽预算。你可以给{top}这类弹性支出预留浮动上限，同时区分刚需消费和享受型消费，刚需优先保障，非必要消费尽量延后。坚持记账、持续复盘，慢慢把储蓄比例稳定提升，长期下来，你会明显感受到手里有存款带来的安全感，而不是每次月底都担心钱不够用。"
    else:
        if rate >= 90:
            return f"这个月你的支出占比达到了{rate:.0f}%，整体偏高，主要开销集中在{top}，还有{('、'.join(top_list[1:])) if len(top_list)>1 else '一些零散支出'}，目前结余{rest:.0f}元。不用太焦虑，我们可以慢慢调整消费结构，不用一下子苛刻地压缩所有开销。首先可以重点关注{top}这一项，它是占用资金最多的板块，我们可以先给它设置一个温和的月度预算上限，在满足基础需求的前提下，减少非必要的消费。很多时候我们的消费来自一时的情绪，并不是真的需要这件物品，下次准备消费的时候，可以先放一天再决定。同时，建议你慢慢建立一笔应急小金库，应急金不用一次性存很多，每个月结余的钱优先放进去，这笔钱可以帮你应对突发的支出，避免临时缺钱的窘迫。记账本身就是一个认识自己消费习惯的过程，我们一点点优化，慢慢把支出占比降下来，存钱会变成一件轻松的事，而不是压力。"
        if rate >= 70:
            return f"你目前的收支情况整体还算平稳，结余{rest:.0f}元，主要支出分布在{top}、{('、'.join(top_list[1:])) if len(top_list)>1 else '其他日常项目'}。这个状态还有优化的空间，不用大刀阔斧改变生活方式，做一些小调整就会有很好的效果。你可以试着适度收紧{top}这部分弹性开销，分清哪些是必须花的刚需，哪些是用来取悦自己的享受型消费，享受型消费可以保留，但控制频率和金额。小额消费很容易被我们忽略，比如随手买的零食、饮品，长期累积起来也是一笔不小的开支。你可以给自己定一个小目标，每个月强制留存一部分收入作为储蓄，先存后花，而不是花完剩下多少存多少。坚持一段时间复盘账单，你会越来越清楚自己的钱流向哪里，慢慢建立稳定、舒服的消费节奏，慢慢攒出属于自己的安全感。"
        return f"恭喜你，现在你的收支结构比较健康，结余{rest:.0f}元，主要开销在{top}以及{('、'.join(top_list[1:])) if len(top_list)>1 else '其他日常支出'}。保持现在的节奏非常棒，同时我们还可以做一些优化，让财务状态更加稳妥。你可以给{top}这类消费预留一部分弹性预算，用来满足休闲、放松的需求，不用完全克制自己的正常享受，健康的预算不是压抑消费，而是让钱花得更明白。接下来可以规划长期储蓄目标，把结余分成两部分，一部分作为灵活备用金，一部分定向储蓄。继续坚持记账，定期回看账单，防止不知不觉抬高消费标准。良好的金钱观是长期积累的，你现在已经迈出很好的一步，持续保持下去，既能好好享受生活，又能稳步积攒存款，面对未来的各类选择时，也会拥有更多底气。"
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
        # 【新增：可编辑表格，修改分类】
        with st.expander("🔍 查看并修改账单分类明细", expanded=False):
            df = st.data_editor(df, use_container_width=True)

        res = analyze_finance(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 总收入", f"{res['总收入']:.2f} 元")
        col2.metric("💸 总支出", f"{res['总支出']:.2f} 元")
        col3.metric("📌 结余", f"{res['结余']:.2f} 元")

        st.divider()

        # 【修改：两张图表左右并排 col1, col2】
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
            cat_sum = None
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

        top3 = "、".join(cat_sum.index[:3]) if (cat_sum is not None and not cat_sum.empty) else ""
        st.caption(f"明细共 {len(df)} 条记录；支出主要花在：{top3}")

        st.divider()
        st.subheader("🤖 AI 消费建议")
        advice_mode = st.radio("选择 AI 风格", ["毒舌", "温柔"], horizontal=True)
        if st.button("生成消费建议"):
            with st.spinner("AI 思考中..."):
                st.markdown("### 📋 财务诊断与规划报告")
                st.info(get_ai_advice(res, top3, advice_mode))

    except Exception as e:
        st.error("❌ 文件处理失败：请检查表格是否为空、表头是否包含『日期 / 分类 / 金额 / 收支类型』。")
        st.caption(f"错误详情：{e}")
else:
    st.info("👈 请在左侧上传表格，或勾选「先用示例数据看一下效果」")
