# GDMC 2025 submission by Tsukuba Team

## Description
Source code of the project that will be submitted to the 2025 edition of the GDMC challenge by the team of the University of Tsukuba.
This project is based on multi-agent system simulation to procedurally generate naturalistic settlements in Minecraft. Autonomous agents explore the environment, build houses based on their needs, and form relationships with other agents.

## How to use
1. Clone the repository:
   ```bash
   git clone git@github.com:Xabi08YT/GDMC2025-MX.git
   ```
   
2. Install Python 3.10 or higher.

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
4. Add the [GDPC Interface](https://modrinth.com/mod/gdmc-http-interface/version/1.6.0-1.21.4) mod to Minecraft (1.21.4)
    
5. Open a minecraft world, and run the `setbuildarea <x0> <y0> <z0> <x1> <y1> <z1>` command

6. Finally, run the main script:
   ```bash
    python main.py
    ```
   
## Dockerfile
In the future, you will be able to run the code with Docker:
```bash
docker build -t gdmc2025 .
docker run -it gdmc2025
```

## How it works

### Agents
Agents are autonomous entities that explore and interact with the Minecraft world. Each agent:
- Has basic needs (hunger, energy, social, health) that decay over time
- Possesses attributes like muscular strength that affect their capabilities
- Observes and learns about their environment as they explore
- Makes decisions based on their current needs and observations
- Can build their own houses when conditions are right
- Can have relationships with other agents

### Buildings
- **Houses:** Agents build their own houses after exploring the area, typically after the simulation has run for half of its duration
- **Firecamp:** A central structure that serves as the village center, randomly placed in the build area

### Jobs
Agents can take on different jobs that determine their:
- Primary activities during the simulation
- Resource gathering priorities
- Building preferences
- Movement patterns within the world

### Relationships
As agents interact, they develop relationships with each other:
- Relationships can influence agent behavior and decision-making
- Social needs can be fulfilled through positive interactions
- Agents track their relationships in a dictionary with detailed information about each connection

The simulation runs for a configurable number of turns, with agents exploring, building, and interacting based on their individual states and the environment around them.

## Authors
 - Matéo GUIDI <mateo.guidi5@gmail.com>
 - Xabi GOÏTY <xabigoity@gmail.com>
 - Claus Aranha (Supervisor) <caranha@cs.tsukuba.ac.jp>

## License
Check the LICENSE file.