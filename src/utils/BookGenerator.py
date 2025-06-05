from buildings.Building import Building
from gdpc import Editor
import json

from buildings.House import House
from buildings.Firecamp import Firecamp
from buildings.JobBuilding import JobBuilding


class BookGenerator:

    def __init__(self, simulation):
        self.simulation = simulation
        self.give_village_book_to_players()

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
        current_page_content.append(f'{"text":"Buildings List (1/{number_building_pages}\\n\\n"}')



        for building in sorted_buildings:
            if building is not None and building.center_point is not None:
                if building_count >= buildings_per_page:
                    pages.append("[" + ",".join(current_page_content) + "]")
                    current_page_content = []
                    current_page_content.append(f'{"text":"Buildings List ({building_count // buildings_per_page}/{number_building_pages})\\n\\n"}')
                    building_count = 0

                click_action = {
                    "text": f"-{building.name}",
                    "clickEvent": {
                        "action": "run_command",
                        "value": f"/tp @s {building.center_point[0]} {self.simulation.heightmap[building.center_point[0], building.center_point[1]]} {building.center_point[1]}"
                    },
                    "hoverEvent": {
                        "action": "show_text",
                        "contents": f"Cliquez pour vous téléporter à {building.name}"
                    }
                }
                current_page_content.append(json.dumps(click_action))
                current_page_content.append('{"text":"\\n"}')
                building_count += 1

        if current_page_content:
            pages.append("[" + ",".join(current_page_content) + "]")

        book_data = {
            "title": title,
            "author": author,
            "pages": pages #['{"text":"Hello"}', '{"text":"World"}']
        }

        return book_data

    def give_village_book_to_players(self, editor = Editor(buffering=True)):
        book_data = self.generate_buildings_book()
        command = f'give @a written_book[written_book_content={{title:"{book_data["title"]}",author:"{book_data["author"]}",pages:{book_data["pages"]}}}]'
        print(f"Executing command: {command}")
        editor.runCommand(command)