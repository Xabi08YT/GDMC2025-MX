import time

from gdpc import Editor, nbt_tools, interface, Block
import os
import threading

host = 'https://gdmc.xabigoity.fr/'

editor = Editor(buffering=False, host=host)

print("Placing water well...")
pos = (100, 100, -10)
waterwell_nbt = nbt_tools.parseNbtFile(os.path.abspath("schematics/oak_waterwell.nbt"))
interface.placeStructure(waterwell_nbt, position=pos,host=host)

print("Placing cauldron.")
cauldron_pos = (103, 99, -7)
editor.placeBlock(cauldron_pos, Block("water_cauldron[level=3]"))

chaudron_x, chaudron_y, chaudron_z = cauldron_pos

def monitor_cauldron():
    while True:
        block = editor.getBlock((chaudron_x, chaudron_y, chaudron_z))

        print(block)
        if ("water_cauldron" in str(block.id) or "cauldron" in str(block.id) and "level=3" not in str(block)):
            print("Le chaudron a été utilisé ! Animation du mécanisme...")
            level = editor.getBlock(chaudron_x, chaudron_y, chaudron_z).states
            editor.placeBlock((chaudron_x, chaudron_y, chaudron_z), Block("air"))

            for y in range(chaudron_y, chaudron_y - 5, -1):
                editor.placeBlock((chaudron_x, y, chaudron_z), Block("cauldron"))
                time.sleep(0.5)
                if y != chaudron_y - 5:
                    editor.placeBlock((chaudron_x, y, chaudron_z), Block("chain"))

            editor.placeBlock((chaudron_x, chaudron_y - 5, chaudron_z), Block("water_cauldron[level=3]"))
            time.sleep(1)

            for y in range(chaudron_y - 5, chaudron_y + 1, 1):
                if y != chaudron_y - 5:
                    editor.placeBlock((chaudron_x, y, chaudron_z), Block("water_cauldron[level=3]"))
                    time.sleep(0.5)
                if y != chaudron_y:
                    editor.placeBlock((chaudron_x, y - 1, chaudron_z), Block("air"))

            print("Le chaudron est prêt à être utilisé à nouveau !")

        time.sleep(2)


monitor_thread = threading.Thread(target=monitor_cauldron, daemon=True)
monitor_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stoppé.")