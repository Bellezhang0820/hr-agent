from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.search_engine import answer
import os

app = FastAPI(title="HR智能体 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    found: bool
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AnswerResponse)
def ask(req: QuestionRequest):
    q = req.question.strip()
    if not q:
        return AnswerResponse(
            found=False,
            answer="请输入您的问题。",
            sources=[]
        )
    result = answer(q)
    return AnswerResponse(**result)


@app.get("/api/policies")
def list_policies():
    from app.knowledge_base import POLICIES
    return [{"id": p["id"], "title": p["title"], "source": p["source"]} for p in POLICIES]


# 挂载前端静态文件（生产用）
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        index = os.path.join(frontend_dist, "index.html")
        return FileResponse(index)
