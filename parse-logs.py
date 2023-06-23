from enum import Enum
import os
from pathlib import Path
import yaml

LOGS_DIR = Path("./logs")
CHECKS_FILE = Path("checks.yaml")

COLON_DELIMITER = ":"
NUMBER_DELIMITER = " #"
HYPHEN_DELIMITER = "-"
COMMA_DELIMITER = ","
NEW_LINE_DELIMITER = "\n"

SPACE = " "
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
DEFEAT_DEMISE = "Defeat Demise"
SMALL_KEY = "Small Key"
BOSS_KEY = "Boss Key"
EXCLUDED_LOCATIONS = "  excluded-locations"

if not os.path.isdir(LOGS_DIR):
    raise NotADirectoryError(LOGS_DIR)


class Log(Enum):
    SOTS = "SotS"
    BARREN = "Barren Regions"
    NON_PROGRESS = "Nonprogress Regions"
    PLAYTHROUGH = "Playthrough"
    SV = "Skyview"
    ET = "Earth Temple"
    LMF = "Lanayru Mining Facility"
    AC = "Ancient Cistern"
    SSH = "Sandship"
    FS = "Fire Sanctuary"

excluded_locations = []

sots = {}
barren = {}
nonprogress = {}
playthrough = []

sv = {}
et = {}
lmf = {}
ac = {}
ssh = {}
fs = {}


def logDungeonInfo(line: str, dungeon_info: dict):
    dungeon_location, dungeon_item = line.split(COLON_DELIMITER)
    dungeon_location = dungeon_location.strip()
    dungeon_item = dungeon_item.strip()

    if SMALL_KEY in dungeon_item:
        dungeon_item = SMALL_KEY
    elif BOSS_KEY in dungeon_item:
        dungeon_item = BOSS_KEY
    else:
        return
    
    if dungeon_location not in dungeon_info:
        dungeon_info[dungeon_location] = {
            SMALL_KEY: 0,
            BOSS_KEY: 0
        }

    dungeon_info[dungeon_location][dungeon_item] += 1


number_of_logs = len(os.listdir(LOGS_DIR))

for log_file in os.listdir(LOGS_DIR):
    with open(LOGS_DIR / log_file, "r", encoding="utf-8") as f:
        log_data = f.readlines()

    status_dict = {
        status: False
        for status in Log
    }

    playthrough_counter = 0

    for line in log_data:
        if line.startswith(NEW_LINE_DELIMITER):
            for status in Log:
                status_dict[status] = False

            playthrough_counter = 0
            continue

        if len(excluded_locations) == 0 and line.startswith(EXCLUDED_LOCATIONS):
            excluded_string = line.split(COLON_DELIMITER)[1].strip()
            excluded_string.strip("[]")

            excluded_list = [
                location.strip()
                for location in excluded_string.split(COMMA_DELIMITER)
            ]

            for location in excluded_list:
                if location[0] == SINGLE_QUOTE:
                    excluded_locations.append(location.strip(SINGLE_QUOTE))
                else:
                    excluded_locations.append(location.strip(DOUBLE_QUOTE))
        elif status_dict[Log.SOTS]:
            sots_location, sots_item = line.split(COLON_DELIMITER)
            sots_location = sots_location.strip()
            sots_item = sots_item.split(NUMBER_DELIMITER)[0].strip()

            if sots_location not in sots:
                sots[sots_location] = 1
            else:
                sots[sots_location] += 1
        elif status_dict[Log.BARREN]:
            barren_region = line.strip()

            if barren_region not in barren:
                barren[barren_region] = 1
            else:
                barren[barren_region] += 1
        elif status_dict[Log.NON_PROGRESS]:
            nonprogress_region = line.strip()

            if nonprogress_region not in nonprogress:
                nonprogress[nonprogress_region] = 1
            else:
                nonprogress[nonprogress_region] += 1
        elif status_dict[Log.PLAYTHROUGH]:
            if line.strip().startswith(DEFEAT_DEMISE):
                playthrough.append(playthrough_counter)
            elif line.startswith(SPACE):
                continue
            else:
                playthrough_counter += 1
        elif status_dict[Log.SV]:
            logDungeonInfo(line, sv)
        elif status_dict[Log.ET]:
            logDungeonInfo(line, et)
        elif status_dict[Log.LMF]:
            logDungeonInfo(line, lmf)
        elif status_dict[Log.AC]:
            logDungeonInfo(line, ac)
        elif status_dict[Log.SSH]:
            logDungeonInfo(line, ssh)
        elif status_dict[Log.FS]:
            logDungeonInfo(line, fs)
        
        for status in Log:
            if line.startswith(status.value):
                if status in (Log.SV, Log.ET, Log.LMF, Log.AC, Log.SSH, Log.FS):
                    for status_to_reset in Log:
                        status_dict[status_to_reset] = False

                status_dict[status] = True

# print("SotS Locations (where SotS items are found): ")

# for location in sots:
#     print("{:<80}".format(location + ":"), sots[location])

# print("\n\n")

print("Barren Regions (how many times each region was barren): ")

for region in barren:
    print("{:<24}".format(region + ":"), barren[region])

print("\n\n")

print("Non-progress Regions (how many times each region was non-progress): ")

for region in nonprogress:
    print("{:<24}".format(region + ":"), nonprogress[region])

print("\n\n")

print("Dungeon Items (where small keys and boss keys are found): ")

for dungeon in [sv, et, lmf, ac, ssh, fs]:
    for check in dungeon:
        print("{:<48}".format(check + ": ") + "Small Keys = " + str(dungeon[check][SMALL_KEY]) + "\t Boss Keys = " + str(dungeon[check][BOSS_KEY]))
    print()

print("\n\n")

print("Playthrough Lengths:")
playthrough.sort()
# print(playthrough)

total = 0

for number in playthrough:
    total += number

for number in range(1, playthrough[-1] + 1):
    print(str(number) + ": " + str(playthrough.count(number)))

print()
mean = round(total / len(playthrough), 3)
print("Mean Playthrough Length: " + str(mean))

print("\n\n")


# Get all enabled checks.
if not os.path.isfile(CHECKS_FILE):
    raise FileNotFoundError(CHECKS_FILE)

with open(CHECKS_FILE, "r", encoding="utf-8") as f:
    checks = yaml.safe_load(f)

all_enabled_checks = {}

for check in checks:
    if check in excluded_locations:
        continue

    all_enabled_checks[check] = 0

for location in sots:
    for check in all_enabled_checks:
        if location in check:
            all_enabled_checks[check] = sots[location]
            continue


# Calculate how many SotS items where found in each region.
regions = {}

for location in all_enabled_checks:
    # print("{:<80}".format(location + ":"), all_enabled_checks[location])

    region = location.split(HYPHEN_DELIMITER)[0].strip()

    if region not in regions:
        regions[region] = (all_enabled_checks[location], 1)
    else:
        regions[region] = (regions[region][0] + all_enabled_checks[location], regions[region][1] + 1)

print("\n\n")

# Print the number of SotS items per region and the % chance a SotS item is found in a given region.
for region in regions:
    number_of_sots = regions[region][0]
    checks_in_region = regions[region][1]
    print(
        "{:<24}".format(region + ":"),
        number_of_sots,
        "\t",
        str(round(number_of_sots / (checks_in_region * number_of_logs), 3)) + "%"
    )
