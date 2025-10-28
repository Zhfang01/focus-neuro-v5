# focus_neuro_v5.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time as dtime
import os, random, time, webbrowser



# ================== 基础设置 ==================
st.set_page_config(page_title="Focus Tracker Neuro+ v5 🌿", layout="wide")
DATA_FILE = "focus_log.csv"
DAILY_GOAL_HOURS = 5
WEEK_HOURS_RANGE = range(8, 24)  # 8:00 - 23:59 显示


# --- 简易密码保护 ---
st.session_state["authenticated"] = st.session_state.get("authenticated", False)

if not st.session_state["authenticated"]:
    pwd = st.text_input("请输入访问密码：", type="password")
    if pwd == "2001":
        st.session_state["authenticated"] = True
        st.success("✅ 验证成功！")
        st.rerun()
    elif pwd != "":
        st.error("❌ 密码错误，请重试。")
    st.stop()  # ⛔️ 阻止页面继续加载

# ================== 主题样式（Calm 绿白） ==================
st.markdown("""
<style>
:root {
  --bg: #f6faf5;
  --text: #1b4332;
  --accent: #2e8b57;
  --soft: #e9f5ec;
  --soft2: #e3f2e1;
  --border: #cdeac0;
}
body {background-color: var(--bg); color: #2d2d2d; font-family: 'Microsoft YaHei',sans-serif;}
h1,h2,h3 {color: #228b22; font-weight:600;}
.big-date {font-size:2rem; font-weight:700; text-align:center; color: var(--accent);}
.info-line {text-align:center; color: var(--accent); font-size:1.05rem;}
.box {background: var(--soft); color: var(--text); padding: 1rem; border-radius:10px; border: 1px solid var(--border);}
.xp-box {background: var(--soft2); color: var(--text); padding:1rem; border-radius:10px; border:1px solid #b7e4c7; text-align:center; font-size:1.05rem;}
.breath-circle { width:120px; height:120px; border-radius:50%; margin:auto; background-color:#95d5b2; transition: all 2s ease-in-out; }
th, td { color:#2d2d2d !important; }
</style>
""", unsafe_allow_html=True)

# ================== 初始化数据 ==================
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["start_time","end_time","duration_hr","tag"]).to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)
if not df.empty:
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

# Session state
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "prompt_breath_after_focus" not in st.session_state:
    st.session_state.prompt_breath_after_focus = False

today_dt = datetime.now()
today = today_dt.date()

# ================== 顶部信息（日期 + 年度进度） ==================
weekday_cn = ['一','二','三','四','五','六','日'][today.weekday()]
year_week = today.isocalendar().week
month_week = (today.day - 1)//7 + 1
total_weeks = date(today.year, 12, 28).isocalendar().week
year_progress = (today - date(today.year,1,1)).days / (date(today.year + 1,1,1) - date(today.year,1,1)).days

st.markdown(f"<div class='big-date'>{today.strftime('%Y年%m月%d日')}（星期{weekday_cn}）</div>", unsafe_allow_html=True)
st.markdown(f"<div class='info-line'>📆 本月第 {month_week} 周 ｜ 今年第 {year_week}/{total_weeks} 周 ｜ 年进度 {(year_progress*100):.1f}%</div>", unsafe_allow_html=True)
st.progress(year_progress)

# ================== 多巴胺图片（动物 & 自然） ==================
dopamine_images = [
    # 动物
    "https://images.unsplash.com/photo-1504208434309-cb69f4fe52b0",  # 狗
    "https://images.unsplash.com/photo-1508675801634-7b9e1a1e20f6",  # 猫
    "https://images.unsplash.com/photo-1551334787-21e6bd3ab135",    # 企鹅
    "https://images.unsplash.com/photo-1501706362039-c6e80948d04e",  # 小鸟
    "https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13",  # 鹿
    "https://images.unsplash.com/photo-1518791841217-8f162f1e1131",  # 狗狗
    "https://images.unsplash.com/photo-1546182990-dffeafbe841d",    # 大象
    "https://images.unsplash.com/photo-1516912481808-3406841bd33c",  # 火烈鸟
    # 自然
    "https://images.unsplash.com/photo-1501785888041-af3ef285b470",  # 山
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",  # 海
    "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429",  # 森林
    "https://images.unsplash.com/photo-1483683804023-6ccdb62f86ef",  # 草原
    "https://images.unsplash.com/photo-1518831959642-40d38b7b6a2d",  # 花田
    "https://images.unsplash.com/photo-1465101162946-4377e57745c3",  # 瀑布
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",  # 林间阳光
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e",  # 星空
]
col_img, _, _ = st.columns([1, 2, 2])
with col_img:
    st.image(random.choice(dopamine_images), caption="🌿 一眼心情好起来", width=320)

