import json
import os
import traceback
import requests
import random
import subprocess
import sys

# tags_file = "tags_flat.json"
tags_file = "errors.json"
tags_file = "errors1.json"
# tags_file = "tags_left.json"
progress_file = "progress_errors1.json"
res_folder = "res"

# read progress file
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        progress = json.load(f)
else:
    progress = {}

# read images
with open(tags_file, "r") as f:
    tags = json.load(f)


def log(message: str):
    message = "[GRYPE] " + message
    print(message, flush=True)
    bot_token = ""
    bot_chatID = ""
    url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"
    r = requests.get(url, params={"chat_id": bot_chatID, "parse_mode": "html", "text": message})


counter = 0
for tag in tags:
    try:
        key = tag.replace(":", "_").replace("/", "_")
        if progress.get(key):
            print(f"{tag} already processed")
        elif "windows" in key:
            log(f"{tag} NO WINDOWS")
            progress[key] = {"done": False, "tag": tag}
        else:
            log(f"Scanning {tag}")
            filename = f"{res_folder}/{key}.json"
            process = subprocess.run(
                f"grype {tag} -o json > {filename}",
                shell=True,
                # text=True,
                # capture_output=True,
            )
            # if "TOOMANYREQUESTS" in process.stderr:
            #     log("TOOMANYREQUESTS")
            #     sys.exit()
            progress[key] = {"tag": tag, "returncode": process.returncode, "stderr": process.stderr, "stdout": process.stdout}
            if process.returncode == 0:
                progress[key]["done"] = True
                progress[key]["result_path"] = filename
            else:
                progress[key]["done"] = False

            with open(progress_file, "w") as f:
                json.dump(progress, f, indent=4, ensure_ascii=False)

            process = subprocess.run(
                f"docker system prune -a -f",
                shell=True,
                # text=True,
                # capture_output=True,
            )
            log(f"Scanned {tag}, {progress[key]['returncode']} \nProcessed {counter} / {len(tags)}")
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
    except:
        log("Exception" + traceback.format_exc())
    counter += 1




log("ALL DONE!!!")
