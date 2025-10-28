# focus_neuro_v5_final.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time as dtime
import os

# ================== 文件路径固定 ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "focus_log.csv")
FASTING_FILE = os.path.join(BASE_DIR, "fasting_log.csv")

# ================== 页面与常量设置 ==================
st.set_page_config(page_title="Focus Tracker Neuro+ v5 🌿", layout="wide")
DAILY_GOAL_HOURS = 5
WEEK_HOURS_RANGE = range(8, 24)
FASTING_LIMIT_HOURS = 8

# ================== 样式 ==================
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
.xp-box {background: var(--soft2); color: var(--text); padding:1rem; border-radius:10px; border:1px solid #b7e4c7; text-align:center; font-size:1.05rem;}
</style>
""", unsafe_allow_html=True)

# ================== 初始化文件 ==================
def ensure_file(path, columns):
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)

ensure_file(DATA_FILE, ["start_time","end_time","duration_hr","tag"])
ensure_file(FASTING_FILE, ["date","start_eat","end_eat","duration_hr"])

# ================== 数据加载函数 ==================
def load_focus_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["start_time","end_time","duration_hr","tag"])
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return df
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
    return df.dropna(subset=["start_time","end_time"])

def save_focus_data(df):
    df.to_csv(DATA_FILE, index=False)

# ================== 初始化全局数据 ==================
if "df" not in st.session_state:
    st.session_state.df = load_focus_data()

df = st.session_state.df
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
st.caption(f"📁 当前 CSV 文件路径: {os.path.abspath(DATA_FILE)}")

# ================== 手动补录 ==================
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
        df_latest = load_focus_data()
        df_latest = pd.concat([df_latest, new_row], ignore_index=True)
        save_focus_data(df_latest)
        st.session_state.df = df_latest
        st.success(f"✅ 已保存：{manual_date} {manual_hour:02d}:00 起专注 {manual_minute} 分钟（{manual_tag}）")
        st.dataframe(df_latest.tail(5))
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
            df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_focus_data(df)
            st.session_state.df = df
            st.success(f"🎯 本次专注 {dur_hr:.2f} 小时")
            if dur_hr >= 0.5: st.balloons()
            if dur_hr >= 1.0: st.snow()
            st.session_state.start_time = None
        else:
            st.warning("请先点击“开始专注”。")

# ================== XP 系统 ==================
st.subheader("🎮 成长系统（XP）")
df = st.session_state.df
if not df.empty:
    total_focus = float(df["duration_hr"].sum())
    xp = int(total_focus * 10)
    level = xp // 100
    next_xp = (level + 1) * 100 - xp
    st.markdown(f"<div class='xp-box'>等级 {level} ｜ 当前 XP：{xp} ｜ 距离升级还差：{next_xp} XP</div>", unsafe_allow_html=True)
    st.progress((xp % 100) / 100)
else:
    st.info("暂无专注记录，开始你的第一段专注吧 🌱")

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
            if h_ptr.hour in WEEK_HOURS_RANGE:
                res[h_ptr.hour] += overlap
            h_ptr = next_hour
        return res

    for offset in range(7):
        d = monday + timedelta(days=offset)
        day_start, day_end = datetime.combine(d, dtime(0,0)), datetime.combine(d, dtime(23,59))
        for _, r in df[(df["start_time"] < day_end) & (df["end_time"] > day_start)].iterrows():
            s, e = max(r["start_time"], day_start), min(r["end_time"], day_end)
            for h, val in accumulate_by_hour(s, e).items():
                weekly_grid.loc[f"{h:02d}:00", col_names[offset]] += val

    st.dataframe(weekly_grid.round(2).style.background_gradient(cmap="Greens").format("{:.2f}"),
                 use_container_width=True)
else:
    st.info("暂无数据。")

# ================== 每日专注总时长 ==================
st.subheader("📅 每日专注总时长")
if not df.empty:
    df["date"] = df["start_time"].dt.date
    daily_summary = df.groupby("date")["duration_hr"].sum().reset_index()
    daily_summary = daily_summary.rename(columns={"duration_hr": "total_hours"}).sort_values("date", ascending=False)
    st.dataframe(daily_summary.style.format({"total_hours": "{:.2f}"}).background_gradient(cmap="Greens"),
                 use_container_width=True)
    avg_focus = daily_summary["total_hours"].mean()
    st.markdown(f"🧾 共记录 **{len(daily_summary)} 天** ｜ 平均每天专注 **{avg_focus:.2f} 小时**")
else:
    st.info("暂无数据，开始你的第一段专注吧 🌱")

# ================== 清空数据 ==================
st.markdown("---")
if st.button("🗑 清空所有记录（危险）"):
    os.remove(DATA_FILE)
    ensure_file(DATA_FILE, ["start_time","end_time","duration_hr","tag"])
    st.session_state.df = pd.DataFrame(columns=["start_time","end_time","duration_hr","tag"])
    st.success("✅ 所有记录已清空！")
    st.rerun()