# ================== 手动补录专注 ==================
st.subheader("📝 手动补录专注记录")

with st.expander("展开填写手动记录"):
    manual_date = st.date_input("选择日期", today)
    manual_hour = st.selectbox("选择小时段（24小时制）", list(range(0, 24)), index=today_dt.hour)
    manual_minute = st.number_input("专注时长（分钟）", min_value=1, max_value=300, value=30)
    manual_tag = st.text_input("任务标签", "学习")

    if st.button("💾 保存手动记录"):
        start_time = datetime.combine(manual_date, dtime(manual_hour, 0))
        end_time = start_time + timedelta(minutes=manual_minute)
        dur_hr = manual_minute / 60.0

        new_row = pd.DataFrame([[start_time, end_time, dur_hr, manual_tag]],
                               columns=["start_time", "end_time", "duration_hr", "tag"])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"✅ 已保存：{manual_date} {manual_hour:02d}:00 起专注 {manual_minute} 分钟（{manual_tag}）")
        st.balloons()


# ================== 专注打卡区 ==================
st.subheader("⏱️ 专注打卡")
tag = st.text_input("当前任务标签（学习/编程/阅读...）", "学习")
c1, c2 = st.columns(2)
with c1:
    if st.button("▶️ 开始专注"):
        if st.session_state.start_time is None:
            st.session_state.start_time = datetime.now()
            st.toast("⚡ 心流启动！")
            try:
                webbrowser.open("https://www.youtube.com/results?search_query=lofi+study+music")
            except:
                pass
        else:
            st.warning("已在计时中，请先结束。")
