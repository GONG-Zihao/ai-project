import asyncio
import os
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ai_core import ai_answer, knowledge_graph
from api_client import api_client
from user_data import (
    UserProfile,
    is_valid_password,
    is_valid_phone,
    is_valid_username,
    load_user_data,
    register_user,
    save_user_data,
    validate_login,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
USE_BACKEND = api_client.is_enabled()

st.set_page_config(page_title="AI个性化学习助手", page_icon="📚", layout="wide")

# 使用明亮渐变纯色背景
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0eafc 100%);
    }
    .achievement-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .achievement-gold {
        border-left: 5px solid #FFD700;
    }
    .achievement-silver {
        border-left: 5px solid #C0C0C0;
    }
    .achievement-bronze {
        border-left: 5px solid #CD7F32;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'user_profile' not in st.session_state or st.session_state.get('last_user') != st.session_state.get('username'):
    st.session_state.user_profile = UserProfile(user_id=st.session_state.get('username', 'default'))
    st.session_state.last_user = st.session_state.get('username', 'default')
    st.session_state['last_question'] = None
    st.session_state['last_answer'] = None
    # 新增：登录后自动开始学习会话
    if st.session_state.get('logged_in', False):
        st.session_state.user_profile.start_session()
        st.session_state['session_start_time'] = datetime.now()
        st.session_state['last_session_update'] = datetime.now()
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''

# 侧边栏导航（受控导航，未登录时只能选首页）
PAGES = ["首页", "AI答疑", "错题本", "学习建议", "学习进度", "学习成就"]
if 'page' not in st.session_state:
    st.session_state.page = "首页"
if 'page_radio' not in st.session_state:
    st.session_state.page_radio = "首页"

def set_page():
    st.session_state.page = st.session_state.page_radio

selected = st.sidebar.radio(
    "导航", PAGES,
    index=PAGES.index(st.session_state.get('page', '首页')),
    key='page_radio',
    on_change=set_page
)

# 用户数据文件名（按用户名隔离）
def get_user_data_file():
    username = st.session_state.get('username', 'default')
    return str(DATA_DIR / f'user_{username}.json')

# 权限控制：未登录时只允许首页和学习社区
protected_pages = ["AI答疑", "错题本", "学习建议", "学习进度", "学习成就"]
if not st.session_state['logged_in'] and st.session_state.page in protected_pages:
    st.session_state.page = "首页"
    st.session_state.show_login_modal = True
else:
    st.session_state.page = st.session_state.page_radio
    st.session_state.show_login_modal = False

api_key = st.sidebar.text_input("DeepSeek API Key", type="password", help="用于调用AI答疑功能，建议仅用于本地测试")

# 全屏弹窗提示（Streamlit 1.25+ 支持st.modal，否则用st.warning+st.stop）
if not st.session_state['logged_in'] and st.session_state.get('show_login_modal', False):
    try:
        with st.modal("请先登录账号"):
            st.write("登录账号以使用该功能！")
            st.button("我知道了", on_click=lambda: st.session_state.update({'show_login_modal': False}))
            st.stop()
    except Exception:
        st.warning("登录账号以使用该功能！")
        st.stop()

# Login/Registration UI
if not st.session_state['logged_in']:
    st.title("AI多模态个性化学习伴侣")
    if 'show_register' not in st.session_state:
        st.session_state['show_register'] = False
    if st.session_state['show_register']:
        st.subheader("注册")
        reg_username = st.text_input("用户名", key="reg_username")
        reg_password = st.text_input("密码", type="password", key="reg_password")
        reg_phone = st.text_input("手机号", key="reg_phone")
        if st.button("注册", key="reg_button"):
            success, msg = register_user(reg_username, reg_password, reg_phone)
            if success:
                st.success(msg)
            else:
                st.error(msg)
        if st.button("已有账号？返回登录", key="to_login"):
            st.session_state['show_register'] = False
            st.rerun()
    else:
        st.subheader("登录")
        login_username = st.text_input("用户名", key="login_username")
        login_password = st.text_input("密码", type="password", key="login_password")
        tenant_slug = st.text_input("学校/租户标识", value=st.session_state.get('tenant', 'default')) if USE_BACKEND else 'default'
        if st.button("登录", key="login_button"):
            if USE_BACKEND:
                try:
                    resp = asyncio.run(api_client.login(tenant_slug, login_username, login_password))
                except Exception as exc:
                    st.error(f"后端登录失败：{exc}")
                else:
                    st.session_state['auth_token'] = resp.get('access_token')
                    st.session_state['tenant'] = resp.get('tenant', tenant_slug)
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_username
                    st.session_state['last_question'] = None
                    st.session_state['last_answer'] = None
                    st.session_state.page = selected
                    st.success("登录成功")
                    st.rerun()
            else:
                success, msg = validate_login(login_username, login_password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = login_username
                    st.session_state['last_question'] = None
                    st.session_state['last_answer'] = None
                    st.session_state.page = selected  # 登录后同步page，保证切换流畅
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        if st.button("还没有账号？点击注册", key="to_register"):
            st.session_state['show_register'] = True
            st.rerun()
    # 未登录时首页不显示内容区介绍
    st.stop()
else:
    # 登录后不再显示外层大标题
    if st.sidebar.button("退出登录"):
        # 退出时归档学习会话
        st.session_state.user_profile.end_session()
        st.session_state['session_start_time'] = None
        st.session_state['last_session_update'] = None
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state.pop('auth_token', None)
        st.rerun()
    # 定时自动归档（每5分钟）
    if st.session_state.get('session_start_time'):
        now = datetime.now()
        last_update = st.session_state.get('last_session_update', now)
        if (now - last_update).total_seconds() > 300:  # 5分钟
            st.session_state.user_profile.end_session()
            st.session_state.user_profile.start_session()
            st.session_state['session_start_time'] = datetime.now()
            st.session_state['last_session_update'] = now

def auto_latex_inline(text):
    # 先处理原有的latex片段
    pattern = r'(F_{\\text\{.*?\}}=0|a=0|v\^2=.*?)(?=[^a-zA-Z0-9_]|$)'
    text = re.sub(pattern, r'$\1$', text)
    # 新增：将 (\LaTeX内容) 替换为 ($\LaTeX内容$)
    text = re.sub(r'\((\\[a-zA-Z0-9_{}^=+\-]+)\)', r'($\1$)', text)
    return text

def safe_latex_render(latex_str):
    # 安全地去除 \text{...}，不区分中英文
    latex_str = re.sub(r'\\text\{([^}]*)\}', r'\1', latex_str)
    # 替换常见单位
    latex_str = latex_str.replace(r'\text{N}', r'\mathrm{N}')
    latex_str = latex_str.replace(r'\text{kg}', r'\mathrm{kg}')
    latex_str = latex_str.replace(r'\text{m/s}^2', r'\mathrm{m/s}^2')
    try:
        st.latex(latex_str)
    except Exception as e:
        st.markdown(f'`[公式渲染失败]` {latex_str}')

def render_answer_with_latex(answer):
    lines = answer.split('\n')
    for line in lines:
        line_strip = line.strip()
        # 跳过只有中括号的行
        if line_strip in ['[', ']']:
            continue
        # 如果是被中括号包裹的公式
        if line_strip.startswith('[') and line_strip.endswith(']'):
            formula = line_strip[1:-1].strip()
            safe_latex_render(formula)
        # 只包含LaTeX公式的行
        elif re.match(r'^\\[a-zA-Z]', line_strip) or re.match(r'^[^a-zA-Z0-9]*\\[a-zA-Z]', line_strip):
            safe_latex_render(line_strip)
        else:
            st.markdown(line)

def display_achievement(achievement):
    """显示成就卡片"""
    level_class = f"achievement-{achievement['level']}"
    st.markdown(
        f"""
        <div class="achievement-card {level_class}">
            <h3>{achievement['name']}</h3>
            <p>{achievement['description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if st.session_state.page == "首页":
    col1, col2 = st.columns([2, 1])
    with col1:
        username = st.session_state.get('username', None)
        if username:
            st.title(f"{username}，欢迎使用AI多模态个性化学习伴侣！")
        else:
            st.title("AI多模态个性化学习伴侣")
        st.markdown("""
        #### 你的专属智能学习伙伴，让学习更高效！
        
        - **AI智能答疑:** 支持文本/图片题目输入，AI自动生成详细解析和思路。
        - **个性化错题本:** 自动归档错题，智能推荐复习，彻底攻克知识盲点。
        - **学习路径规划:** 根据你的学习情况，量身定制学习计划和资源。
        - **进度可视化:** 清晰掌握学习进度，每一次努力都有迹可循。
        - **学习成就系统:** 记录学习成果，激励持续进步。
        """)
    with col2:
        st.image(str(ASSETS_DIR / "logo.png"), use_container_width=True)

    # 首页顶部实时显示本次学习已用时长
    if st.session_state.get('session_start_time'):
        elapsed = datetime.now() - st.session_state['session_start_time']
        hours = elapsed.total_seconds() / 3600
        st.info(f"本次学习已用时长：{hours:.2f} 小时")

elif st.session_state.page == "AI答疑":
    st.header("AI答疑")
    st.info("支持文本输入和图片上传两种方式，AI将为你详细解答。")
    
    # 题目输入区域
    col1, col2 = st.columns([2, 1])
    with col1:
        question_text = st.text_area("请输入题目（支持数学/语文/英语等）")
    with col2:
        uploaded_image = st.file_uploader("或上传题目图片", type=["png", "jpg", "jpeg"])
    
    submit = st.button("提交给AI解答")
    if submit:
        if not api_key:
            st.warning("请在侧边栏输入有效的DeepSeek API Key！")
        elif not question_text and not uploaded_image:
            st.warning("请至少输入题目文本或上传图片！")
        else:
            with st.spinner("AI正在思考中..."):
                if USE_BACKEND and st.session_state.get("auth_token"):
                    payload = {
                        "question": question_text,
                        "subject": None,
                        "user_context": {"username": st.session_state.get("username")},
                    }
                    try:
                        response = asyncio.run(api_client.ask_question(st.session_state["auth_token"], payload))
                        answer = response.get("answer", "[后端未返回内容]")
                        citations = response.get("citations", [])
                        st.session_state["last_citations"] = citations
                        st.session_state["last_metadata"] = response.get("metadata", {})
                    except Exception as exc:
                        st.error(f"调用后端出错：{exc}")
                        answer = None
                else:
                    answer = ai_answer(
                        question_text,
                        uploaded_image,
                        user_profile=st.session_state.user_profile,
                        api_key=api_key,
                    )
                    st.session_state["last_citations"] = []
            if "[AI答疑出错" not in answer and "[未检测到API Key" not in answer and "[请输入题目文本" not in answer:
                    st.session_state.last_question = question_text
                    st.session_state.last_answer = answer
                    if "last_metadata" not in st.session_state:
                        st.session_state["last_metadata"] = {}
            else:
                st.error(answer)
                st.session_state.last_answer = None
                st.session_state.last_question = None

    # 显示AI解答
    if st.session_state.last_answer:
        st.success("AI解答：")
        render_answer_with_latex(st.session_state.last_answer)
        if st.session_state.get("last_citations"):
            with st.expander("参考资料"):
                for cite in st.session_state["last_citations"]:
                    st.markdown(f"- 来源: {cite.get('source', '未知')} (score: {cite.get('score', 'N/A')})")
        
        # 收藏到错题本
        with st.expander("收藏到错题本"):
            knowledge = st.text_input("知识点（可选）", key="knowledge_input")
            difficulty = st.selectbox("难度", ["简单", "中等", "困难"], key="difficulty_select")
            if st.button("收藏"):
                if USE_BACKEND and st.session_state.get("auth_token"):
                    payload = {
                        "problem_id": None,
                        "subject": st.session_state.get("last_metadata", {}).get("subject"),
                        "knowledge_tags": [knowledge] if knowledge else None,
                        "difficulty": difficulty,
                        "notes": "来自AI答疑收藏",
                        "metadata": {
                            "question": st.session_state.last_question,
                            "answer": st.session_state.last_answer,
                        },
                    }
                    try:
                        asyncio.run(api_client.create_mistake(st.session_state["auth_token"], payload))
                        st.success("题目已同步到后端错题本！")
                    except Exception as exc:
                        st.error(f"错题同步失败：{exc}")
                else:
                    mistake = {
                        'question': st.session_state.last_question,
                        'answer': st.session_state.last_answer,
                        'knowledge': knowledge,
                        'difficulty': difficulty,
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.user_profile.add_mistake(mistake)
                    st.success("题目已收藏到错题本！")

elif st.session_state.page == "错题本":
    st.header("我的错题本")

    # 搜索和筛选
    col1, col2, col3 = st.columns(3)
    with col1:
        search_kw = st.text_input("搜索题目/知识点", key="search_kw")
    with col2:
        knowledge_filter = st.text_input("按知识点筛选", key="knowledge_filter")
    with col3:
        difficulty_filter = st.selectbox("按难度筛选", ["全部", "简单", "中等", "困难"], key="difficulty_filter")
    
    # 获取错题列表
    if USE_BACKEND and st.session_state.get("auth_token"):
        try:
            resp = asyncio.run(api_client.get_mistakes(st.session_state["auth_token"]))
            mistakes = resp.get("items", [])
        except Exception as exc:
            st.error(f"获取后端错题失败：{exc}")
            mistakes = []
    else:
        mistakes = st.session_state.user_profile.data['mistakes']

    # 应用筛选
    filtered = mistakes
    if search_kw:
        filtered = [
            p for p in filtered
            if search_kw.lower() in (p.get('question','') or '').lower()
            or search_kw.lower() in (','.join(p.get('knowledge_tags', []) if isinstance(p.get('knowledge_tags'), list) else [p.get('knowledge','')]) ).lower()
        ]
    if knowledge_filter:
        filtered = [
            p for p in filtered
            if knowledge_filter.lower() in (
                ','.join(p.get('knowledge_tags', []) if isinstance(p.get('knowledge_tags'), list) else [p.get('knowledge','')])
            ).lower()
        ]
    if difficulty_filter != "全部":
        filtered = [p for p in filtered if p.get('difficulty','') == difficulty_filter]

    if not filtered:
        st.info("没有符合条件的错题。")
    else:
        for i, problem in enumerate(filtered):
            knowledge_label = problem.get('knowledge') or ','.join(problem.get('knowledge_tags', []) or ['未标注'])
            with st.expander(f"错题 {i+1} - {knowledge_label} - {problem.get('difficulty', '未标注')}"):
                st.markdown(f"**题目:** {problem.get('question', problem.get('metadata', {}).get('question', 'N/A'))}")
                st.markdown("**AI解答:**")
                render_answer_with_latex(problem.get('answer', problem.get('metadata', {}).get('answer', 'N/A')))
                st.caption(f"收藏时间: {problem.get('created_at', problem.get('timestamp', 'N/A'))}")
                if not USE_BACKEND:
                    if st.button(f"删除错题 {i+1}", key=f"delete_{i}"):
                        mistakes.remove(problem)
                        st.session_state.user_profile.save_data()
                        st.success(f"错题 {i+1} 已删除！")
                        st.rerun()

elif st.session_state.page == "学习建议":
    st.header("个性化学习建议")

    # 获取学习建议
    if USE_BACKEND and st.session_state.get("auth_token"):
        try:
            plan_resp = asyncio.run(api_client.get_learning_plan(st.session_state["auth_token"]))
            knowledge_resp = asyncio.run(api_client.get_knowledge_mastery(st.session_state["auth_token"]))
        except Exception as exc:
            st.error(f"获取学习建议失败：{exc}")
            plan_resp = {"plan": []}
            knowledge_resp = {"knowledge": []}
        plan_items = plan_resp.get("plan", [])
        if plan_items:
            for item in plan_items:
                st.markdown(
                    f"**{item['knowledge']}** · 待完成 {item['tasks']} 项 · 最近出现 {item['last_seen']}"
                )
                st.caption(
                    "难度分布: " + ", ".join(
                        f"{k}:{v}" for k, v in item.get("difficulty_distribution", {}).items()
                    )
                )
        else:
            st.info("暂无后端生成的学习建议，请先进行 AI 答疑或收藏错题。")

        knowledge_points = knowledge_resp.get("knowledge", [])
        if knowledge_points:
            st.subheader("知识点掌握情况 (来自后端)")
            knowledge_df = pd.DataFrame(knowledge_points)
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=knowledge_df['mastery_level'],
                theta=knowledge_df['name'],
                fill='toself',
                name='掌握程度'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=False
            )
            st.plotly_chart(fig)
        suggestions = "后端智能建议已上方列出，可结合 AI 再次润色。"
    else:
        suggestions = st.session_state.user_profile.get_learning_suggestions()
        st.markdown(suggestions)

        # 知识点掌握情况
        if st.session_state.user_profile.data['knowledge_points']:
            st.subheader("知识点掌握情况")
            knowledge_df = pd.DataFrame.from_dict(
                st.session_state.user_profile.data['knowledge_points'],
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

    # 生成AI个性化建议
    if api_key and st.button("生成AI个性化学习建议"):
        with st.spinner("AI正在生成个性化建议..."):
            prompt = f"请根据以下学习情况，给出详细的个性化学习建议和复习计划：\n{suggestions}"
            suggestion = ai_answer(prompt, api_key=api_key)
        st.success("AI个性化学习建议：")
        st.markdown(suggestion)

elif st.session_state.page == "学习进度":
    st.header("学习进度追踪")

    # 获取学习进度数据
    if USE_BACKEND and st.session_state.get("auth_token"):
        try:
            progress_resp = asyncio.run(api_client.get_progress_metrics(st.session_state["auth_token"]))
            achievements_resp = asyncio.run(api_client.get_achievements(st.session_state["auth_token"]))
        except Exception as exc:
            st.error(f"获取学习进度失败：{exc}")
            progress_resp = {"metrics": {"daily_activity": [], "subject_distribution": [], "study_sessions": []}, "overview": {}}
            achievements_resp = {"achievements": [], "totals": {}}

        metrics = progress_resp.get("metrics", {})
        daily_activity = metrics.get("daily_activity", [])
        subject_dist = metrics.get("subject_distribution", [])

        if not daily_activity:
            st.info("暂无学习数据，快去AI答疑或开始学习会话吧！")
        else:
            st.subheader("每日学习统计")
            daily_df = pd.DataFrame(daily_activity)
            fig = px.line(daily_df, x='date', y='count', title='每日解题数量趋势')
            st.plotly_chart(fig)

            st.subheader("学科分布")
            subject_df = pd.DataFrame(subject_dist)
            fig = px.pie(subject_df, values='count', names='subject', title='各学科题目分布')
            st.plotly_chart(fig)

        st.subheader("学习成就")
        for achievement in achievements_resp.get("achievements", []):
            display_achievement({
                "name": achievement.get("name"),
                "description": f"等级: {achievement.get('level', '未知')}",
                "level": achievement.get("level", "bronze")
            })

        overview = progress_resp.get("overview", {})
        st.metric("累计错题", achievements_resp.get("totals", {}).get("mistakes", 0))
        st.metric("累计学习次数", achievements_resp.get("totals", {}).get("interactions", 0))
        st.metric("连续学习天数", achievements_resp.get("totals", {}).get("streak", 0))
        st.caption(f"学习会话总数：{overview.get('total_sessions', 0)} · 总时长：{overview.get('total_hours', 0)} 小时")
    else:
        progress = st.session_state.user_profile.get_learning_progress()

        if progress is None:
            st.info("暂无学习数据，快去AI答疑吧！")
        else:
            # 每日学习统计
            st.subheader("每日学习统计")
            fig = px.line(progress['daily_stats'], 
                         x='date', 
                         y='question',
                         title='每日解题数量趋势')
            st.plotly_chart(fig)
            
            # 学科分布
            st.subheader("学科分布")
            fig = px.pie(values=progress['subject_stats'].values,
                        names=progress['subject_stats'].index,
                        title='各学科题目分布')
            st.plotly_chart(fig)
            
            # 学习成就
            st.subheader("学习成就")
            achievements = st.session_state.user_profile.get_achievements()
            for achievement in achievements:
                display_achievement(achievement)

elif st.session_state.page == "学习成就":
    st.header("学习成就系统")

    # 显示所有成就
    if USE_BACKEND and st.session_state.get("auth_token"):
        try:
            achievements_resp = asyncio.run(api_client.get_achievements(st.session_state["auth_token"]))
        except Exception as exc:
            st.error(f"获取学习成就失败：{exc}")
            achievements_resp = {"achievements": [], "totals": {}}

        achievements = achievements_resp.get("achievements", [])
        if not achievements:
            st.info("继续努力，解锁更多成就！")
        else:
            for achievement in achievements:
                display_achievement({
                    "name": achievement.get("name"),
                    "description": f"等级: {achievement.get('level')}",
                    "level": achievement.get("level", "bronze")
                })

        totals = achievements_resp.get("totals", {})
        st.subheader("学习统计")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("累计错题", totals.get("mistakes", 0))
        with col2:
            st.metric("累计学习次数", totals.get("interactions", 0))
        with col3:
            st.metric("连续学习天数", totals.get("streak", 0))
    else:
        achievements = st.session_state.user_profile.get_achievements()
        if not achievements:
            st.info("继续努力，解锁更多成就！")
        else:
            for achievement in achievements:
                display_achievement(achievement)

        # 显示学习统计
        st.subheader("学习统计")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_mistakes = len(st.session_state.user_profile.data['mistakes'])
            st.metric("累计错题", total_mistakes)
        
        with col2:
            total_interactions = len(st.session_state.user_profile.data['interactions'])
            st.metric("累计学习次数", total_interactions)
        
        with col3:
            knowledge_points = len(st.session_state.user_profile.data['knowledge_points'])
            st.metric("掌握知识点", knowledge_points)
