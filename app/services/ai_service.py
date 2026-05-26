"""
会场精灵 v2 - AI 服务

完整流程（对应 v1 的 main.py + Web_UI_design.py 中的 answer_question）：
用户问题 → 活动检索(find_activity) → 语义抽取(extract_blocks) → 已知信息 → AI润色 → 回答

关键设计：
1. 上下文记忆：连续对话时沿用 current_activity，不重新检索
2. AI 只做润色：输入是精简上下文（~100-200 tokens），不输入完整活动数据
3. 降级回复：AI 不可用时用 render_response 纯模板渲染
"""

import os
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import Activity, SubActivity, Organizer
from app.core.config import settings
from app.services.retriever import (
    find_activity,
    extract_blocks,
    render_response,
    build_context_for_ai,
    get_no_activity_response,
)


# ============================================
# 会话状态管理（内存中维护上下文）
# ============================================

# session_id → {"current_activity": dict, "activity_id": int}
SESSION_CONTEXT = {}


def get_session_context(session_id: str) -> dict:
    """获取会话上下文"""
    if session_id not in SESSION_CONTEXT:
        SESSION_CONTEXT[session_id] = {"current_activity": None, "activity_id": None}
    return SESSION_CONTEXT[session_id]


def set_session_activity(session_id: str, activity: dict, activity_id: int):
    """为会话锁定当前活动"""
    ctx = get_session_context(session_id)
    ctx["current_activity"] = activity
    ctx["activity_id"] = activity_id


def clear_session(session_id: str):
    """清除会话上下文"""
    if session_id in SESSION_CONTEXT:
        del SESSION_CONTEXT[session_id]


# ============================================
# 数据加载：从数据库读取活动列表
# ============================================

def load_activities_from_db(db: Session, activity_id: Optional[int] = None) -> List[dict]:
    """
    从数据库加载活动数据，转为 retriever 需要的 dict 格式。
    
    如果指定 activity_id，只加载该活动（用于用户指定关联活动的场景）。
    否则加载所有未取消的活动。
    """
    if activity_id:
        query = db.query(Activity).filter(Activity.id == activity_id)
    else:
        query = db.query(Activity).filter(Activity.status != 3)

    activities = query.all()
    result = []

    for act in activities:
        act_dict = {
            "id": act.id,
            "activity_name": act.activity_name,
            "start_time": act.start_time.strftime("%Y-%m-%d %H:%M") if act.start_time else None,
            "end_time": act.end_time.strftime("%Y-%m-%d %H:%M") if act.end_time else None,
            "address": act.address,
            "description": act.description,
            "requires_ticket": act.requires_ticket,
            "ticket_price": act.ticket_price,
            "ticket_url": act.ticket_url,
            "ticket_deadline": act.ticket_deadline.strftime("%Y-%m-%d %H:%M") if act.ticket_deadline else None,
            "status": act.status,
            "aliases": _generate_aliases(act),
        }

        # 加载子活动
        sub_activities = db.query(SubActivity).filter(
            SubActivity.activity_id == act.id
        ).order_by(SubActivity.sort_order).all()
        if sub_activities:
            act_dict["sub_activities"] = [
                {
                    "sub_name": sub.sub_name,
                    "start_time": sub.start_time.strftime("%Y-%m-%d %H:%M") if sub.start_time else None,
                    "end_time": sub.end_time.strftime("%Y-%m-%d %H:%M") if sub.end_time else None,
                    "location": sub.location,
                    "description": sub.description,
                }
                for sub in sub_activities
            ]

        # 加载标签
        tags = [tag.tag_name for tag in act.tags]
        if tags:
            act_dict["tags"] = tags

        # 加载主办方信息
        organizer = db.query(Organizer).filter(Organizer.id == act.organizer_id).first()
        if organizer:
            act_dict["organizer_name"] = organizer.organizer_name
            act_dict["phone"] = organizer.phone
            act_dict["email"] = organizer.email

        result.append(act_dict)

    return result


