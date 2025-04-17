from json import load

from src.Agent import Agent

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

agents = []
for i in cfg[1:]:
    for j in range(i):
        agents.append(Agent())

