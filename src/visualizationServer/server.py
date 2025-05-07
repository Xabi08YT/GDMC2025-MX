from flask import Flask, render_template, request, jsonify

app = Flask("visualizationServer")

@app.route("/")
def index():
    return "<p>Hello, World!</p>"

@app.route("/sim/<timeStamp>")
def sim(timeStamp):
    return f"Ok, timeStamp: {timeStamp}"

app.run(debug=True)