with c2:
    if st.button("⏹️ 结束专注"):
        if st.session_state.start_time:
            end_time = datetime.now()
            dur_hr = (end_time - st.session_state.start_time).total_seconds()/3600
            new_row = pd.DataFrame([[st.session_state.start_time, end_time, dur_hr, tag]],
                                   columns=["start_time","end_time","duration_hr","tag"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"🎯 本次专注 {dur_hr:.2f} 小时")
            # 即时奖励
            if dur_hr >= 0.5: st.balloons()
            if dur_hr >= 1.0: st.snow()
            if random.random() < 0.15:
                st.success("🎁 惊喜奖励：额外 +10 XP！")
            st.session_state.start_time = None
            # 提醒进入呼吸恢复
            st.session_state.prompt_breath_after_focus = True
        else:
            st.warning("请先点击“开始专注”。")

# ================== XP 等级系统 ==================
st.subheader("🎮 成长系统（XP）")
if not df.empty:
    total_focus = float(df["duration_hr"].sum())
    xp = int(total_focus * 10)  # 1 小时 = 10 XP
    level = xp // 100
    next_xp = (level + 1) * 100 - xp
    st.markdown(f"<div class='xp-box'>等级 {level} ｜ 当前 XP：{xp} ｜ 距离升级还差：{next_xp} XP</div>", unsafe_allow_html=True)
    st.progress((xp % 100) / 100)
else:
    st.info("暂无专注记录，开始你的第一段专注吧 🌱")



# ================== 🌳 森林成长系统 ==================
# ================== 🌳 真·森林田地视图 ==================
st.subheader("🌳 我的专注森林（真实田地视图）")

if not df.empty:
    df["year"] = df["start_time"].dt.year
    df["date"] = df["start_time"].dt.date
    df["minutes"] = (df["end_time"] - df["start_time"]).dt.total_seconds() / 60

    # 种树条件：≥40分钟
    tree_df = df[df["minutes"] >= 40].copy()
    if tree_df.empty:
        st.info("🌱 你还没有种树呢。每满40分钟专注，就能在森林中种下一棵树！")
    else:
        # 不同时长的树类型
        def get_tree_symbol(mins):
            if mins < 60:
                return "🌱"  # 小树苗
            elif mins < 120:
                return "🌲"  # 中等松树
            else:
                return "🌳"  # 大树
        tree_df["tree"] = tree_df["minutes"].apply(get_tree_symbol)

        years = sorted(tree_df["year"].unique())
        for y in years:
            st.markdown(f"### 🍀 {y} 年专注森林")
            year_trees = tree_df[tree_df["year"] == y]["tree"].tolist()

            # 将树按8棵一行排布
            rows = [year_trees[i:i+8] for i in range(0, len(year_trees), 8)]
            field_html = "<div style='font-size:2rem;line-height:2.5rem;background:#e9f5ec;border-radius:10px;padding:10px;text-align:center;'>"
            for row in rows:
                field_html += "".join(row) + "<br>"
            field_html += "</div>"
            st.markdown(field_html, unsafe_allow_html=True)

            st.caption(f"共 {len(year_trees)} 棵树 🌳")
else:
    st.info("暂无数据。完成专注后，你的第一棵树就会出现在森林里 🌱。")


# ================== 工具函数：区间按小时切分累计 ==================
def accumulate_by_hour(start_ts: datetime, end_ts: datetime, hours_range=WEEK_HOURS_RANGE):
    """
    返回一个 dict: {hour: hours_spent_in_that_hour}，只统计给定 hours_range 内的时间。
    精确按重叠时长切分（比如 08:30-10:15 会在 8 点加 0.5h，在 9 点加 1h，在 10 点加 0.25h）。
    """
    res = {h: 0.0 for h in hours_range}
    # 遍历每个小时槽
    current = datetime.combine(start_ts.date(), dtime(min(hours_range), 0))
    # 起点小于任务开始
    current = max(current, start_ts.replace(minute=0, second=0, microsecond=0))
    # 遍历从 start_ts 小时到 end_ts 小时
    slot_start = datetime.combine(start_ts.date(), dtime(hours_range.start, 0))
    slot_end = datetime.combine(start_ts.date(), dtime(hours_range.stop - 1, 59, 59, 999999))
    # 扩到跨天情况
    s = start_ts
    e = end_ts
    # 切分跨天（如果有的话，只取当天可视范围；周表按天汇总会分别处理）
    # 这里仅负责单条记录在当天的小时内部分配，因此上层会按天循环。
    # 计算从记录开始到结束逐小时分配
    h_ptr = datetime(s.year, s.month, s.day, s.hour, 0, 0)
    while h_ptr < e:
        next_hour = h_ptr + timedelta(hours=1)
        overlap_start = max(s, h_ptr)
        overlap_end = min(e, next_hour)
        hours = max(0.0, (overlap_end - overlap_start).total_seconds() / 3600)
        if h_ptr.hour in hours_range and hours > 0:
            res[h_ptr.hour] += hours
        h_ptr = next_hour
    return res

# ================== 每周小时表（周一开始，列=周一到周日，行=8-23点） ==================
st.subheader("📊 本周专注（周一开始，按小时分布）")
if not df.empty:
    # 定位当周（周一~周日）
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    # 初始化表格
    col_names = ["周一","周二","周三","周四","周五","周六","周日"]
    weekly_grid = pd.DataFrame(0.0, index=[f"{h:02d}:00" for h in WEEK_HOURS_RANGE], columns=col_names)

    # 逐天处理
    for offset in range(7):
        d = monday + timedelta(days=offset)
        day_start = datetime.combine(d, dtime(0,0,0))
        day_end = day_start + timedelta(days=1)

        day_rows = df[(df["start_time"] < day_end) & (df["end_time"] > day_start)]
        # 把该日内记录截断到当天范围内
        for _, r in day_rows.iterrows():
            s = max(r["start_time"], day_start)
            e = min(r["end_time"], day_end)
            by_hour = accumulate_by_hour(s, e, WEEK_HOURS_RANGE)
            for h, val in by_hour.items():
                weekly_grid.loc[f"{h:02d}:00", col_names[offset]] += val

    weekly_grid = weekly_grid.round(2)

    # 今日列高亮提示（表头后加“(今天)”）
    today_col_index = today.weekday()  # 0=Mon
    display_cols = col_names.copy()
    display_cols[today_col_index] = display_cols[today_col_index] + "（今天）"

    # 显示
    styled = (weekly_grid
              .set_axis(display_cols, axis=1)
              .style.background_gradient(cmap="Greens")
              .format("{:.2f}"))
    st.dataframe(styled, use_container_width=True)

    # 汇总条
    week_total = weekly_grid.values.sum()
    today_total = weekly_grid.iloc[:, today_col_index].sum()
    st.markdown(
        f"<div class='box'>🧾 周累计：<b>{week_total:.2f}</b> 小时 ｜ 今日累计：<b>{today_total:.2f}</b> 小时</div>",
        unsafe_allow_html=True
    )
else:
    st.info("暂无数据。开始记录，看看这一周你的节奏。")

# ================== 年度 GitHub 风格热力格 ==================
st.subheader("🗓️ 年度专注热力格（GitHub 风格）")
if not df.empty:
    df["date"] = df["start_time"].dt.date
    daily = df.groupby("date")["duration_hr"].sum().reset_index()

    # 今年的所有日期
    start_of_year = date(today.year, 1, 1)
    end_of_year = date(today.year, 12, 31)
    all_days = pd.date_range(start_of_year, end_of_year, freq="D")
    
    merged = pd.DataFrame({"date": all_days})
    daily["date"] = pd.to_datetime(daily["date"])
    merged["date"] = pd.to_datetime(merged["date"])
    merged = merged.merge(daily, on="date", how="left").fillna({"duration_hr": 0.0})


    # ISO 周 & 周几（周一=0）
    merged["iso_week"] = merged["date"].dt.isocalendar().week.astype(int)
    merged["dow"] = merged["date"].dt.weekday

    # 处理年初落在上一年的 ISO 周（比如 Jan 1 属于上一年第 52/53 周）
    # 统一将属于上一年的 ISO 周归为第 1 列（视觉连续即可）
    min_week = merged.loc[merged["date"].dt.month == 1, "iso_week"].min()
    if min_week > 10:  # 典型 52/53
        merged.loc[merged["date"].dt.month == 1, "iso_week"] = 1

    pivot = merged.pivot_table(
    index="dow", 
    columns="iso_week", 
    values="duration_hr", 
    aggfunc="sum"  # 解决重复冲突：同一周同一天的小时数相加
).sort_index()


    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        colorscale=[[0, "#e9f5ec"], [1, "#2e8b57"]],
        hoverongaps=False,
        colorbar=dict(title="小时")
    ))
    fig.update_layout(
        title=f"{today.year} 年专注格图",
        paper_bgcolor="#f6faf5",
        plot_bgcolor="#f6faf5",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("暂无年度数据。")

# ================== 🧘 正念中心：呼吸引导 + 冥想计时 ==================
st.subheader("🧘 正念中心（Mindful Center）")
tab1, tab2 = st.tabs(["🌬️ 呼吸引导", "🌊 冥想计时"])

with tab1:
    st.markdown("<h4 style='text-align:center;color:#1b4332;'>吸气 4 秒 → 停 2 秒 → 呼气 4 秒 → 停 2 秒</h4>", unsafe_allow_html=True)

    # 若刚结束专注，提示做一轮呼吸
    if st.session_state.prompt_breath_after_focus:
        st.info("🌿 刚刚结束专注，来一轮 1 分钟呼吸放松？")
        st.session_state.prompt_breath_after_focus = False

    if st.button("开始 1 分钟呼吸 🕯️"):
        placeholder = st.empty()
        # 1 分钟 ≈ 12 秒 x 5
        for i in range(20):  # 2s/步，20步=40s（更轻量），你可改为30步=60s
            phase = i % 4
            if phase == 0:      # 吸气
                text, size = "🌬️ 吸气...", 200
            elif phase == 1:    # 停顿
                text, size = "⏸️ 停顿...", 200
            elif phase == 2:    # 呼气
                text, size = "💨 呼气...", 80
            else:               # 停顿
                text, size = "⏸️ 停顿...", 80
            html = f"""
            <div style='text-align:center;'>
              <div class='breath-circle' style='width:{size}px;height:{size}px;'></div>
              <p style='font-size:1.2rem;color:#1b4332;'>{text}</p>
            </div>
            """
            placeholder.markdown(html, unsafe_allow_html=True)
            time.sleep(2)
        placeholder.markdown("<h4 style='text-align:center;color:#1b4332;'>✅ 呼吸完成，平静回归。</h4>", unsafe_allow_html=True)

with tab2:
    duration = st.selectbox("选择冥想时长（分钟）", [3, 5, 10], index=1)
    if st.button("开始冥想 🌙"):
        st.toast("静坐片刻，把注意力放在呼吸上。")
        placeholder = st.empty()
        end_time = datetime.now() + timedelta(minutes=duration)
        while datetime.now() < end_time:
            remaining = int((end_time - datetime.now()).total_seconds())
            mins, secs = divmod(remaining, 60)
            placeholder.markdown(f"<h3 style='text-align:center;color:#1b4332;'>⏳ 剩余时间：{mins:02d}:{secs:02d}</h3>", unsafe_allow_html=True)
            time.sleep(1)
        placeholder.markdown("<h3 style='text-align:center;color:#2e8b57;'>✅ 冥想完成</h3>", unsafe_allow_html=True)
        st.balloons()



# ================== 🍽️ 轻断食追踪（16:8 模式） ==================
# ================== 🍎 轻断食纪律追踪（含手动输入 + 热力格） ==================
st.subheader("🍎 轻断食打卡与热力格（16:8 Discipline Tracker）")

FASTING_FILE = "fasting_log.csv"
FASTING_LIMIT_HOURS = 8

# ---------- 初始化文件 ----------
if os.path.exists(FASTING_FILE) and os.path.getsize(FASTING_FILE) > 0:
    fast_df = pd.read_csv(FASTING_FILE)
else:
    fast_df = pd.DataFrame(columns=["date", "start_eat", "end_eat", "duration_hr"])


# ---------- 读取数据 ----------
fast_df = pd.read_csv(FASTING_FILE)
if not fast_df.empty:
    fast_df["date"] = pd.to_datetime(fast_df["date"]).dt.date
else:
    fast_df = pd.DataFrame(columns=["date", "start_eat", "end_eat", "duration_hr"])

# ---------- 手动输入 ----------
st.markdown("**手动填写今天的进食时间**")
manual_date = st.date_input("📅 日期", today)
start_time = st.time_input("🍳 第一餐时间", dtime(14, 0))
end_time   = st.time_input("🥦 最后一餐时间", dtime(22, 0))

if st.button("💾 保存记录"):
    start_dt = datetime.combine(manual_date, start_time)
    end_dt   = datetime.combine(manual_date, end_time)
    dur_hr   = (end_dt - start_dt).total_seconds() / 3600
    new_row = pd.DataFrame([[manual_date, start_dt, end_dt, dur_hr]],
                           columns=["date","start_eat","end_eat","duration_hr"])

    # 去重 + 覆盖同日
    fast_df = pd.concat([fast_df[fast_df["date"] != manual_date], new_row], ignore_index=True)
    fast_df.to_csv(FASTING_FILE, index=False)
    if dur_hr <= FASTING_LIMIT_HOURS:
        st.success(f"✅ 已保存！{manual_date} 进食 {dur_hr:.1f} 小时 —— 成功完成 16:8 🍏")
    else:
        st.error(f"⚠️ 已保存，但进食 {dur_hr:.1f} 小时 —— 超出 8 小时限制")

# ---------- 构建热力格 ----------
if not fast_df.empty:
    # 聚合去重，取每天最后记录
    fast_df = fast_df.sort_values("date").groupby("date", as_index=False).last()

    # 成功与否标记
    fast_df["status"] = fast_df["duration_hr"].apply(
        lambda x: 1 if pd.notna(x) and x <= FASTING_LIMIT_HOURS else
                  (0 if pd.notna(x) and x > FASTING_LIMIT_HOURS else np.nan)
    )

    # 补全年日期
    start_of_year = date(today.year, 1, 1)
    end_of_year = date(today.year, 12, 31)
    all_days = pd.date_range(start_of_year, end_of_year, freq="D")
    merged = pd.DataFrame({"date": all_days})
    merged["date"] = pd.to_datetime(merged["date"]).dt.date
    merged = merged.merge(fast_df[["date","status"]], on="date", how="left")

    # ISO周 & 周几
    merged["iso_week"] = pd.to_datetime(merged["date"]).dt.isocalendar().week.astype(int)
    merged["dow"] = pd.to_datetime(merged["date"]).dt.weekday

    # pivot 防止重复
    merged = merged.drop_duplicates(subset=["date"])
    pivot = merged.pivot(index="dow", columns="iso_week", values="status")

    # 构造颜色：绿=成功，红=失败，灰=未打卡
    z = pivot.fillna(-1).values
    color_scale = [[0.0, "#ff8b94"], [0.5, "#e9e9e9"], [1.0, "#a8e6cf"]]

    # ---------- 绘制 Plotly Heatmap ----------
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=pivot.columns,
        y=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        colorscale=color_scale,
        showscale=False,
        hovertemplate="周%{x}, %{y}<extra></extra>"
    ))
    fig.update_layout(
        title=f"{today.year} 年 16:8 轻断食热力格",
        paper_bgcolor="#f6faf5",
        plot_bgcolor="#f6faf5",
        xaxis=dict(showgrid=False, tickmode="linear"),
        yaxis=dict(showgrid=False),
        height=220,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 统计
    total_days = merged["status"].notna().sum()
    success_days = (merged["status"] == 1).sum()
    rate = success_days / total_days * 100 if total_days > 0 else 0
    st.markdown(f"📊 本年打卡天数：**{total_days}** ｜ 成功：**{success_days}** 天（{rate:.1f}%）")
else:
    st.info("暂无断食数据，先填写一条记录吧 🍎")

# ================== 清空数据（谨慎） ==================
st.markdown("---")
if st.button("🗑 清空所有记录（危险）"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.experimental_rerun()
