import streamlit as st
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="成就系统", page_icon="��", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("请先登录账号以使用成就系统功能！")
    st.stop()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

username = st.session_state['username']
user_file = DATA_DIR / f'user_{username}.json'

# 定义成就类型
ACHIEVEMENTS = {
    'study_time': {
        'name': '学习时长',
        'levels': [
            {'name': '初学者', 'requirement': 10, 'icon': '🌱'},
            {'name': '勤奋者', 'requirement': 50, 'icon': '🌿'},
            {'name': '专注者', 'requirement': 100, 'icon': '🌳'},
            {'name': '大师', 'requirement': 500, 'icon': '🌲'}
        ]
    },
    'continuous_days': {
        'name': '连续学习',
        'levels': [
            {'name': '坚持者', 'requirement': 3, 'icon': '🔥'},
            {'name': '毅力者', 'requirement': 7, 'icon': '⚡'},
            {'name': '习惯者', 'requirement': 30, 'icon': '🌟'},
            {'name': '传奇', 'requirement': 100, 'icon': '👑'}
        ]
    },
    'mistakes': {
        'name': '错题攻克',
        'levels': [
            {'name': '探索者', 'requirement': 10, 'icon': '🔍'},
            {'name': '挑战者', 'requirement': 50, 'icon': '💪'},
            {'name': '征服者', 'requirement': 100, 'icon': '🏆'},
            {'name': '完美者', 'requirement': 500, 'icon': '👑'}
        ]
    },
    'subjects': {
        'name': '学科精通',
        'levels': [
            {'name': '入门', 'requirement': 1, 'icon': '📚'},
            {'name': '熟练', 'requirement': 2, 'icon': '📖'},
            {'name': '精通', 'requirement': 3, 'icon': '🎓'},
            {'name': '全能', 'requirement': 5, 'icon': '🏅'}
        ]
    }
}

# 加载用户数据
def load_user_data():
    if user_file.exists():
        with open(user_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

user_data = load_user_data()

# 计算成就
def calculate_achievements(user_data):
    if not user_data:
        return {}
    
    achievements = {}
    
    # 计算学习时长成就
    total_study_time = sum(record['time'] for record in user_data.get('study_records', []))
    for level in ACHIEVEMENTS['study_time']['levels']:
        if total_study_time >= level['requirement']:
            achievements['study_time'] = {
                'name': level['name'],
                'icon': level['icon'],
                'progress': min(100, total_study_time / level['requirement'] * 100)
            }
    
    # 计算连续学习成就
    if user_data.get('study_records'):
        dates = sorted(set(record['date'] for record in user_data['study_records']))
        max_streak = 0
        current_streak = 1
        for i in range(1, len(dates)):
            if (datetime.fromisoformat(dates[i]) - 
                datetime.fromisoformat(dates[i-1])).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        for level in ACHIEVEMENTS['continuous_days']['levels']:
            if max_streak >= level['requirement']:
                achievements['continuous_days'] = {
                    'name': level['name'],
                    'icon': level['icon'],
                    'progress': min(100, max_streak / level['requirement'] * 100)
                }
    
    # 计算错题成就
    total_mistakes = len(user_data.get('mistakes', []))
    for level in ACHIEVEMENTS['mistakes']['levels']:
        if total_mistakes >= level['requirement']:
            achievements['mistakes'] = {
                'name': level['name'],
                'icon': level['icon'],
                'progress': min(100, total_mistakes / level['requirement'] * 100)
            }
    
    # 计算学科成就
    subjects = set(record.get('subject') for record in user_data.get('study_records', []))
    for level in ACHIEVEMENTS['subjects']['levels']:
        if len(subjects) >= level['requirement']:
            achievements['subjects'] = {
                'name': level['name'],
                'icon': level['icon'],
                'progress': min(100, len(subjects) / level['requirement'] * 100)
            }
    
    return achievements

# 页面标题
st.title("AI多模态个性化学习伴侣")
st.markdown("展示你的学习成就，激励持续进步！")

if not user_data:
    st.info("暂无学习数据，快去开始学习吧！")
else:
    # 计算成就
    achievements = calculate_achievements(user_data)
    
    # 显示成就卡片
    st.header("我的成就")
    
    # 创建成就卡片样式
    st.markdown("""
    <style>
    .achievement-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .achievement-icon {
        font-size: 2em;
        margin-bottom: 10px;
    }
    .achievement-name {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .achievement-progress {
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 显示成就卡片
    cols = st.columns(2)
    for i, (achievement_type, achievement) in enumerate(achievements.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="achievement-card">
                <div class="achievement-icon">{achievement['icon']}</div>
                <div class="achievement-name">{ACHIEVEMENTS[achievement_type]['name']} - {achievement['name']}</div>
                <div class="achievement-progress">
                    <div class="stProgress">
                        <div class="stProgressBar" style="width: {achievement['progress']}%"></div>
                    </div>
                    <div style="text-align: right">{achievement['progress']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 显示成就进度
    st.header("成就进度")
    
    # 创建进度数据
    progress_data = []
    for achievement_type, achievement in ACHIEVEMENTS.items():
        current_level = achievements.get(achievement_type, {}).get('progress', 0)
        progress_data.append({
            '成就类型': achievement['name'],
            '当前进度': current_level
        })
    
    # 创建进度图
    if progress_data:
        df_progress = pd.DataFrame(progress_data)
        fig = px.bar(df_progress, x='成就类型', y='当前进度',
                    title='各类型成就进度',
                    labels={'当前进度': '完成度 (%)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # 显示未解锁成就
    st.header("待解锁成就")
    
    for achievement_type, achievement in ACHIEVEMENTS.items():
        if achievement_type not in achievements:
            st.markdown(f"### {achievement['name']}")
            for level in achievement['levels']:
                st.markdown(f"- {level['icon']} {level['name']} ({level['requirement']})")
    
    # 显示最近获得的成就
    st.header("最近获得的成就")
    
    # 这里可以添加最近获得成就的逻辑
    # 需要记录成就获得的时间戳
    
    # 显示成就统计
    st.header("成就统计")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("已获得成就", len(achievements))
    with col2:
        st.metric("总成就数", len(ACHIEVEMENTS)) 
