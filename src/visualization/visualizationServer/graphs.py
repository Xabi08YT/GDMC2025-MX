from pandas import DataFrame, concat
from matplotlib import pyplot as plt
from io import BytesIO

import base64


def draw_means_graph(df, params: dict, title):
    columns = list(params.keys())
    columns.append("turn")
    finalDF = DataFrame([], columns=columns)

    for turn in df["turn"].unique():
        tmpDF = df[df["turn"] == turn]
        tmp = {"turn": turn}
        for k in params.keys():
            tmp[k] = tmpDF[params[k][0]].mean()

        finalDF = concat([DataFrame(tmp, columns), finalDF], ignore_index=True)

    img = BytesIO()

    for k in params.keys():
        plt.plot(finalDF["turn"], finalDF[k], label=params[k][1])

    plt.title(title)
    plt.legend()

    plt.savefig(img)

    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')

def draw_general_needs_graphs(df):
    params = {
        "mean_hunger": ["hunger", "Mean of Hunger need"],
        "mean_social": ["social", "Mean of Social need"],
        "mean_energy": ["energy", "Mean of Energy need"],
        "mean_health": ["health", "Mean of Health need"],
        "mean_happiness": ["happiness", "Mean of Happiness"]
    }
    return draw_means_graph(df, params, "Means of the needs values as well as happiness")

def draw_general_needs_decay_graphs(df):
    params = {
        "mean_hunger_decay": ["hunger_decay", "Mean of Hunger need decay rate"],
        "mean_social_decay": ["social_decay", "Mean of Social need decay rate"],
        "mean_energy_decay": ["energy_decay", "Mean of Energy need decay rate"],
        "mean_health_decay": ["health_decay", "Mean of Health need decay rate"],
        "mean_happiness_decay": ["happiness_decay", "Mean of Happiness decay rate"],
    }

    return draw_means_graph(df, params, "Means of needs and happiness decay values")

def draw_jobless_count_graph(df):
    columns = ["turn,jobless_count"]
    finalDF = DataFrame([], columns=columns)
    for turn in df["turn"].unique():
        tmpDF = df[df["turn"] == turn]
        tmp = {
            "turn": turn,
            "jobless_count": len(tmpDF[tmpDF["job"] == "Unemployed"])
        }

        finalDF = concat([finalDF, DataFrame(tmp,columns)], ignore_index=True)

    img = BytesIO()

    plt.plot(finalDF["turn"], finalDF["jobless_count"])

    plt.title("Number of jobless agents per turn")

    plt.savefig(img)

    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')