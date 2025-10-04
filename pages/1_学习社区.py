import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="学习社区", page_icon="👥", layout="wide")

# 初始化社区数据
if 'community_data' not in st.session_state:
    if os.path.exists('data/community_data.json'):
        with open('data/community_data.json', 'r', encoding='utf-8') as f:
            st.session_state.community_data = json.load(f)
    else:
        st.session_state.community_data = {
            'discussions': [],
            'questions': [],
            'resources': []
        }

def save_community_data():
    os.makedirs('data', exist_ok=True)
    with open('data/community_data.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.community_data, f, ensure_ascii=False, indent=2)

# 页面标题
st.title("AI多模态个性化学习伴侣")
st.markdown("在这里，你可以与其他学习者交流经验、分享资源、互相帮助！")

# 创建三个标签页
tab1, tab2, tab3 = st.tabs(["讨论区", "问答区", "资源分享"])

with tab1:
    st.header("讨论区")
    
    # 获取当前用户名
    current_user = st.session_state['username'] if st.session_state.get('logged_in') else '匿名用户'
    
    # 发布新讨论
    with st.expander("发布新讨论"):
        title = st.text_input("标题")
        content = st.text_area("内容")
        if st.button("发布"):
            if title and content:
                new_discussion = {
                    'id': len(st.session_state.community_data['discussions']) + 1,
                    'title': title,
                    'content': content,
                    'author': current_user,  # 用当前用户名
                    'timestamp': datetime.now().isoformat(),
                    'comments': []
                }
                st.session_state.community_data['discussions'].append(new_discussion)
                save_community_data()
                st.success("发布成功！")
            else:
                st.warning("请填写标题和内容！")
    
    # 显示讨论列表
    st.subheader("最新讨论")
    for idx, discussion in enumerate(reversed(st.session_state.community_data['discussions'])):
        with st.expander(f"{discussion['title']} - {discussion['author']} - {discussion['timestamp']}"):
            st.markdown(discussion['content'])
            # 讨论作者可删除讨论
            if current_user == discussion['author']:
                if st.button("删除该讨论", key=f"delete_discussion_{discussion['id']}"):
                    # 反向索引需转换
                    real_idx = len(st.session_state.community_data['discussions']) - 1 - idx
                    st.session_state.community_data['discussions'].pop(real_idx)
                    save_community_data()
                    st.success("讨论已删除！")
                    st.rerun()
            # 评论区
            st.markdown("---")
            st.markdown("### 评论")
            for cidx, comment in enumerate(discussion['comments']):
                st.markdown(f"**{comment['author']}** ({comment['timestamp']}):")
                st.markdown(comment['content'])
                # 评论作者可删除评论
                if current_user == comment['author']:
                    if st.button("删除评论", key=f"delete_comment_{discussion['id']}_{cidx}"):
                        discussion['comments'].pop(cidx)
                        save_community_data()
                        st.success("评论已删除！")
                        st.rerun()
            # 添加评论
            comment_key = f"comment_{discussion['id']}"
            if comment_key not in st.session_state:
                st.session_state[comment_key] = ""
            new_comment = st.text_input("添加评论", key=comment_key)
            if st.button("提交评论", key=f"submit_comment_{discussion['id']}"):
                if new_comment:
                    discussion['comments'].append({
                        'author': current_user,  # 用当前用户名
                        'content': new_comment,
                        'timestamp': datetime.now().isoformat()
                    })
                    save_community_data()
                    st.session_state.pop(comment_key, None)  # 彻底清空输入框
                    st.success("评论已发布！")
                    st.rerun()

with tab2:
    st.header("问答区")
    
    # 获取当前用户名
    current_user = st.session_state['username'] if st.session_state.get('logged_in') else '匿名用户'
    
    # 发布新问题
    with st.expander("发布新问题"):
        question_title = st.text_input("问题标题")
        question_content = st.text_area("问题描述")
        tags = st.multiselect("选择标签", ["数学", "物理", "化学", "英语", "语文", "其他"])
        if st.button("发布问题"):
            if question_title and question_content:
                new_question = {
                    'id': len(st.session_state.community_data['questions']) + 1,
                    'title': question_title,
                    'content': question_content,
                    'tags': tags,
                    'author': current_user,  # 用当前用户名
                    'timestamp': datetime.now().isoformat(),
                    'answers': []
                }
                st.session_state.community_data['questions'].append(new_question)
                save_community_data()
                st.success("问题已发布！")
            else:
                st.warning("请填写问题标题和描述！")
    
    # 显示问题列表
    st.subheader("最新问题")
    for qidx, question in enumerate(reversed(st.session_state.community_data['questions'])):
        with st.expander(f"{question['title']} - {question['author']} - {', '.join(question['tags'])}"):
            st.markdown(question['content'])
            # 问题作者可删除问题
            if current_user == question['author']:
                if st.button("删除该问题", key=f"delete_question_{question['id']}"):
                    real_qidx = len(st.session_state.community_data['questions']) - 1 - qidx
                    st.session_state.community_data['questions'].pop(real_qidx)
                    save_community_data()
                    st.success("问题已删除！")
                    st.rerun()
            # 回答区
            st.markdown("---")
            st.markdown("### 回答")
            for aidx, answer in enumerate(question['answers']):
                st.markdown(f"**{answer['author']}** ({answer['timestamp']}):")
                st.markdown(answer['content'])
                # 回答作者可删除回答
                if current_user == answer['author']:
                    if st.button("删除回答", key=f"delete_answer_{question['id']}_{aidx}"):
                        question['answers'].pop(aidx)
                        save_community_data()
                        st.success("回答已删除！")
                        st.rerun()
            # 添加回答
            answer_key = f"answer_{question['id']}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = ""
            new_answer = st.text_area("添加回答", key=answer_key)
            if st.button("提交回答", key=f"submit_answer_{question['id']}"):
                if new_answer:
                    question['answers'].append({
                        'author': current_user,  # 用当前用户名
                        'content': new_answer,
                        'timestamp': datetime.now().isoformat()
                    })
                    save_community_data()
                    st.session_state.pop(answer_key, None)  # 彻底清空输入框
                    st.success("回答已发布！")
                    st.rerun()

with tab3:
    st.header("资源分享")
    
    # 获取当前用户名
    current_user = st.session_state['username'] if st.session_state.get('logged_in') else '匿名用户'
    
    # 分享新资源
    with st.expander("分享新资源"):
        resource_title_key = "resource_title"
        resource_description_key = "resource_description"
        resource_link_key = "resource_link"
        if resource_title_key not in st.session_state:
            st.session_state[resource_title_key] = ""
        if resource_description_key not in st.session_state:
            st.session_state[resource_description_key] = ""
        if resource_link_key not in st.session_state:
            st.session_state[resource_link_key] = ""
        resource_title = st.text_input("资源标题", key=resource_title_key)
        resource_description = st.text_area("资源描述", key=resource_description_key)
        resource_type = st.selectbox("资源类型", ["学习笔记", "习题集", "视频教程", "其他"])
        resource_link = st.text_input("资源链接", key=resource_link_key)
        if st.button("分享资源"):
            if resource_title and resource_description and resource_link:
                new_resource = {
                    'id': len(st.session_state.community_data['resources']) + 1,
                    'title': resource_title,
                    'description': resource_description,
                    'type': resource_type,
                    'link': resource_link,
                    'author': current_user,  # 用当前用户名
                    'timestamp': datetime.now().isoformat(),
                    'likes': 0
                }
                st.session_state.community_data['resources'].append(new_resource)
                save_community_data()
                st.session_state.pop(resource_title_key, None)
                st.session_state.pop(resource_description_key, None)
                st.session_state.pop(resource_link_key, None)
                st.success("资源已分享！")
                st.rerun()
            else:
                st.warning("请填写完整的资源信息！")
    
    # 显示资源列表
    st.subheader("最新资源")
    for ridx, resource in enumerate(reversed(st.session_state.community_data['resources'])):
        with st.expander(f"{resource['title']} - {resource['type']} - {resource['author']}"):
            st.markdown(resource['description'])
            st.markdown(f"[访问资源]({resource['link']})")
            st.markdown(f"👍 {resource['likes']} 人觉得有用")
            if st.button("点赞", key=f"like_{resource['id']}"):
                resource['likes'] += 1
                save_community_data()
                st.success("点赞成功！")
                st.rerun()
            # 资源作者可删除资源
            if current_user == resource['author']:
                if st.button("删除该资源", key=f"delete_resource_{resource['id']}"):
                    real_ridx = len(st.session_state.community_data['resources']) - 1 - ridx
                    st.session_state.community_data['resources'].pop(real_ridx)
                    save_community_data()
                    st.success("资源已删除！")
                    st.rerun() 