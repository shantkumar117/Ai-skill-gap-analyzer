from flask import redirect
from app import app

@app.route("/")
def root_redirect():
    return redirect("/analyze")

