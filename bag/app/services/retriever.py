"""
会场精灵 v2 - 活动检索引擎

基于 v1 版本的检索算法，适配 v2 数据库结构。
核心流程：用户问题 → 活动检索(打分+排序+选择) → 语义抽取(semantic_map) → 已知信息 → AI润色 → 回答

设计目标：AI 只做润色，不参与信息检索，极大降低 tokens 消耗。
"""

from typing import Optional, List


# ============================================
# 语义映射表（对应 v1 的 semantic_map.py）
# 将用户问题中的关键词映射到数据库字段
# ============================================

SEMANTIC_MAP = {
    "location": {
        "keywords": ["地点", "位置", "在哪里", "在哪", "地址", "地方"],
        "fields": ["address"],
        "type": "string",
    },
    "navigation": {
        "keywords": ["怎么去", "导航", "路线", "怎么到", "怎么走", "交通", "地铁", "公交", "驾车"],
        "field": "address",
        "type": "navigation",
    },
    "time": {
        "keywords": ["时间", "几点", "日期", "时候", "开始", "结束", "什么时候", "多久"],
        "fields": ["start_time", "end_time"],
        "type": "composite",
    },
    "ticket": {
        "keywords": ["票", "价格", "多少钱", "购票", "票价", "买票", "团购", "门票", "免费"],
        "fields": ["requires_ticket", "ticket_price", "ticket_url", "ticket_deadline"],
        "type": "composite",
    },
    "description": {
        "keywords": ["是什么", "简介", "介绍", "关于", "什么活动", "干嘛"],
        "field": "description",
        "type": "string",
    },
    "sub_activities": {
        "keywords": ["子活动", "分会场", "分论坛", "专场", "安排", "日程", "议程", "流程", "节目"],
        "field": "sub_activities",
        "type": "list",
    },
}


# ============================================
# 活动检索：打分 + 候选排序 + 选择
# 对应 v1 的 retriever.py
# ============================================

def score_activity(activity: dict, question: str) -> dict:
    """
    对单个活动与用户问题的相关性打分。
    
    评分维度（基于 v1 算法，适配 v2 数据库字段）：
    1. 活动名关键词命中（拆字匹配）      +0.4
    2. 别名/缩写命中                      +0.5
    3. 活动类型词命中（博览会/音乐节等）   +0.3
    4. 地点弱命中                         +0.2
    5. 时间弱命中                         +0.1
    """
    q = question.lower()
    score = 0.0
    matched = []

    # 1️⃣ 活动名关键词命中（逐字拆分匹配）
    name = activity.get("activity_name", "")
    for token in name:
        if token and token in q:
            score += 0.4
            matched.append("name_partial")
            break

    # 2️⃣ aliases 命中（别名/缩写）
    aliases = activity.get("aliases", [])
    for alias in aliases:
        if alias.lower() in q:
            score += 0.5
            matched.append("alias")
            break

    # 3️⃣ 活动类型词（从活动名和描述中提取的类型关键词）
    type_keywords_map = {
        "博览会": ["博览会", "展览", "展"],
        "音乐节": ["音乐节", "音乐", "演出", "演唱会", "乐队"],
        "论坛": ["论坛", "峰会", "会议", "研讨会", "大会"],
        "赛事": ["赛事", "比赛", "竞赛", "锦标赛"],
        "嘉年华": ["嘉年华", "狂欢", "派对"],
    }
    for type_name, type_words in type_keywords_map.items():
        if any(tw in q for tw in type_words):
            if any(tw in name for tw in type_words) or \
               any(tw in (activity.get("description") or "") for tw in type_words):
                score += 0.3
                matched.append("type")
                break

    # 4️⃣ 地点弱命中
    location = activity.get("address", "")
    if location:
        for city in ["上海", "北京", "广州", "深圳", "杭州", "成都", "武汉", "南京"]:
            if city in q and city in location:
                score += 0.2
                matched.append("location")
                break

    # 5️⃣ 时间弱命中
    date_str = activity.get("start_time", "")
    if date_str:
        for time_word in ["今天", "明天", "后天", "本周", "周末", "近期"]:
            if time_word in q:
                score += 0.1
                matched.append("date")
                break

    return {
        "activity": activity,
        "score": round(min(score, 1.0), 2),
        "matched": matched,
    }


