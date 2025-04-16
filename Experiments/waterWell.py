import time
from gdpc import Editor, nbt_tools, interface, Block
import os
import threading

editor = Editor(buffering=False)

def place_initial_structures():
    pos = (100, 100, -10)
    waterwell_nbt = nbt_tools.parseNbtFile(os.path.abspath("schematics/oak_waterwell.nbt"))
    interface.placeStructure(waterwell_nbt, position=pos)

    cauldron_pos = (103, 99, -7)
    editor.placeBlock(cauldron_pos, Block("water_cauldron[level=3]"))

    return cauldron_pos


def animate_cauldron_down(pos, current_level):
    x, start_y, z = pos
    bottom_y = start_y - 5

    editor.placeBlock((x, start_y, z), Block("air"))

    for y in range(start_y, bottom_y, -1):
        if current_level == "0":
            editor.placeBlock((x, y, z), Block("cauldron"))
        else:
            editor.placeBlock((x, y, z), Block(f"water_cauldron[level={current_level}]"))

        if y != start_y:
            editor.placeBlock((x, y + 1, z), Block("chain"))

        time.sleep(0.1)

    editor.placeBlock((x, bottom_y, z), Block("water_cauldron[level=3]"))

    return bottom_y

def animate_cauldron_up(pos):
    x, bottom_y, z = pos
    top_y = bottom_y + 5

    for y in range(bottom_y + 1, top_y + 1):
        editor.placeBlock((x, y, z), Block("water_cauldron[level=3]"))

        editor.placeBlock((x, y - 1, z), Block("air"))

        time.sleep(0.1)

    editor.placeBlock((x, bottom_y, z), Block("air"))


def get_cauldron_level(block):
    if not block:
        return None

    block_id = block.id
    if block_id.startswith("minecraft:"):
        block_id = block_id[10:]

    if "cauldron" not in block_id:
        return None

    if block_id == "cauldron":
        return "0"
    elif block_id == "water_cauldron":
        if hasattr(block, 'states') and 'level' in block.states:
            level = str(block.states['level'])
            return level
        else:
            return "1"
    elif block_id == "lava_cauldron":
        return "special"
    else:
        return "0"


def monitor_cauldron(cauldron_pos):
    x, y, z = cauldron_pos
    original_y = y

    animation_in_progress = False

    initial_block = editor.getBlock((x, y, z))
    last_level = get_cauldron_level(initial_block) or "3"

    while True:
        try:
            if animation_in_progress:
                time.sleep(0.5)
                continue

            block = editor.getBlock((x, y, z))
            current_level = get_cauldron_level(block)

            if current_level is not None:
                if current_level != last_level:
                    if current_level != "3":
                        animation_in_progress = True

                        bottom_y = animate_cauldron_down((x, y, z), current_level)

                        animate_cauldron_up((x, bottom_y, z))

                        editor.placeBlock((x, original_y, z), Block("water_cauldron[level=3]"))

                        last_level = "3"
                        animation_in_progress = False
                    else:
                        last_level = current_level

        except Exception as e:
            animation_in_progress = False

        time.sleep(0.5)


def main():
    cauldron_pos = place_initial_structures()

    monitor_thread = threading.Thread(target=monitor_cauldron, args=(cauldron_pos,), daemon=True)
    monitor_thread.start()

    try:
        print("Monitoring cauldron.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user")


if __name__ == "__main__":
    main()