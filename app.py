from flask import Flask, render_template, request

app=Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    prompt=request.form["message"]
    return render_template("success.html")