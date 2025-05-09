import base64
from io import BytesIO

from flask import Flask, render_template, request, jsonify
from os import getpid, kill, listdir
from time import ctime
from pandas import read_csv, DataFrame, concat
from matplotlib import pyplot as plt

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
    columns = ["turn", "mean_hunger", "mean_social", "mean_energy", "mean_health"]
    finalDF = DataFrame([], columns=columns)

    for turn in df["turn"].unique():
        tmpDF = df[df["turn"] == turn]
        tmp = {
            "turn": turn,
            "mean_hunger": tmpDF["hunger"].mean(),
            "mean_social": tmpDF["social"].mean(),
            "mean_energy": tmpDF["energy"].mean(),
            "mean_health": tmpDF["health"].mean()
        }

        finalDF = concat([DataFrame(tmp, columns), finalDF], ignore_index=True)

    print(finalDF.head())
    img = BytesIO()

    plt.plot(finalDF["turn"], finalDF["mean_hunger"], label="Mean of Hunger need")
    plt.plot(finalDF["turn"], finalDF["mean_social"], label="Mean of Social need")
    plt.plot(finalDF["turn"], finalDF["mean_energy"], label="Mean of Energy need")
    plt.plot(finalDF["turn"], finalDF["mean_health"], label="Mean of Health need")
    plt.title("General informations during the simulation")
    plt.legend()

    plt.savefig(img)

    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template("globalgraphs.html", plot_url=plot_url)


app.run(debug=True)
