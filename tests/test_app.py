import os, tempfile
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
from app import app

def test_pages_load():
    c = app.test_client()
    for url in ["/", "/tasks", "/add", "/subjects", "/health"]:
        assert c.get(url).status_code == 200

def test_add_task():
    c = app.test_client()
    r = c.post("/add", data={"title": "Finish case study", "subject": "DevOps"}, follow_redirects=True)
    assert b"Finish case study" in r.data
