from buildings.Building import Building
from gdpc import Editor
import json
import random  # Ajout de l'import pour les choix aléatoires de couleurs

from buildings.House import House
from buildings.Firecamp import Firecamp
from buildings.JobBuilding import JobBuilding


class BookGenerator:

    def __init__(self, simulation):
        self.simulation = simulation
        self.give_village_book_to_players()

    COLORS = ["dark_red", "red", "gold", "dark_green", "green", "aqua",
              "dark_aqua", "dark_blue", "blue", "light_purple", "dark_purple"]

    def generate_buildings_book(self, title="Simulation's Book", author="MX"):
        pages = []
        current_page_content = []
        sorted_buildings = sorted(Building.BUILDINGS,
                                  key=lambda b: (0 if isinstance(b, Firecamp) else
                                                 (1 if isinstance(b, JobBuilding) else
                                                  (2 if isinstance(b, House) else 3))))
        buildings_per_page = 6
        building_count = 0
        number_building_pages = (len(sorted_buildings) + buildings_per_page - 1) // buildings_per_page

        current_page_content.append('{"text":"Buildings (1/' + str(number_building_pages) + ')"}')
        current_page_content.append('{"text":"\\n\\n"}')

        for building in sorted_buildings:
            if building is not None and building.center_point is not None:
                if building_count >= buildings_per_page:
                    pages.append("[" + ",".join(current_page_content) + "]")
                    current_page_content = []
                    current_page_content.append('{"text":"Buildings (' + str(len(pages) + 1) + '/' + str(number_building_pages) + ')"}')
                    current_page_content.append('{"text":"\\n\\n"}')
                    building_count = 0

                click_action = {
                    "text": f"-{building.name}",
                    "color": "dark_purple" if isinstance(building, House) else "gold" if isinstance(building, Firecamp) else "blue" if isinstance(building, JobBuilding) else "dark_gray",
                    "clickEvent": {
                        "action": "run_command",
                        "value": f"/tp @s {building.center_point[0]} {self.simulation.heightmap[building.center_point[0], building.center_point[1]]} {building.center_point[1]}"
                    },
                    "hoverEvent": {
                        "action": "show_text",
                        "contents": f"Click to be teleported at {building.name}"
                    }
                }
                current_page_content.append(json.dumps(click_action))
                current_page_content.append('{"text":"\\n"}')
                building_count += 1

        if current_page_content:
            pages.append("[" + ",".join(current_page_content) + "]")

        for agent in self.simulation.agents:
            current_page_content = []
            agent_name = agent.name if len(agent.name) <= 16 else agent.name[:14]+ '..'
            current_page_content.append('{"text":"' + agent_name + '"}')
            current_page_content.append('{"text":"\\n\\n"}')

            if agent.dead:
                current_page_content.append('{"text":"Dead: "}')
                current_page_content.append('{"text":"Yes", "color":"dark_red"}')
            else:
                current_page_content.append('{"text":"Dead: "}')
                current_page_content.append('{"text":"No", "color":"green"}')
            current_page_content.append('{"text":"\\n"}')

            happiness_value = round(agent.happiness, 2)
            happiness_color = "green" if happiness_value > 0.5 else "aqua" if happiness_value > -0.5 else "red"
            current_page_content.append('{"text":"Happiness: "}')
            current_page_content.append('{"text":"' + str(happiness_value) + '", "color":"' + happiness_color + '"}')
            current_page_content.append('{"text":"\\n"}')

            # Position
            position_action = {
                "text": "Position: (" + str(int(agent.x)) + ", " + str(int(agent.z)) + ")",
                "italic": True,
                "clickEvent": {
                    "action": "run_command",
                    "value": f"/tp @s {int(agent.x)} {self.simulation.heightmap[int(agent.x), int(agent.z)]} {int(agent.z)}"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "contents": f"Click to be teleported at {agent.name}'s position"
                }
            }
            current_page_content.append(json.dumps(position_action))
            current_page_content.append('{"text":"\\n"}')

            # Maison
            current_page_content.append('{"text":"House: "}')
            home_status = "Got one" if agent.home else "None"
            home_color = "green" if agent.home else "red"
            current_page_content.append('{"text":"' + home_status + '", "color":"' + home_color + '"}')
            current_page_content.append('{"text":"\\n"}')

            # Travail
            current_page_content.append('{"text":"Job: "}')
            job_status = str(agent.job.job_type.value) if agent.job else "None"
            job_color = "blue" if agent.job else "red"
            current_page_content.append('{"text":"' + job_status + '", "color":"' + job_color + '"}')
            current_page_content.append('{"text":"\\n"}')

            # Attributs
            current_page_content.append('{"text":"Attributes:", "underlined":true}')
            current_page_content.append('{"text":"\\n"}')
            for attr, value in agent.attributes.items():
                formatted_value = round(value, 2)
                attr_color = "green" if formatted_value > 75 else "gold" if formatted_value > 40 else "red"
                current_page_content.append('{"text":"-' + str(attr).capitalize() + ': ", "italic":true}')
                current_page_content.append('{"text":"' + str(formatted_value) + '", "color":"' + attr_color + '"}')
                current_page_content.append('{"text":"\\n"}')

            pages.append("[" + ",".join(current_page_content) + "]")

        book_data = {
            "title": title,
            "author": author,
            "pages": pages
        }

        return book_data

    def give_village_book_to_players(self, editor = Editor(buffering=True)):
        book_data = self.generate_buildings_book()
        command = f'give @a written_book[written_book_content={{title:"{book_data["title"]}",author:"{book_data["author"]}",pages:{book_data["pages"]}}}]'
        editor.runCommand(command)
