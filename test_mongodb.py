import pymongo
from pymongo import MongoClient

try:
    # 尝试连接MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    
    # 测试连接
    client.admin.command('ping')
    print("MongoDB连接成功！")
    
    # 创建测试数据库和集合
    db = client['ai_study']
    users = db['users']
    
    # 插入测试数据
    test_user = {
        'username': 'test_user',
        'password': 'test_password',
        'phone': '13800138000'
    }
    users.insert_one(test_user)
    print("测试数据插入成功！")
    
    # 查询测试数据
    result = users.find_one({'username': 'test_user'})
    print("查询结果:", result)
    
    # 删除测试数据
    users.delete_one({'username': 'test_user'})
    print("测试数据删除成功！")
    
except Exception as e:
    print("MongoDB连接失败！错误信息:", str(e))
finally:
    # 关闭连接
    if 'client' in locals():
        client.close()
        print("MongoDB连接已关闭") 