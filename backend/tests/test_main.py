from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ask_annual_leave():
    r = client.post("/api/ask", json={"question": "年假有多少天？"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is True
    assert "年假" in data["answer"]
    assert len(data["sources"]) > 0


def test_ask_salary():
    r = client.post("/api/ask", json={"question": "工资什么时候发放？"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is True
    assert "10日" in data["answer"] or "薪资" in data["answer"]


def test_ask_unknown():
    r = client.post("/api/ask", json={"question": "公司食堂有没有麻辣烫？"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is False
    assert "暂未收录" in data["answer"]


def test_ask_empty():
    r = client.post("/api/ask", json={"question": ""})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is False


def test_list_policies():
    r = client.get("/api/policies")
    assert r.status_code == 200
    policies = r.json()
    assert len(policies) >= 5
    assert "title" in policies[0]


def test_ask_sick_leave():
    r = client.post("/api/ask", json={"question": "病假工资怎么算？"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is True
    assert "病假" in data["answer"]


def test_ask_maternity():
    r = client.post("/api/ask", json={"question": "产假有多少天？"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is True
    assert "产假" in data["answer"]
