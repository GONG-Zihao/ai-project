import json
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict
import re
import pymongo
from pymongo import MongoClient
from hashlib import sha256
import streamlit as st

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['ai_study']
users = db['users']

class UserProfile:
    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.data_file = f'data/user_{user_id}.json'
        self.load_data()
        self.session_start = None  # 新增：本次会话开始时间
    
    def load_data(self):
        """加载用户数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                'interactions': [],  # 用户交互记录
                'mistakes': [],      # 错题记录
                'knowledge_points': {},  # 知识点掌握情况
                'learning_path': [],     # 学习路径
                'achievements': [],       # 学习成就
                'learning_sessions': []  # 新增：学习时长会话
            }
            self.save_data()
        # 兼容老数据
        if 'learning_sessions' not in self.data:
            self.data['learning_sessions'] = []
    
    def save_data(self):
        """保存用户数据"""
        os.makedirs('data', exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_interaction(self, interaction):
        """添加用户交互记录"""
        self.data['interactions'].append(interaction)
        self.save_data()
    
    def add_mistake(self, mistake):
        """添加错题记录"""
        mistake['timestamp'] = datetime.now().isoformat()
        self.data['mistakes'].append(mistake)
        self.update_knowledge_points(mistake)
        self.save_data()
    
    def update_knowledge_points(self, mistake):
        """更新知识点掌握情况"""
        knowledge = mistake.get('knowledge', '')
        if knowledge:
            if knowledge not in self.data['knowledge_points']:
                self.data['knowledge_points'][knowledge] = {
                    'count': 0,
                    'last_review': None,
                    'mastery_level': 0
                }
            self.data['knowledge_points'][knowledge]['count'] += 1
            self.data['knowledge_points'][knowledge]['last_review'] = datetime.now().isoformat()
            self.data['knowledge_points'][knowledge]['mastery_level'] = min(
                5, self.data['knowledge_points'][knowledge]['count']
            )
    
    def get_learning_progress(self):
        """获取学习进度数据"""
        df = pd.DataFrame(self.data['interactions'])
        if df.empty:
            return None
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # 每日学习统计
        daily_stats = df.groupby('date').agg({
            'subject': 'count',
            'question': 'count'
        }).reset_index()
        
        # 学科分布
        subject_stats = df['subject'].value_counts()
        
        # 知识点掌握情况
        knowledge_stats = pd.DataFrame.from_dict(
            self.data['knowledge_points'],
            orient='index'
        )
        
        return {
            'daily_stats': daily_stats,
            'subject_stats': subject_stats,
            'knowledge_stats': knowledge_stats
        }
    
    def get_learning_suggestions(self):
        """生成学习建议"""
        if not self.data['mistakes']:
            return "暂无错题数据，快去AI答疑并收藏错题吧！"
        
        # 分析错题分布
        mistake_df = pd.DataFrame(self.data['mistakes'])
        knowledge_counts = mistake_df['knowledge'].value_counts()
        difficulty_counts = mistake_df['difficulty'].value_counts()
        
        # 找出最薄弱的知识点
        weak_points = knowledge_counts.head(3)
        
        # 生成建议
        suggestions = []
        suggestions.append(f"你已累计收藏 {len(mistake_df)} 道错题。")
        
        if not weak_points.empty:
            suggestions.append("\n最需要加强的知识点：")
            for point, count in weak_points.items():
                suggestions.append(f"- {point}：{count}道错题")
        
        if not difficulty_counts.empty:
            suggestions.append("\n难度分布：")
            for diff, count in difficulty_counts.items():
                suggestions.append(f"- {diff}：{count}道")
        
        return "\n".join(suggestions)
    
    def get_achievements(self):
        """获取学习成就"""
        achievements = []
        
        # 计算成就
        total_mistakes = len(self.data['mistakes'])
        if total_mistakes >= 10:
            achievements.append({
                'name': '错题收集者',
                'description': '收集了10道错题',
                'level': 'bronze'
            })
        if total_mistakes >= 50:
            achievements.append({
                'name': '错题大师',
                'description': '收集了50道错题',
                'level': 'silver'
            })
        if total_mistakes >= 100:
            achievements.append({
                'name': '错题王者',
                'description': '收集了100道错题',
                'level': 'gold'
            })
        
        # 连续学习天数
        if self.data['interactions']:
            dates = set(pd.to_datetime(i['timestamp']).date() 
                       for i in self.data['interactions'])
            streak = 0
            current_date = datetime.now().date()
            while current_date in dates:
                streak += 1
                current_date -= timedelta(days=1)
            
            if streak >= 3:
                achievements.append({
                    'name': '坚持不懈',
                    'description': f'连续学习{streak}天',
                    'level': 'bronze'
                })
            if streak >= 7:
                achievements.append({
                    'name': '学习达人',
                    'description': f'连续学习{streak}天',
                    'level': 'silver'
                })
            if streak >= 30:
                achievements.append({
                    'name': '学习王者',
                    'description': f'连续学习{streak}天',
                    'level': 'gold'
                })
        
        return achievements

    def start_session(self):
        """开始学习会话"""
        self.session_start = datetime.now()

    def end_session(self):
        """结束学习会话并归档"""
        if self.session_start:
            end_time = datetime.now()
            duration = (end_time - self.session_start).total_seconds() / 3600  # 小时
            session = {
                'date': self.session_start.date().isoformat(),
                'start': self.session_start.isoformat(),
                'end': end_time.isoformat(),
                'duration': duration
            }
            self.data['learning_sessions'].append(session)
            self.save_data()
            self.session_start = None

    def get_total_study_time(self):
        return sum(s['duration'] for s in self.data.get('learning_sessions', []))

    def get_study_days(self):
        return len(set(s['date'] for s in self.data.get('learning_sessions', [])))

    def get_daily_study_trend(self):
        df = pd.DataFrame(self.data.get('learning_sessions', []))
        if df.empty:
            return pd.DataFrame(columns=['date', 'duration'])
        df['date'] = pd.to_datetime(df['date'])
        return df.groupby('date')['duration'].sum().reset_index()

    def get_hourly_distribution(self):
        df = pd.DataFrame(self.data.get('learning_sessions', []))
        if df.empty:
            return pd.DataFrame(columns=['hour', 'count'])
        df['start'] = pd.to_datetime(df['start'])
        df['hour'] = df['start'].dt.hour
        return df.groupby('hour').size().reset_index(name='count')

def load_user_data():
    """加载用户数据（兼容旧版本）"""
    try:
        with open('data/user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_user_data(data):
    """保存用户数据（兼容旧版本）"""
    os.makedirs('data', exist_ok=True)
    with open('data/user_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_incorrect_problem(user_data, question, answer):
    """
    添加一条错题记录到用户数据。
    """
    new_problem = {
        'question': question,
        'answer': answer,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    print(f"DEBUG: Adding new problem: {new_problem}")
    user_data.append(new_problem)
    save_user_data(user_data)

def hash_password(password):
    """Hash password using SHA-256"""
    return sha256(password.encode()).hexdigest()

def is_valid_username(username):
    """Validate username format"""
    return re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]{3,20}$', username) is not None

def is_valid_password(password):
    """Validate password format"""
    return re.match(r'^[a-zA-Z0-9!@#$%^&*()_+=-]{6,20}$', password) is not None

def is_valid_phone(phone):
    """Validate phone number format"""
    return re.match(r'^1[3-9]\d{9}$', phone) is not None

def check_user_exists(username):
    """Check if username already exists"""
    return users.find_one({'username': username}) is not None

def register_user(username, password, phone):
    """Register new user"""
    if not username or not password or not phone:
        return False, "所有字段都必须填写"
    
    if not is_valid_username(username):
        return False, "用户名格式不正确(3-20位字母/数字/下划线/中文)"
    
    if not is_valid_password(password):
        return False, "密码格式不正确(6-20位字母/数字/特殊字符)"
    
    if not is_valid_phone(phone):
        return False, "手机号格式不正确"
    
    if check_user_exists(username):
        return False, "用户名已存在"
    
    try:
        users.insert_one({
            'username': username,
            'password': hash_password(password),
            'phone': phone
        })
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败: {str(e)}"

def validate_login(username, password):
    """Validate user login"""
    if not username or not password:
        return False, "用户名和密码不能为空"
    
    user = users.find_one({'username': username})
    if user and user['password'] == hash_password(password):
        return True, "登录成功"
    return False, "用户名或密码错误" 