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
    """消费复盘文字，重写，去掉AI味道，单段≥400字"""
    income, out, rest = res["总收入"], res["总支出"], res["结余"]
    top_list = details.split("、") if details else []
    top = top_list[0] if top_list else "日常开销"

    if income <= 0:
        return "目前还没有登记任何收入记录，暂时没法客观评估你的开销节奏，也很难给出贴合你情况的收支规划。记账这件事里，收入才是所有预算安排的根基，如果只记录花出去的钱，却忽略所有进账，我们看到的消费情况就是片面的，参考价值会大打折扣。你可以慢慢把生活费、兼职酬劳、红包奖励、奖学金这类所有来源的收入都补充录入表格，等收入数据完整之后，才能准确算出每一类开销占收入的比重，看清哪些板块花钱偏多、哪些支出是可以适当调整的。不用急着一次性补齐所有历史记录，从当下开始持续记录就很好。等收支数据齐全，你就能慢慢摸索出适合自己的存钱节奏，学会在满足日常需求的同时，预留出一部分资金作为备用，避免之后遇到临时需要用钱的情况时手忙脚乱。坚持完整记录收支，也是慢慢建立稳定金钱观念的过程，长期下来，你会对自己的资金流向更加清楚，花钱的时候也会更有底气，而不是糊里糊涂，月底才发现钱已经全部用完。"

    rate = out / income * 100 if income else 0
    if mode == "直白提醒":
        if rate >= 90:
            return f"现在支出占到收入的{rate:.0f}%，几乎留不下什么积蓄，结余只有{rest:.0f}元，花钱大头是{top}，其次还有{('、'.join(top_list[1:])) if len(top_list)>1 else '其他零散开销'}，这样的消费状态容错空间非常小，需要及时重视。一旦之后出现突发的额外支出，比如生病买药、更换生活必需品、临时出行等等，你手里没有足够的备用资金，很容易陷入资金紧张、周转不开的困境。很多时候大额开销带来的压力很容易被察觉到，但恰恰是各类零散的小额消费，一点点蚕食掉大部分收入，很多人就是抱着单次花费不多的心态放松管控，最后不知不觉接近月光。优先给{top}这项支出设置一个硬性的月度花钱上限，每次准备消费之前，停下来想一想这件东西是不是当下真正刚需，区分清楚必须消费和一时兴起的冲动消费。现阶段正是建立长期消费习惯的关键时期，如果一直维持这种高消耗的模式，很难攒下属于自己的积蓄。哪怕每个月只是压缩一小部分非必要开支，慢慢积累，一段时间之后也会形成一笔可以兜底的备用金，不用一直处在有钱就花、月底空空的状态里。持续记账复盘，定期回看账单，也是在不断提醒自己把控消费节奏，不要放任消费欲望不受约束。"
        if rate >= 70:
            return f"本月开销占到收入的{rate:.0f}%，结余{rest:.0f}元，表面上看收支还能维持，但隐患已经慢慢显现出来，主要花费集中在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '和一些零碎支出'}。单独看每一笔支出好像都不算昂贵，可叠加在一起，就悄悄吃掉了你大部分收入，这也是很多人明明没买什么大件，月底却存不下钱的核心原因。你现在属于临界状态，只要再多一笔没有提前规划的额外消费，就很容易直接超支，打破现有的收支平衡。可以先给{top}这类弹性比较大的消费定好每月额度，严格对照额度控制开销，同时多留意奶茶零食、随手网购小件、短视频种草消费这类不起眼的小额支出，这类高频小额支出日积月累，累加起来也是一笔不容小觑的数目。存钱不要等到月底看剩下多少再存，尽量养成先预留储蓄资金，再安排其余消费的习惯。不用一下子大幅度缩减所有娱乐和放松的开销，那样很难长久坚持，重点是把无意义的冲动消费过滤掉，慢慢拉高每月结余的比例。坚持定期复盘账单，熟悉自己的消费偏好，一点点调整，慢慢把消费节奏稳定在更加安全舒服的区间。"
        return f"当前结余{rest:.0f}元，整体收支暂时处在稳妥区间，但绝对不能因此放松对消费的把控，大额支出集中在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '以及其他日常花费'}。很多人就是在收支平稳、还有结余的时候慢慢放松警惕，不自觉抬高自己的消费阈值，慢慢习惯更高的消费水平，等到想要再收紧开支、增加储蓄的时候，就会觉得很难适应。你可以试着把消费划分成刚需支出和享受型支出两大块，吃饭、基础生活用品这类刚需优先保障，而休闲娱乐、装饰好物这类享受型消费可以设置浮动上限，非急需的消费尽量延后一段时间再决定。哪怕当下资金宽裕，也不要随心情随意消费，每一笔开销尽量做到心里有数。记账和复盘的意义，不只是记录数字，更是帮你看清自己的消费偏好，找到可以优化的空间。你可以给自己定下一个温和的储蓄目标，每个月尽量稳定留存一部分收入，慢慢把储蓄比例拉高。手里持续保有结余，会给你很强的安全感，面对之后各类计划和突发情况，也会拥有更多选择，而不是被资金情况束缚住。保持持续记账复盘的习惯，慢慢打磨适合自己的长期消费模式。"
    else:
        if rate >= 90:
            return f"这个月开销占收入{rate:.0f}%，整体比例偏高，花钱集中在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '和一些零散支出'}，结余{rest:.0f}元，看到这个结果不用过度焦虑，我们可以循序渐进调整消费结构，不用苛刻地砍掉所有让自己开心的开销。可以优先从占比最高的{top}板块入手，给它设置一个比较温和的月度预算上限，在满足基础需求的前提下，慢慢减少冲动型消费。很多消费其实都来自当下的情绪，并不是本身真的需要这件物品，之后遇到想要下单的时候，可以试着先放一天，冷静之后再决定要不要购买，能避开很多没必要的支出。同时，可以慢慢搭建属于自己的小金库，应急备用金不需要一次性存入很大一笔钱，每个月能存下的结余优先放进去，积少成多，这笔资金可以用来应对突如其来的支出，避免临时缺钱带来的窘迫。记账本身就是一个慢慢认识自己花钱习惯的过程，改变消费节奏本来就不是一蹴而就的事情，不用追求一步到位。我们一点点梳理账单、优化开销，慢慢降低支出占收入的比重，在好好照顾自己日常生活的基础上，慢慢攒下积蓄，找到舒服、可持续的收支节奏。"
        if rate >= 70:
            return f"收支整体还算平稳，结余{rest:.0f}元，开销主要是{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '等项目'}，目前还有不小的优化空间，不用大刀阔斧改动现有的生活方式，一些细小的调整长期下来就会有很不错的效果。可以适度控制{top}这类弹性比较大的开销，分清哪些是维持生活必须要花的钱，哪些是用来取悦自己、放松心情的享受型消费，享受型的消费完全可以保留，只需要控制好频率和单次花费。随手产生的小额消费很容易被我们忽略，比如路上随手买的饮品、零食、刷手机时冲动下单的小东西，单次金额不高，但是购买频次高，累积起来也是一笔可观的支出。可以试着养成先存后花的习惯，每个月拿到收入之后，先划出固定一部分作为储蓄，剩下的资金再分配给各类日常开销。每隔一段时间回看一次完整账单，看清钱都流向了哪里，慢慢找到属于自己、没有压力的消费节奏。合理的消费规划不是压抑自己的需求，而是让每一笔钱都花得心甘情愿，既能好好享受当下的生活，也能稳步积攒存款，慢慢建立属于自己的资金安全感。"
        return f"很棒，目前你的收支结构比较健康，结余{rest:.0f}元，主要花费在{top}{('、' + '、'.join(top_list[1:])) if len(top_list)>1 else '以及其他日常支出'}，保持现在这个稳定的节奏非常难得，同时我们还可以继续微调，让财务状态更加稳妥。{top}这类休闲放松类的消费，可以预留一部分弹性预算，不用完全克制正常的娱乐需求，健康的预算管理从来不是压抑消费，而是让资金分配更均衡，该花的地方从容花，该存的钱稳定存。你可以把每月结余分成两个部分，一部分作为灵活备用金，用来应对计划之外的小额支出，另一部分定向长期储蓄，朝着自己的小目标慢慢积累。继续坚持记账，定期回看账单，有意识地留意自己会不会在不知不觉中抬高消费标准，很多人就是在状态不错的时候慢慢放宽要求，最后储蓄计划被打乱。稳定的金钱观念是长期一点点养出来的，不是短时间就能成型。你现在已经找到了不错的起点，持续保持复盘的习惯，在好好生活的同时稳步攒钱，未来不管是想要短途出行、购入心仪物品，还是应对突发状况，手里有存款，都会拥有更多从容选择的底气。"


