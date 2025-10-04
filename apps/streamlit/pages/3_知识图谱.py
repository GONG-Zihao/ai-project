import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import json
import os
from pathlib import Path
from ai_core import KnowledgeGraph

st.set_page_config(page_title="知识图谱", page_icon="��", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("请先登录账号以使用知识图谱功能！")
    st.stop()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

username = st.session_state['username']
graph_file = DATA_DIR / f'knowledge_graph_{username}.json'

# 初始化知识图谱
if 'knowledge_graph' not in st.session_state or st.session_state.get('last_kg_user') != username:
    st.session_state.knowledge_graph = KnowledgeGraph()
    st.session_state.last_kg_user = username
    # 加载用户专属知识图谱
    if graph_file.exists():
        with open(graph_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            st.session_state.knowledge_graph.graph.clear()
            for node in data['nodes']:
                st.session_state.knowledge_graph.graph.add_node(node['id'], **node['attributes'])
            for edge in data['edges']:
                st.session_state.knowledge_graph.graph.add_edge(edge['source'], edge['target'], **edge['attributes'])

def save_knowledge_graph():
    os.makedirs(DATA_DIR, exist_ok=True)
    # 保存到用户专属文件
    data = {
        'nodes': [{'id': n, 'attributes': st.session_state.knowledge_graph.graph.nodes[n]} for n in st.session_state.knowledge_graph.graph.nodes()],
        'edges': [{'source': u, 'target': v, 'attributes': st.session_state.knowledge_graph.graph.edges[u, v]} 
                 for u, v in st.session_state.knowledge_graph.graph.edges()]
    }
    with open(graph_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 页面标题
st.title("AI多模态个性化学习伴侣")
st.markdown("探索知识点之间的关联关系，构建你的知识网络！")

# 创建两个标签页
tab1, tab2 = st.tabs(["图谱浏览", "知识点管理"])

with tab1:
    st.header("知识图谱可视化")
    
    # 选择要显示的科目
    subjects = ["数学", "物理", "化学", "英语", "语文"]
    selected_subject = st.selectbox("选择科目", subjects)
    
    # 获取该科目的知识点
    nodes = []
    edges = []
    for node in st.session_state.knowledge_graph.graph.nodes():
        if st.session_state.knowledge_graph.graph.nodes[node].get('subject') == selected_subject:
            nodes.append(node)
            for neighbor in st.session_state.knowledge_graph.graph.neighbors(node):
                if st.session_state.knowledge_graph.graph.nodes[neighbor].get('subject') == selected_subject:
                    edges.append((node, neighbor))
    
    if nodes:
        # 创建网络图
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        
        # 使用spring布局
        pos = nx.spring_layout(G)
        
        # 创建Plotly图形
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='节点连接数',
                    xanchor='left'
                )
            )
        )
        
        # 计算节点连接数
        node_adjacencies = []
        for node in G.nodes():
            node_adjacencies.append(len(list(G.neighbors(node))))
        node_trace.marker.color = node_adjacencies
        
        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                         title=f'{selected_subject}知识图谱',
                         showlegend=False,
                         hovermode='closest',
                         margin=dict(b=20,l=5,r=5,t=40),
                         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                     )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示知识点详情
        st.subheader("知识点详情")
        selected_node = st.selectbox("选择知识点", nodes)
        if selected_node:
            st.markdown(f"### {selected_node}")
            st.markdown(st.session_state.knowledge_graph.graph.nodes[selected_node].get('description', '暂无描述'))
            
            # 显示相关知识点
            st.markdown("### 相关知识点")
            related_nodes = list(st.session_state.knowledge_graph.graph.neighbors(selected_node))
            if related_nodes:
                for node in related_nodes:
                    st.markdown(f"- {node}")
            else:
                st.info("暂无相关知识点")
    else:
        st.info(f"暂无{selected_subject}科目的知识点数据")

with tab2:
    st.header("知识点管理")
    
    # 添加新知识点
    with st.expander("添加新知识点"):
        concept = st.text_input("知识点名称")
        subject = st.selectbox("所属科目", subjects)
        description = st.text_area("知识点描述")
        related_concepts = st.multiselect(
            "相关知识点",
            options=[node for node in st.session_state.knowledge_graph.graph.nodes() 
                    if node != concept]
        )
        
        if st.button("添加知识点"):
            if concept and subject and description:
                st.session_state.knowledge_graph.add_concept(
                    concept,
                    subject=subject,
                    description=description
                )
                for related in related_concepts:
                    st.session_state.knowledge_graph.add_relation(concept, related)
                save_knowledge_graph()
                st.success("知识点已添加！")
                st.rerun()
            else:
                st.warning("请填写完整的知识点信息！")
    
    # 知识点列表
    st.subheader("知识点列表")
    for subject in subjects:
        with st.expander(f"{subject}知识点"):
            nodes = [node for node in st.session_state.knowledge_graph.graph.nodes()
                    if st.session_state.knowledge_graph.graph.nodes[node].get('subject') == subject]
            if nodes:
                for node in nodes:
                    st.markdown(f"### {node}")
                    st.markdown(st.session_state.knowledge_graph.graph.nodes[node].get('description', '暂无描述'))
                    
                    # 编辑和删除按钮
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("编辑", key=f"edit_{node}"):
                            st.session_state.editing_node = node
                    with col2:
                        if st.button("删除", key=f"delete_{node}"):
                            st.session_state.knowledge_graph.graph.remove_node(node)
                            save_knowledge_graph()
                            st.success("知识点已删除！")
                            st.rerun()
                    
                    st.markdown("---")
            else:
                st.info(f"暂无{subject}科目的知识点") 
