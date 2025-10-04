import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="学习计划", page_icon="📚", layout="wide")

# 使用明亮渐变纯色背景
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0eafc 100%);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 权限控制：未登录时强制返回首页
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("请先登录账号以使用该功能！")
    st.stop()

st.title("AI多模态个性化学习伴侣")
st.header("学习计划")

# 用户数据文件名（按用户名隔离）
username = st.session_state.get('username', 'default')
user_data_file = f'data/user_{username}.json'

# 读取用户数据
if os.path.exists(user_data_file):
    with open(user_data_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
else:
    user_data = {
        'learning_plan': [],
        'knowledge_points': {},
        'mistakes': [],
        'interactions': []
    }

# 显示学习计划
if user_data.get('learning_plan'):
    st.subheader("当前学习计划")
    remove_indices = []
    for idx, plan in enumerate(user_data['learning_plan']):
        st.markdown(f"**{plan['title']}**")
        st.markdown(plan['description'])
        st.markdown(f"预计完成时间：{plan['due_date']}")
        if st.button("计划已完成", key=f"plan_done_{idx}"):
            # 初始化已完成计划表单
            if 'completed_plan' not in user_data:
                user_data['completed_plan'] = []
            user_data['completed_plan'].append(plan)
            remove_indices.append(idx)
            st.success("该计划已归档到已完成表单！")
    # 实际移除已完成的计划
    if remove_indices:
        user_data['learning_plan'] = [p for i, p in enumerate(user_data['learning_plan']) if i not in remove_indices]
        with open(user_data_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        st.rerun()
    st.markdown("---")
else:
    st.info("暂无学习计划，快去制定吧！")

# 展示已完成计划
if user_data.get('completed_plan'):
    st.subheader("已完成计划")
    for plan in user_data['completed_plan']:
        st.markdown(f"**{plan['title']}**")
        st.markdown(plan['description'])
        st.markdown(f"完成时间：{plan.get('due_date', 'N/A')}")
        st.markdown("---")

# 添加新学习计划
st.subheader("添加新学习计划")
new_title = st.text_input("计划标题")
new_description = st.text_area("计划描述")
new_due_date = st.date_input("预计完成时间")

if st.button("添加计划"):
    if new_title and new_description:
        new_plan = {
            'title': new_title,
            'description': new_description,
            'due_date': new_due_date.strftime("%Y-%m-%d")
        }
        if 'learning_plan' not in user_data:
            user_data['learning_plan'] = []
        user_data['learning_plan'].append(new_plan)
        with open(user_data_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        st.success("学习计划已添加！")
        st.rerun()
    else:
        st.warning("请填写完整的计划信息！")

# 显示知识点掌握情况
if user_data.get('knowledge_points'):
    st.subheader("知识点掌握情况")
    knowledge_df = pd.DataFrame.from_dict(
        user_data['knowledge_points'],
        orient='index'
    )
    
    # 使用Plotly创建雷达图
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=knowledge_df['mastery_level'],
        theta=knowledge_df.index,
        fill='toself',
        name='掌握程度'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=False
    )
    st.plotly_chart(fig)
else:
    st.info("暂无知识点数据，快去学习吧！") 