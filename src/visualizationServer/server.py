from flask import Flask, render_template, request, jsonify
from os import getpid, kill, listdir
from time import ctime
from pandas import read_csv
from matplotlib import pyplot as plt

app = Flask("visualizationServer")

@app.route("/")
def index():
    tmp = [(f.split(".")[0],ctime(int(f.split(".")[0]))) for f in listdir("logs")]
    return render_template("index.html", files=tmp)

@app.route("/shutdown")
def shutdown():
    print("Shutting down. Expect an error due to shutdown.")
    pid = getpid()
    kill(pid,2)

@app.route("/sim/<simID>")
def sim(simID):
    return render_template("simulation.html", simID=simID)

@app.route("/sim/<simID>/global")
def globalgraphs(simID):
    df = read_csv("logs/"+simID+".csv")
    plt
    return render_template("globalgraphs.html")
app.run(debug=True)