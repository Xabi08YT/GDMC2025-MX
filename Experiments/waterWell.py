import time
from gdpc import Editor, nbt_tools, interface, Block
import os
import threading

#host = 'https://gdmc.xabigoity.fr/'

editor = Editor(buffering=False)

print("Placing water well...")
pos = (100, 100, -10)
waterwell_nbt = nbt_tools.parseNbtFile(os.path.abspath("oak_waterwell.nbt"))
interface.placeStructure(waterwell_nbt, position=pos)

print("Placing cauldron.")
cauldron_pos = (103, 99, -7)
editor.placeBlock(cauldron_pos, Block("water_cauldron[level=3]"))

chaudron_x, chaudron_y, chaudron_z = cauldron_pos

def monitor_cauldron():
    while True:
        try:
            block = editor.getBlock((chaudron_x, chaudron_y, chaudron_z))

            if ("cauldron" in str(block.id) and block.states['level'] != 3):
                print("Cauldron has been used! Animating mechanism...")
                cauldron = editor.getBlock(cauldron_pos)
                level = "1"
                if (cauldron.id == "water_cauldron"):
                    level = str(cauldron.states['level'])
                if level == "0":
                    level = "1"
                editor.placeBlock((chaudron_x, chaudron_y, chaudron_z), Block("air"))

                for y in range(chaudron_y, chaudron_y - 5, -1):
                    editor.placeBlock((chaudron_x, y, chaudron_z), Block("water_cauldron[level=" + level + "]"))
                    if y != chaudron_y - 5:
                        editor.placeBlock((chaudron_x, y, chaudron_z), Block("chain"))

                editor.placeBlock((chaudron_x, chaudron_y - 5, chaudron_z), Block("water_cauldron[level=3]"))

                for y in range(chaudron_y - 5, chaudron_y + 1, 1):
                    if y != chaudron_y - 5:
                        editor.placeBlock((chaudron_x, y, chaudron_z), Block("water_cauldron[level=3]"))
                    if y != chaudron_y:
                        editor.placeBlock((chaudron_x, y - 1, chaudron_z), Block("air"))
        except Exception as e:
            print(f"Error in monitor_cauldron: {e}")

        time.sleep(0.5)


monitor_thread = threading.Thread(target=monitor_cauldron, daemon=True)
monitor_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user")