# ===================== 页面配置 + 自定义CSS 美化字体、颜色 =====================
st.set_page_config(page_title="我的记账本", layout="wide")

custom_css = """
<style>
    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: "Microsoft YaHei", sans-serif;
    }
    h1, h2, h3, h4 {
        font-weight: 700 !important;
    }
    .small-note {
        font-size:14px; color:#636e72;
    }
    .card-shadow {
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# 渐变标题栏
st.markdown("""
<div style="padding:22px; background: linear-gradient(135deg, #74b9ff, #0984e3); border-radius:16px; color:white;" class="card-shadow">
    <h2 style="margin:0; font-size:28px;">我的记账本</h2>
    <p style="margin:8px 0 0; font-size:16px; opacity:0.92;">上传账单表格，查看收支汇总，梳理自己的花钱节奏</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# 侧边栏美化
with st.sidebar:
    st.markdown("""
    <div style="padding:14px; background:linear-gradient(135deg,#ffeaa7,#fdcb6e); border-radius:12px; color:#2d3436;">
        <h3 style="margin:0; font-size:18px;">账单文件</h3>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("上传表格", type=["csv", "xlsx"], help="表头需要包含：日期、分类、金额、收支类型")
    use_demo = st.checkbox("打开示例账单预览效果")
    st.markdown("""
    <div style="background:#dfe6e9; padding:12px; border-radius:10px; font-size:14px; color:#2d3436;">
    温馨提示<br>
    支持 csv / xlsx<br>
    收支类型填写：收入 / 支出
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
        st.error("文件读取失败，检查文件格式，不要在WPS/Excel里打开占用着文件。")
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
        st.markdown("""
        <div style="padding:12px; background:#a29bfe; border-radius:12px; color:white;">
            <h4 style="margin:0;">账单明细（可直接修改）</h4>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("点开查看、编辑每一笔记录", expanded=False):
            df = st.data_editor(df, use_container_width=True)

        st.divider()

        # 收支三色卡片
        res = analyze_finance(df)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#55efc4,#00b894); padding:24px; border-radius:14px; text-align:center;" class="card-shadow">
                <div style="font-size:15px; color:#2d3436; font-weight:500;">总收入</div>
                <div style="font-size:28px; font-weight:bold; color:#00694c;">{:.2f} 元</div>
            </div>
            """.format(res["总收入"]), unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#ff7675,#d63031); padding:24px; border-radius:14px; text-align:center;" class="card-shadow">
                <div style="font-size:15px; color:white; font-weight:500;">总支出</div>
                <div style="font-size:28px; font-weight:bold; color:white;">{:.2f} 元</div>
            </div>
            """.format(res["总支出"]), unsafe_allow_html=True)
        with c3:
            rest_color_bg = "linear-gradient(135deg,#74b9ff,#0984e3)" if res["结余"]>=0 else "linear-gradient(135deg,#fab1a0,#e17055)"
            text_color = "#003b70" if res["结余"]>=0 else "#8c2d18"
            st.markdown(f"""
            <div style="background:{rest_color_bg}; padding:24px; border-radius:14px; text-align:center;" class="card-shadow">
                <div style="font-size:15px; color:white; font-weight:500;">当前结余</div>
                <div style="font-size:28px; font-weight:bold; color:{text_color};">{res["结余"]:.2f} 元</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        # 图表标题栏
        st.markdown("""
        <div style="padding:12px; background:#fd79a8; border-radius:12px; color:white;">
            <h4 style="margin:0;">收支图表</h4>
        </div>
        """, unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            fig_pie = px.pie(
                values=[res["总收入"], res["总支出"]],
                names=["收入", "支出"],
                title="收入和支出占比",
                color_discrete_sequence=["#00b894", "#e17055"],
                hole=0.2
            )
            fig_pie.update_layout(title_x=0.5, font={"size":14})
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
                    color_discrete_sequence=["#0984e3"]
                )
                fig_bar.update_layout(yaxis=dict(autorange="reversed"), title_x=0.5, font={"size":14})
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("目前还没有支出记录")

        top3 = "、".join(cat_sum.index[:3]) if (cat_sum is not None and not cat_sum.empty) else ""
        st.markdown(f"<div style='color:#636e72; font-size:15px;'>一共 {len(df)} 条账单｜主要开销方向：{top3}</div>", unsafe_allow_html=True)

        st.divider()
        # 复盘板块
        st.markdown("""
        <div style="padding:12px; background:#00b894; border-radius:12px; color:white;">
            <h4 style="margin:0;">消费复盘参考</h4>
        </div>
        """, unsafe_allow_html=True)
        review_style = st.radio("选择复盘语气", ["毒舌", "温柔"], horizontal=True)
        run_review = st.button("生成复盘文字", type="primary")

        if run_review:
            st.markdown("""
            <div style="background:#fff; padding:22px; border-radius:14px; border:2px solid #74b9ff;" class="card-shadow">
            """, unsafe_allow_html=True)
            st.write(get_review_text(res, top3, review_style))
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error("账单处理出错，请检查表头：需要日期、分类、金额、收支类型")
        st.caption(f"详情：{e}")
else:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#dfe6e9,#b2bec3); padding:32px; border-radius:16px; text-align:center; color:#2d3436;" class="card-shadow">
    <p style="font-size:18px; font-weight:500;">在左侧上传你的记账表格，或者勾选示例账单先看看效果</p>
    </div>
    """, unsafe_allow_html=True)