def _generate_aliases(activity: Activity) -> List[str]:
    """
    从活动名自动生成常见别名/缩写。
    对应 v1 的 JSON 数据中的 aliases 字段。
    
    v2 数据库没有 aliases 字段，所以需要自动生成。
    """
    name = activity.activity_name
    aliases = []

    # 去掉年份后缀
    import re
    clean_name = re.sub(r'\s*\d{4}$', '', name).strip()
    if clean_name != name:
        aliases.append(clean_name)

    # 常见缩写规则
    suffix_map = {
        "博览会": ["博览", "展会"],
        "音乐节": ["音乐"],
        "论坛": [],
        "嘉年华": [],
    }
    for suffix, short_names in suffix_map.items():
        if suffix in name:
            for short in short_names:
                if short not in aliases:
                    aliases.append(short)

    return aliases


# ============================================
# 主对话函数
# ============================================

async def generate_ai_response(
    message: str,
    db: Session,
    session_id: Optional[str] = None,
    activity_id: Optional[int] = None,
) -> str:
    """
    智能对话主函数。
    
    对应 v1 的 answer_question，完整流程：
    1. 加载活动数据
    2. 检索/沿用上下文活动
    3. 语义抽取
    4. 构建 AI 上下文或渲染模板回复
    5. 调用 AI 润色（可选）
    """
    
    # 加载活动数据
    activities_data = load_activities_from_db(db, activity_id)

    # 获取会话上下文
    sid = session_id or "default"
    ctx = get_session_context(sid)
    current_activity = ctx.get("current_activity")

    # 步骤 1：检索活动
    activity, is_new = find_activity(
        activities_data, message, current_activity
    )

    # 没有匹配到活动
    if activity is None:
        from app.services.retriever import retrieve_activity_candidates
        candidates = retrieve_activity_candidates(activities_data, message)
        return get_no_activity_response(candidates)

    # 锁定新活动到会话上下文
    if is_new:
        set_session_activity(sid, activity, activity.get("id"))

    # 步骤 2：语义抽取
    extracted = extract_blocks(activity, message)

    # 步骤 3：生成回答
    if extracted:
        # 有相关信息 → AI 润色或模板渲染
        context = build_context_for_ai(activity, message)
        
        if settings.DASHSCOPE_API_KEY:
            try:
                ai_response = _call_dashscope(context, message)
                if ai_response:
                    return ai_response
            except Exception:
                pass

        # AI 不可用 → 用 render_response 纯模板渲染
        return render_response(extracted)
    else:
        # 没有匹配到具体信息块，但锁定了活动
        activity_name = activity.get("activity_name", "未知活动")
        return f"关于「{activity_name}」，您询问的内容暂不在已知信息范围内。\n\n您可以试试问：\n- 时间安排\n- 地点地址\n- 票务信息\n- 子活动安排\n- 交通导航"


# ============================================
# AI 调用
# ============================================

def _call_dashscope(context: str, question: str) -> Optional[str]:
    """
    调用通义千问 API，AI 只做润色。
    
    对应 v1 的 ai_client.py + prompt.py。
    输入是精简上下文（不是完整活动数据），极大降低 tokens 消耗。
    """
    import dashscope
    from dashscope import Generation

    dashscope.api_key = settings.DASHSCOPE_API_KEY

    system_prompt = """你是一个活动信息智能助手。
你只能基于【已知信息】回答问题，不能编造不存在的内容。
请将已知信息用自然、友好的语言呈现给用户。
如果已知信息中没有答案，请明确说明"暂无该信息"，并建议用户可以询问其他方面。"""

    user_content = f"""【已知信息】
{context}

【用户问题】
{question}"""

    response = Generation.call(
        model=settings.AI_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ],
        result_format='message',
        temperature=0.3,
        max_tokens=300,
    )

    if response.status_code == 200 and response.output:
        return response.output.choices[0].message.content.strip()

    return None