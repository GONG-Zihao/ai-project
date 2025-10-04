import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

st.set_page_config(page_title="数据分析", page_icon="��", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("请先登录账号以使用数据分析功能！")
    st.stop()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

username = st.session_state['username']
user_file = DATA_DIR / f'user_{username}.json'

def load_user_data():
    if user_file.exists():
        with open(user_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

user_data = load_user_data()

user_profile = st.session_state.user_profile

# 页面标题
st.title("AI多模态个性化学习伴侣")
st.markdown("深入分析你的学习数据，发现学习规律！")

# 顶部显示本次学习已用时长
if st.session_state.get('session_start_time'):
    elapsed = datetime.now() - st.session_state['session_start_time']
    hours = elapsed.total_seconds() / 3600
    st.info(f"本次学习已用时长：{hours:.2f} 小时")

# 统计数据
study_time = user_profile.get_total_study_time()
study_days = user_profile.get_study_days()
daily_trend = user_profile.get_daily_study_trend()
hourly_dist = user_profile.get_hourly_distribution()

# 创建三个标签页
tab1, tab2, tab3 = st.tabs(["学习概览", "科目分析", "知识点分析"])

with tab1:
    st.header("学习概览")
    if study_time == 0:
        st.info("暂无学习数据，快去开始学习吧！")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总学习时长", f"{study_time:.1f}小时")
        with col2:
            st.metric("累计错题数", len(user_profile.data.get('mistakes', [])))
        with col3:
            st.metric("学习天数", study_days)
        st.subheader("学习时长趋势")
        if not daily_trend.empty:
            fig_time = px.line(daily_trend, x='date', y='duration',
                            title='每日学习时长趋势',
                            labels={'duration': '学习时长（小时）', 'date': '日期'})
            st.plotly_chart(fig_time, use_container_width=True)
        st.subheader("学习时间分布")
        if not hourly_dist.empty:
            fig_time_dist = px.bar(hourly_dist, x='hour', y='count',
                                title='学习时间分布',
                                labels={'hour': '小时', 'count': '学习会话数'})
            st.plotly_chart(fig_time_dist, use_container_width=True)

if not user_data:
    st.info("暂无学习数据，快去开始学习吧！")
else:
    with tab2:
        st.header("科目分析")
        if study_time == 0:
            st.info("暂无学习数据，快去开始学习吧！")
        else:
            # 动态获取所有科目
            all_subjects = list(set(m.get('subject', '未标注') for m in user_profile.data.get('mistakes', [])))
            if not all_subjects:
                st.info("暂无科目数据")
            else:
                selected_subject = st.selectbox("选择科目", all_subjects)
                # 该科目的错题
                subject_mistakes = [m for m in user_profile.data.get('mistakes', []) if m.get('subject', '未标注') == selected_subject]
                if not subject_mistakes:
                    st.info(f"暂无{selected_subject}科目的错题记录")
                else:
                    st.subheader("错题数量趋势")
                    df_mistakes = pd.DataFrame(subject_mistakes)
                    if 'timestamp' in df_mistakes:
                        df_mistakes['date'] = pd.to_datetime(df_mistakes['timestamp']).dt.date
                        fig_mistakes = px.line(df_mistakes.groupby('date').size().reset_index(),
                                             x='date', y=0,
                                             title='错题数量趋势',
                                             labels={'0': '错题数量', 'date': '日期'})
                        st.plotly_chart(fig_mistakes, use_container_width=True)
                    # 难度分布
                    if 'difficulty' in df_mistakes.columns:
                        fig_difficulty = px.pie(df_mistakes, names='difficulty',
                                              title='错题难度分布')
                        st.plotly_chart(fig_difficulty, use_container_width=True)

    with tab3:
        st.header("知识点分析")
        if study_time == 0:
            st.info("暂无学习数据，快去开始学习吧！")
        else:
            # 动态获取所有知识点
            all_knowledge = list(user_profile.data.get('knowledge_points', {}).keys())
            if not all_knowledge:
                st.info("暂无知识点数据")
            else:
                selected_knowledge = st.selectbox("选择知识点", all_knowledge)
                # 该知识点的错题
                knowledge_mistakes = [m for m in user_profile.data.get('mistakes', []) if m.get('knowledge', '') == selected_knowledge]
                if not knowledge_mistakes:
                    st.info(f"暂无{selected_knowledge}知识点的错题记录")
                else:
                    st.subheader("错题数量趋势")
                    df_km = pd.DataFrame(knowledge_mistakes)
                    if 'timestamp' in df_km:
                        df_km['date'] = pd.to_datetime(df_km['timestamp']).dt.date
                        fig_km = px.line(df_km.groupby('date').size().reset_index(),
                                        x='date', y=0,
                                        title=f'{selected_knowledge}错题数量趋势',
                                        labels={'0': '错题数量', 'date': '日期'})
                        st.plotly_chart(fig_km, use_container_width=True)
                    # 掌握程度
                    mastery = user_profile.data['knowledge_points'][selected_knowledge].get('mastery_level', 0)
                    st.metric("当前掌握程度(1-5)", mastery) 