def retrieve_activity_candidates(
    activities: List[dict],
    question: str,
) -> List[dict]:
    """
    对所有活动打分并排序，返回候选列表。
    对应 v1 的 retrieve_activity_candidates。
    """
    scored = []
    for act in activities:
        result = score_activity(act, question)
        if result["score"] > 0:
            scored.append(result)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def select_activity(
    candidates: List[dict],
    total_activities: int,
) -> Optional[dict]:
    """
    从候选列表中选择最佳活动。
    对应 v1 的 select_activity。
    
    选择策略：
    1. 只有一个活动 → 直接选（宽松）
    2. 活动数 ≤ 2 → 分数 ≥ 0.1 即选
    3. 分数明显领先（领先第二名 ≥ 0.3）→ 选
    4. 分数本身 ≥ 0.6 → 选
    5. 否则 → 不确定，需要用户补充信息
    """
    if not candidates:
        return None

    best = candidates[0]

    # 1️⃣ 只有一个活动，直接选
    if total_activities == 1:
        return best["activity"]

    # 2️⃣ 活动数量 ≤ 2：非常宽松
    if total_activities <= 2 and best["score"] >= 0.1:
        return best["activity"]

    # 3️⃣ 分数明显领先
    if len(candidates) > 1:
        second = candidates[1]
        if best["score"] - second["score"] >= 0.3:
            return best["activity"]

    # 4️⃣ 分数本身足够高
    if best["score"] >= 0.6:
        return best["activity"]

    # 5️⃣ 否则不确定
    return None


def find_activity(
    activities: List[dict],
    question: str,
    current_activity: Optional[dict] = None,
) -> tuple:
    """
    完整检索流程：如果有上下文活动则沿用，否则检索新活动。
    
    返回: (activity, is_new)
      - activity: 锁定的活动 dict 或 None
      - is_new: True 表示本次新检索到的，False 表示沿用上下文
    """
    # 如果已有上下文活动，直接沿用（v1 的 current_activity 机制）
    if current_activity is not None:
        return current_activity, False

    candidates = retrieve_activity_candidates(activities, question)
    selected = select_activity(candidates, len(activities))

    if selected is None:
        if candidates:
            return None, False
        return None, False

    return selected, True


# ============================================
# 语义抽取：从活动数据中提取问题相关的字段
# 对应 v1 的 extractor.py
# ============================================

def extract_blocks(activity: dict, question: str) -> dict:
    """
    根据用户问题中的关键词，从活动数据中抽取相关字段。
    对应 v1 的 extract_blocks。
    
    返回格式:
    {
        "location": {"type": "string", "value": "上海市浦东新区龙阳路2345号"},
        "time": {"type": "composite", "value": {"start_time": "...", "end_time": "..."}},
        ...
    }
    """
    q = question.lower()
    result = {}

    for semantic, config in SEMANTIC_MAP.items():
        if not any(k in q for k in config["keywords"]):
            continue

        t = config.get("type", "string")

        # 复合字段
        if t == "composite":
            values = {}
            fields = config.get("fields", [])
            for f in fields:
                if f in activity and activity[f] is not None:
                    values[f] = activity[f]
            if values:
                result[semantic] = {"type": "object", "value": values}

        # 列表字段
        elif t == "list":
            field = config.get("field")
            value = activity.get(field)
            if value is not None and isinstance(value, list) and len(value) > 0:
                result[semantic] = {"type": "list", "value": value}

        # 导航字段
        elif t == "navigation":
            field = config.get("field")
            value = activity.get(field)
            if value is not None:
                result[semantic] = {"type": "navigation", "value": value}

        # 普通字符串字段
        else:
            field = config.get("field")
            if not field:
                fields = config.get("fields", [])
                if fields:
                    field = fields[0]
            if field:
                value = activity.get(field)
                if value is not None:
                    result[semantic] = {"type": "string", "value": str(value)}

    return result


