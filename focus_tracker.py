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
FASTING_FILE = "fasting_log.csv"
DAILY_GOAL_HOURS = 5
WEEK_HOURS_RANGE = range(8, 24)  # 8:00 - 23:59 显示
FASTING_LIMIT_HOURS = 8


# ================== 主题样式 ==================
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
if not os.path.exists(FASTING_FILE):
    pd.DataFrame(columns=["date", "start_eat", "end_eat", "duration_hr"]).to_csv(FASTING_FILE, index=False)

df = pd.read_csv(DATA_FILE)
if not df.empty:
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

today_dt = datetime.now()
today = today_dt.date()


# ================== 顶部信息 ==================
weekday_cn = ['一','二','三','四','五','六','日'][today.weekday()]
year_week = today.isocalendar().week
month_week = (today.day - 1)//7 + 1
total_weeks = date(today.year, 12, 28).isocalendar().week
year_progress = (today - date(today.year,1,1)).days / (date(today.year + 1,1,1) - date(today.year,1,1)).days

st.markdown(f"<div class='big-date'>{today.strftime('%Y年%m月%d日')}（星期{weekday_cn}）</div>", unsafe_allow_html=True)
st.markdown(f"<div class='info-line'>📆 本月第 {month_week} 周 ｜ 今年第 {year_week}/{total_weeks} 周 ｜ 年进度 {(year_progress*100):.1f}%</div>", unsafe_allow_html=True)
st.progress(year_progress)


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


# ================== 专注打卡 ==================
st.subheader("⏱️ 专注打卡")
tag = st.text_input("当前任务标签（学习/编程/阅读...）", "学习")
c1, c2 = st.columns(2)
if "start_time" not in st.session_state:
    st.session_state.start_time = None

with c1:
    if st.button("▶️ 开始专注"):
        if st.session_state.start_time is None:
            st.session_state.start_time = datetime.now()
            st.toast("⚡ 心流启动！")
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
            if dur_hr >= 0.5: st.balloons()
            if dur_hr >= 1.0: st.snow()
            st.session_state.start_time = None
        else:
            st.warning("请先点击“开始专注”。")


# ================== XP 系统 ==================
st.subheader("🎮 成长系统（XP）")
if not df.empty:
    total_focus = float(df["duration_hr"].sum())
    xp = int(total_focus * 10)
    level = xp // 100
    next_xp = (level + 1) * 100 - xp
    st.markdown(f"<div class='xp-box'>等级 {level} ｜ 当前 XP：{xp} ｜ 距离升级还差：{next_xp} XP</div>", unsafe_allow_html=True)
    st.progress((xp % 100) / 100)
else:
    st.info("暂无专注记录，开始你的第一段专注吧 🌱")


# ================== 删除误记录 ==================
st.markdown("---")
st.subheader("🗑 删除误记录")
if not df.empty:
    df_display = df.sort_values("start_time", ascending=False).head(20)
    df_display["desc"] = df_display["start_time"].dt.strftime("%m-%d %H:%M") + " ~ " + df_display["end_time"].dt.strftime("%H:%M") + " ｜ " + df_display["tag"]
    delete_choice = st.selectbox("选择要删除的记录", ["（不删除）"] + df_display["desc"].tolist())

    if delete_choice != "（不删除）":
        if st.button("确认删除 🗑"):
            target = df_display[df_display["desc"] == delete_choice].iloc[0]
            df = df[df["start_time"] != target["start_time"]]
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ 已删除该记录！")
            st.rerun()


