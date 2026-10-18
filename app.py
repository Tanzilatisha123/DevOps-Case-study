import os, sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db"),
)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            due_date TEXT,
            done INTEGER NOT NULL DEFAULT 0)""")
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


@app.route("/")
def dashboard():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = db.execute("SELECT COUNT(*) FROM tasks WHERE done=1").fetchone()[0]
    overdue = db.execute("SELECT COUNT(*) FROM tasks WHERE done=0 AND due_date < ?",
                         (date.today().isoformat(),)).fetchone()[0]
    upcoming = db.execute("SELECT * FROM tasks WHERE done=0 AND due_date != '' "
                          "ORDER BY due_date LIMIT 5").fetchall()
    return render_template("dashboard.html", total=total, done=done,
                           pending=total - done, overdue=overdue, upcoming=upcoming)


@app.route("/tasks")
def tasks():
    subject = request.args.get("subject", "")
    db = get_db()
    if subject:
        rows = db.execute("SELECT * FROM tasks WHERE subject=? ORDER BY done, due_date", (subject,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM tasks ORDER BY done, due_date").fetchall()
    return render_template("tasks.html", tasks=rows, selected=subject)


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        subject = request.form.get("subject", "").strip()
        if not title or not subject:
            flash("Title and subject are required.", "error")
            return redirect(url_for("add_task"))
        db = get_db()
        db.execute("INSERT INTO tasks(title,subject,priority,due_date) VALUES(?,?,?,?)",
                   (title, subject, request.form.get("priority", "Medium"),
                    request.form.get("due_date", "")))
        db.commit()
        flash("Task added!", "success")
        return redirect(url_for("tasks"))
    return render_template("add_task.html")


@app.route("/subjects")
def subjects():
    rows = get_db().execute("""SELECT subject, COUNT(*) total, SUM(done) done
                               FROM tasks GROUP BY subject ORDER BY subject""").fetchall()
    return render_template("subjects.html", subjects=rows)


@app.route("/complete/<int:task_id>")
def complete(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    db.commit()
    return redirect(url_for("tasks"))


@app.route("/delete/<int:task_id>")
def delete(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    db.commit()
    return redirect(url_for("tasks"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
