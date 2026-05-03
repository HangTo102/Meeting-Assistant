"""
会场精灵 - 数据库初始化脚本
用于快速部署和测试环境搭建
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    DatabaseManager, Organizer, Activity, SubActivity, 
    ActivityTag, ChatLog
)


def create_sample_data(session: Session):
    """创建示例数据"""
    
    print("📝 创建示例数据...")
    
    # 1. 创建主办方
    organizer = Organizer(
        username="master",
        password_hash="$2a$10$YourHashedPasswordHere",  # 实际使用 BCrypt 加密
        organizer_name="上海国际展览中心",
        contact_person="张经理",
        phone="021-12345678",
        email="contact@shexpo.com",
        address="上海市浦东新区龙阳路2345号",
        status=1
    )
    session.add(organizer)
    session.flush()  # 获取 ID
    print(f"✅ 创建主办方: {organizer.organizer_name} (ID: {organizer.id})")
    
    # 2. 创建活动
    activity1 = Activity(
        organizer_id=organizer.id,
        activity_name="国际创新博览会 2026",
        start_time=datetime(2026, 3, 20, 9, 0, 0),
        end_time=datetime(2026, 3, 22, 18, 0, 0),
        address="上海国际会展中心 - 上海市浦东新区龙阳路2345号",
        description="汇聚全球创新科技，展示最新科技成果，涵盖人工智能、物联网、新能源等多个前沿领域。",
        requires_ticket=True,
        ticket_url="https://tickets.example.com/expo2026",
        ticket_price="早鸟票: ¥99, 普通票: ¥149, VIP票: ¥399",
        ticket_deadline=datetime(2026, 3, 19, 23, 59, 59),
        status=1,
        view_count=12580
    )
    session.add(activity1)
    session.flush()
    print(f"✅ 创建活动: {activity1.activity_name} (ID: {activity1.id})")
    
    # 3. 创建子活动
    sub_activities = [
        {
            "sub_name": "科技论坛开幕式",
            "start_time": datetime(2026, 3, 20, 9, 0, 0),
            "end_time": datetime(2026, 3, 20, 10, 30, 0),
            "location": "主会场A厅",
            "description": "博览会正式开幕，邀请行业领袖致辞",
            "sort_order": 1
        },
        {
            "sub_name": "人工智能专场",
            "start_time": datetime(2026, 3, 20, 14, 0, 0),
            "end_time": datetime(2026, 3, 20, 17, 0, 0),
            "location": "B厅会议室",
            "description": "探讨AI技术在各行业的应用",
            "sort_order": 2
        },
        {
            "sub_name": "企业路演",
            "start_time": datetime(2026, 3, 21, 10, 0, 0),
            "end_time": datetime(2026, 3, 21, 12, 0, 0),
            "location": "路演大厅",
            "description": "初创企业项目展示与融资对接",
            "sort_order": 3
        },
        {
            "sub_name": "新能源技术峰会",
            "start_time": datetime(2026, 3, 21, 14, 0, 0),
            "end_time": datetime(2026, 3, 21, 17, 0, 0),
            "location": "C厅",
            "description": "聚焦新能源技术发展与产业应用",
            "sort_order": 4
        },
        {
            "sub_name": "闭幕式暨颁奖典礼",
            "start_time": datetime(2026, 3, 22, 16, 0, 0),
            "end_time": datetime(2026, 3, 22, 18, 0, 0),
            "location": "主会场A厅",
            "description": "颁发创新奖项，宣布下一届博览会信息",
            "sort_order": 5
        }
    ]
    
    for sub_data in sub_activities:
        sub = SubActivity(activity_id=activity1.id, **sub_data)
        session.add(sub)
    print(f"✅ 创建 {len(sub_activities)} 个子活动")
    
    # 4. 创建标签
    tags = ["科技", "创新", "博览会", "人工智能", "新能源", "企业路演", "投资"]
    for tag_name in tags:
        tag = ActivityTag(activity_id=activity1.id, tag_name=tag_name)
        session.add(tag)
    print(f"✅ 创建 {len(tags)} 个标签")
    
    # 5. 创建更多示例活动
    activities_data = [
        {
            "activity_name": "2026春季科技峰会",
            "start_time": datetime(2026, 4, 15, 9, 0, 0),
            "end_time": datetime(2026, 4, 16, 18, 0, 0),
            "address": "北京国家会议中心",
            "description": "春季科技创新盛会",
            "requires_ticket": True,
            "ticket_price": "¥299",
            "status": 1
        },
        {
            "activity_name": "AI开发者大会",
            "start_time": datetime(2026, 5, 10, 9, 0, 0),
            "end_time": datetime(2026, 5, 12, 18, 0, 0),
            "address": "深圳会展中心",
            "description": "面向AI开发者的技术交流大会",
            "requires_ticket": True,
            "ticket_price": "¥199",
            "status": 1
        },
        {
            "activity_name": "开源技术沙龙",
            "start_time": datetime(2026, 3, 25, 14, 0, 0),
            "end_time": datetime(2026, 3, 25, 17, 0, 0),
            "address": "杭州梦想小镇",
            "description": "开源技术分享与交流",
            "requires_ticket": False,
            "status": 1
        }
    ]
    
    for act_data in activities_data:
        activity = Activity(organizer_id=organizer.id, **act_data)
        session.add(activity)
    print(f"✅ 创建 {len(activities_data)} 个额外活动")
    
    # 6. 创建示例对话记录
    import uuid
    sample_session = str(uuid.uuid4())
    chat_logs = [
        {
            "session_id": sample_session,
            "activity_id": activity1.id,
            "user_message": "今天的活动有哪些？",
            "assistant_response": "今天的活动有：\n• 国际创新博览会 9:00-18:00\n• 科技论坛 14:00-17:00\n• 企业路演 10:00-12:00",
            "response_time_ms": 850,
            "is_helpful": True
        },
        {
            "session_id": sample_session,
            "activity_id": activity1.id,
            "user_message": "国际创新博览会在哪里？",
            "assistant_response": "📍 上海国际会展中心\n🏠 上海市浦东新区龙阳路2345号\n\n地铁：2/7号线龙阳路站步行500米\n公交：花木1路、浦东11路",
            "response_time_ms": 620,
            "is_helpful": True
        },
        {
            "session_id": sample_session,
            "activity_id": activity1.id,
            "user_message": "门票多少钱？",
            "assistant_response": "💰 票价信息：\n• 早鸟票：¥99（已售罄）\n• 普通票：¥149\n• VIP票：¥399（含专属通道和礼品）\n\n⚠️ 学生凭有效证件可享5折优惠",
            "response_time_ms": 780,
            "is_helpful": True
        }
    ]
    
    for chat_data in chat_logs:
        chat = ChatLog(**chat_data)
        session.add(chat)
    print(f"✅ 创建 {len(chat_logs)} 条对话记录")
    
    session.commit()
    print("\n✅ 所有示例数据创建完成！")


def init_database(database_url: str, drop_existing: bool = False):
    """
    初始化数据库
    
    Args:
        database_url: 数据库连接URL
        drop_existing: 是否删除现有表
    """
    print(f"🚀 初始化数据库...")
    print(f"📍 连接地址: {database_url.split('@')[-1] if '@' in database_url else database_url}\n")
    
    try:
        # 创建管理器
        db = DatabaseManager(database_url)
        
        if drop_existing:
            print("⚠️  删除现有表...")
            db.drop_tables()
            print("✅ 已删除现有表\n")
        
        # 创建表
        print("🔨 创建数据表...")
        db.create_tables()
        print("✅ 数据表创建成功\n")
        
        # 创建示例数据
        with db.get_session() as session:
            create_sample_data(session)
        
        print("\n🎉 数据库初始化完成！")
        print("-" * 50)
        print("初始主办方账号信息已创建（请及时修改密码）")
        print("-" * 50)
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='会场精灵数据库初始化工具')
    parser.add_argument(
        '--url', 
        default='mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/event_assistant?charset=utf8mb4',
        help='数据库连接URL'
    )
    parser.add_argument(
        '--drop',
        action='store_true',
        help='删除现有表后重新创建'
    )
    parser.add_argument(
        '--no-data',
        action='store_true',
        help='不插入示例数据'
    )
    
    args = parser.parse_args()
    
    # 检查环境变量
    db_url = os.getenv('DATABASE_URL', args.url)
    
    print("=" * 60)
    print("     会场精灵 - 数据库初始化工具")
    print("=" * 60)
    print()
    
    init_database(db_url, drop_existing=args.drop)


if __name__ == "__main__":
    main()