# ================== 每周专注表 ==================
st.subheader("📊 本周专注（按小时分布）")
if not df.empty:
    monday = today - timedelta(days=today.weekday())
    col_names = ["周一","周二","周三","周四","周五","周六","周日"]
    weekly_grid = pd.DataFrame(0.0, index=[f"{h:02d}:00" for h in WEEK_HOURS_RANGE], columns=col_names)

    def accumulate_by_hour(start_ts, end_ts):
        res = {h: 0.0 for h in WEEK_HOURS_RANGE}
        h_ptr = start_ts.replace(minute=0, second=0)
        while h_ptr < end_ts:
            next_hour = h_ptr + timedelta(hours=1)
            overlap = max(0.0, (min(end_ts, next_hour) - max(start_ts, h_ptr)).total_seconds()/3600)
            if h_ptr.hour in WEEK_HOURS_RANGE: res[h_ptr.hour] += overlap
            h_ptr = next_hour
        return res

    for offset in range(7):
        d = monday + timedelta(days=offset)
        day_start, day_end = datetime.combine(d, dtime(0,0)), datetime.combine(d, dtime(23,59))
        for _, r in df[(df["start_time"] < day_end) & (df["end_time"] > day_start)].iterrows():
            s, e = max(r["start_time"], day_start), min(r["end_time"], day_end)
            for h, val in accumulate_by_hour(s, e).items():
                weekly_grid.loc[f"{h:02d}:00", col_names[offset]] += val

    styled = weekly_grid.round(2).style.background_gradient(cmap="Greens").format("{:.2f}")
    st.dataframe(styled, use_container_width=True)
else:
    st.info("暂无数据。")


# ================== 🍎 轻断食追踪 ==================
st.subheader("🍎 轻断食打卡与热力格（16:8 Discipline Tracker）")

if os.path.exists(FASTING_FILE) and os.path.getsize(FASTING_FILE) > 0:
    fast_df = pd.read_csv(FASTING_FILE)
else:
    fast_df = pd.DataFrame(columns=["date", "start_eat", "end_eat", "duration_hr"])

if not fast_df.empty:
    fast_df["date"] = pd.to_datetime(fast_df["date"]).dt.date

st.markdown("**手动填写今天的进食时间**")
manual_date = st.date_input("📅 日期", today)
start_time = st.time_input("🍳 第一餐时间", dtime(14, 0))
end_time = st.time_input("🥦 最后一餐时间", dtime(22, 0))

if st.button("💾 保存记录"):
    start_dt, end_dt = datetime.combine(manual_date, start_time), datetime.combine(manual_date, end_time)
    dur_hr = (end_dt - start_dt).total_seconds() / 3600
    new_row = pd.DataFrame([[manual_date, start_dt, end_dt, dur_hr]], columns=["date","start_eat","end_eat","duration_hr"])
    fast_df = pd.concat([fast_df[fast_df["date"] != manual_date], new_row], ignore_index=True)
    fast_df.to_csv(FASTING_FILE, index=False)
    st.success(f"✅ 已保存！{manual_date} 进食 {dur_hr:.1f} 小时")

if not fast_df.empty:
    fast_df["status"] = fast_df["duration_hr"].apply(lambda x: 1 if x <= FASTING_LIMIT_HOURS else 0)
    merged = pd.DataFrame({"date": pd.date_range(date(today.year,1,1), date(today.year,12,31))})
    merged["date"] = pd.to_datetime(merged["date"]).dt.date
    merged = merged.merge(fast_df[["date","status"]], on="date", how="left")
    merged["iso_week"] = pd.to_datetime(merged["date"]).dt.isocalendar().week.astype(int)
    merged["dow"] = pd.to_datetime(merged["date"]).dt.weekday
    pivot = merged.groupby(["dow","iso_week"])["status"].mean().unstack()

    fig = go.Figure(data=go.Heatmap(
        z=pivot.fillna(-1).values,
        x=pivot.columns,
        y=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        colorscale=[[0.0, "#ff8b94"], [0.5, "#e9e9e9"], [1.0, "#a8e6cf"]],
        showscale=False,
    ))
    fig.update_layout(
        title=f"{today.year} 年 16:8 轻断食热力格",
        paper_bgcolor="#f6faf5",
        plot_bgcolor="#f6faf5",
        height=220,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)


# ================== 清空数据 ==================
st.markdown("---")
if st.button("🗑 清空所有记录（危险）"):
    if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
    st.rerun()
