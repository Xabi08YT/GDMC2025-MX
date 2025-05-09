from flask import Flask, render_template
from os import getpid, kill, listdir
from time import ctime
from pandas import read_csv
from visualizationServer.graphs import draw_general_needs_graphs, draw_general_needs_decay_graphs

app = Flask("visualizationServer")


@app.route("/")
def index():
    tmp = [(f.split(".")[0], ctime(int(f.split(".")[0]))) for f in listdir("logs")]
    return render_template("index.html", files=tmp)


@app.route("/shutdown")
def shutdown():
    print("Shutting down. Expect an error due to shutdown.")
    pid = getpid()
    kill(pid, 2)


@app.route("/sim/<simID>")
def sim(simID):
    return render_template("simulation.html", simID=simID)


@app.route("/sim/<simID>/global")
def globalgraphs(simID):
    df = read_csv("logs/" + simID + ".csv")
    df["happiness"] = 0
    df["happiness_decay"] = 0

    gneedsurl = draw_general_needs_graphs(df)
    gneedsdecayurl = draw_general_needs_decay_graphs(df)

    return render_template("globalgraphs.html", general_plot_needs_url=gneedsurl, general_plot_decayurl=gneedsdecayurl)


app.run(debug=True)