# ============================================
# 回答渲染：将抽取结果转为用户可读的文本
# 对应 v1 的 responder.py
# ============================================

def render_block(semantic: str, block: dict) -> List[str]:
    """渲染单个语义块为文本行"""
    t = block["type"]
    v = block["value"]
    lines = []

    if t == "string":
        lines.append(str(v))

    elif t == "object":
        lines.append("📌 相关信息：")
        if isinstance(v, dict):
            for key, value in v.items():
                display_name = {
                    "address": "📍 地址",
                    "start_time": "⏰ 开始时间",
                    "end_time": "🕕 结束时间",
                    "requires_ticket": "🎫 需要购票",
                    "ticket_price": "💰 票价",
                    "ticket_url": "🔗 购票链接",
                    "ticket_deadline": "⏳ 购票截止",
                }.get(key, f"  - {key}")
                if key == "requires_ticket":
                    value = "是" if value else "否（免费入场）"
                lines.append(f"  {display_name}：{value}")

    elif t == "list":
        lines.append("📋 相关安排：")
        for item in v:
            if isinstance(item, dict):
                parts = [str(x) for x in item.values()]
                lines.append("  - " + " | ".join(parts))
            else:
                lines.append(f"  - {item}")

    elif t == "navigation":
        lines.append(f"📍 活动地址：{v}")
        lines.append("🧭 导航提示：")
        lines.append("  - 可在高德/百度/Google 地图中搜索上述地址进行导航")

    return lines


def render_response(extracted: dict) -> str:
    """将所有抽取块渲染为完整回答文本"""
    lines = []
    for semantic, block in extracted.items():
        if "type" not in block or "value" not in block:
            continue
        lines.extend(render_block(semantic, block))
    return "\n".join(lines) if lines else "暂无相关信息"


# ============================================
# 为 AI 构建精简上下文
# ============================================

def build_context_for_ai(activity: dict, question: str) -> str:
    """
    将抽取结果转为给 AI 的精简上下文文本。
    AI 只需要润色这段文本，不需要检索信息。
    """
    extracted = extract_blocks(activity, question)

    if not extracted:
        activity_name = activity.get("activity_name", "未知活动")
        address = activity.get("address", "未知地点")
        start_time = activity.get("start_time", "未知时间")
        return f"活动名称：{activity_name}\n地点：{address}\n时间：{start_time}\n\n用户提问内容不在已知信息范围内，请礼貌说明暂无该信息，并建议用户询问其他方面（时间/地点/票务/子活动安排等）。"

    # 先用 render_response 生成基础文本，再让 AI 润色
    raw_text = render_response(extracted)
    activity_name = activity.get("activity_name", "")

    return f"活动：{activity_name}\n已知信息：\n{raw_text}"


def get_no_activity_response(candidates: List[dict] = None) -> str:
    """
    没有匹配到活动时的回复。
    如果有候选但置信度不足，提示用户更具体地描述。
    """
    if candidates and len(candidates) > 0:
        names = [c["activity"].get("activity_name", "") for c in candidates[:3]]
        name_list = "、".join(names)
        return f"我找到了多个可能的活动：{name_list}\n请说得更具体一点，比如加上活动名称，这样我才能准确回答 😊"

    return """您好！我是会场精灵助手 👋

目前暂未收录您提到的活动信息。您可以：
• 更准确地描述活动名称
• 询问已收录的活动信息

例如您可以问：
- "国际创新博览会的时间和地点"
- "门票多少钱？"
- "怎么去活动现场？" """