import openai
from PIL import Image
import io
try:  # paddleocr 体积较大，允许按需安装
    from paddleocr import PaddleOCR
except ImportError:  # pragma: no cover - optional dependency
    PaddleOCR = None
    OCR_IMPORT_ERROR = "paddleocr 未安装"
else:
    OCR_IMPORT_ERROR = None
import networkx as nx
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# 初始化OCR
if PaddleOCR:
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    except Exception as exc:  # pragma: no cover - optional dependency
        OCR_IMPORT_ERROR = f"初始化 PaddleOCR 失败: {exc}"
        ocr = None
else:
    ocr = None

# 知识图谱
class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.load_knowledge_graph()
    
    def load_knowledge_graph(self):
        """加载预定义的知识图谱"""
        try:
            with open(DATA_DIR / 'knowledge_graph.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for node in data['nodes']:
                    self.graph.add_node(node['id'], **node['attributes'])
                for edge in data['edges']:
                    self.graph.add_edge(edge['source'], edge['target'], **edge['attributes'])
        except FileNotFoundError:
            # 如果文件不存在，创建基础知识图谱
            self.create_basic_knowledge_graph()
    
    def create_basic_knowledge_graph(self):
        """创建基础知识图谱结构"""
        # 数学知识图谱
        math_nodes = [
            {'id': 'math_basic', 'attributes': {'name': '基础数学', 'level': '基础'}},
            {'id': 'algebra', 'attributes': {'name': '代数', 'level': '基础'}},
            {'id': 'geometry', 'attributes': {'name': '几何', 'level': '基础'}},
            {'id': 'calculus', 'attributes': {'name': '微积分', 'level': '高级'}},
        ]
        
        for node in math_nodes:
            self.graph.add_node(node['id'], **node['attributes'])
        
        # 添加关系
        self.graph.add_edge('math_basic', 'algebra', relation='prerequisite')
        self.graph.add_edge('math_basic', 'geometry', relation='prerequisite')
        self.graph.add_edge('algebra', 'calculus', relation='prerequisite')
        
        # 保存知识图谱
        os.makedirs(DATA_DIR, exist_ok=True)
        self.save_knowledge_graph()
    
    def save_knowledge_graph(self):
        """保存知识图谱到文件"""
        data = {
            'nodes': [{'id': n, 'attributes': self.graph.nodes[n]} for n in self.graph.nodes()],
            'edges': [{'source': u, 'target': v, 'attributes': self.graph.edges[u, v]} 
                     for u, v in self.graph.edges()]
        }
        with open(DATA_DIR / 'knowledge_graph.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_related_concepts(self, concept_id, max_depth=2):
        """获取相关概念"""
        if concept_id not in self.graph:
            return []
        
        related = []
        for node in nx.descendants_at_distance(self.graph, concept_id, max_depth):
            related.append(self.graph.nodes[node])
        return related

    def add_concept(self, concept, subject, description):
        """添加新知识点"""
        self.graph.add_node(concept, subject=subject, description=description)

    def add_relation(self, concept1, concept2):
        """添加知识点之间的关联"""
        self.graph.add_edge(concept1, concept2)

# 初始化知识图谱
knowledge_graph = KnowledgeGraph()

def extract_text_from_image(image):
    """从图片中提取文字"""
    if ocr is None:
        return f"[OCR功能未启用：{OCR_IMPORT_ERROR or '请安装 paddleocr'}]"
    try:
        result = ocr.ocr(image, cls=True)
        text = ""
        for line in result:
            for word_info in line:
                text += word_info[1][0] + "\n"
        return text.strip()
    except Exception as e:
        return f"[OCR识别出错：{e}]"

def identify_subject(text):
    """识别题目所属学科"""
    subjects = {
        '数学': ['数学', '代数', '几何', '微积分', '函数', '方程', '概率', '统计'],
        '物理': ['物理', '力学', '电学', '光学', '热学', '牛顿', '能量', '动量'],
        '化学': ['化学', '元素', '反应', '分子', '原子', '溶液', '酸碱'],
        '英语': ['英语', '语法', '词汇', '阅读', '写作', '听力', '口语'],
        '语文': ['语文', '文言文', '现代文', '作文', '阅读理解', '诗词']
    }
    
    for subject, keywords in subjects.items():
        if any(keyword in text for keyword in keywords):
            return subject
    return '其他'

def get_subject_prompt(subject):
    """根据学科获取对应的提示词"""
    prompts = {
        '数学': "你是一位专业的数学老师，请详细解答以下数学题目，并给出解题思路和关键公式：",
        '物理': "你是一位专业的物理老师，请详细解答以下物理题目，并给出物理原理和公式推导：",
        '化学': "你是一位专业的化学老师，请详细解答以下化学题目，并给出化学反应原理和实验现象解释：",
        '英语': "你是一位专业的英语老师，请详细解答以下英语题目，并给出语法解释和例句：",
        '语文': "你是一位专业的语文老师，请详细解答以下语文题目，并给出文学分析和写作技巧：",
        '其他': "你是一位专业的学习助手，请详细解答以下题目，并给出清晰的解释："
    }
    return prompts.get(subject, prompts['其他'])

def ai_answer(question_text, image=None, user_profile=None, api_key=None):
    """
    输入题目文本或图片，返回AI生成的详细解答。
    支持OCR识别、多学科处理和知识图谱分析。
    """
    if not api_key:
        return "[未检测到API Key，请在侧边栏输入OpenAI/DeepSeek API Key]"
    
    # 处理图片输入
    if image is not None:
        try:
            image = Image.open(image)
            question_text = extract_text_from_image(image)
            if question_text.startswith("[OCR识别出错"):
                return question_text
        except Exception as e:
            return f"[图片处理出错：{e}]"
    
    if not question_text:
        return "[请输入题目文本]"
    
    try:
        # 识别学科
        subject = identify_subject(question_text)
        prompt = get_subject_prompt(subject)
        
        # 调用AI模型
        client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question_text}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        answer = response.choices[0].message.content.strip()
        
        # 记录到用户数据
        if user_profile:
            user_profile.add_interaction({
                'question': question_text,
                'answer': answer,
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            })
        
        return answer
    except Exception as e:
        return f"[AI答疑出错：{e}]" 
