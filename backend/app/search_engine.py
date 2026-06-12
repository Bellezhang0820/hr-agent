import re
from typing import Optional
from app.knowledge_base import POLICIES


def _tokenize(text: str) -> list[str]:
    """简单中文分词：按字、词切分"""
    text = text.lower()
    tokens = re.findall(r'[\u4e00-\u9fff]{1,4}|[a-z0-9]+', text)
    return tokens


def _score(query: str, policy: dict) -> float:
    """计算问题与政策的匹配分数"""
    score = 0.0
    query_lower = query.lower()

    # 关键词直接命中（最高权重）
    for kw in policy["keywords"]:
        if kw in query_lower:
            score += 10.0

    # 标题词命中
    for ch in policy["title"]:
        if ch in query_lower:
            score += 1.0

    # 内容分词匹配
    q_tokens = set(_tokenize(query))
    c_tokens = set(_tokenize(policy["content"]))
    overlap = q_tokens & c_tokens
    score += len(overlap) * 0.5

    return score


def search(query: str, top_k: int = 3, threshold: float = 5.0) -> list[dict]:
    """检索最相关的政策条目"""
    scored = [(p, _score(query, p)) for p in POLICIES]
    scored.sort(key=lambda x: x[1], reverse=True)
    results = [(p, s) for p, s in scored if s >= threshold]
    return results[:top_k]


def answer(query: str) -> dict:
    """生成回答"""
    results = search(query)

    if not results:
        return {
            "found": False,
            "answer": "该问题暂未收录，请联系HR进一步确认。",
            "sources": []
        }

    # 取最相关的条目
    best_policy, best_score = results[0]

    # 构建回答
    reply_lines = [f"**{best_policy['title']}**\n"]
    reply_lines.append(best_policy["content"])

    # 如果有次相关条目也一并提示
    if len(results) > 1:
        extra = results[1][0]
        reply_lines.append(f"\n相关政策：您也可以参考《{extra['title']}》了解更多信息。")

    sources = [p["source"] for p, _ in results[:2]]

    return {
        "found": True,
        "answer": "\n".join(reply_lines),
        "sources": sources
    }
