import json
import os
import traceback
import requests
import pandas as pd
import random
import subprocess
import sys

# tags_file = "tags_flat.json"
tags_file = "errors.json"
progress_file = "progress_errors.json"
res_folder = "res"
# clairctl = "docker scout cves --format sarif --output alpine.sarif.json stakater/reloader:SNAPSHOT-PR-586-UBI-0db6f802"

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
    print(message, flush=True)
    bot_token = ""
    bot_chatID = ""
    send_text = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + bot_chatID + "&parse_mode=Markdown&text=" + message
    requests.get(send_text)


counter = 0
for tag in tags:
    try:
        key = tag.replace(":", "_").replace("/", "_")
        if progress.get(key):
            print(f"{tag} already processed")
        elif "windows" in key:
            log(f"{tag} NO WINDOWS")
            progress[key] = {"done": False, "tag": tag, "reason": "windows"}
        else:
            log(f"SCOUT Scanning {tag}")
            process = subprocess.run(
                f"docker scout cves --format sarif --output res/{key}.json {tag}",
                shell=True,
                text=True,
                capture_output=True,
            )
            if "TOOMANYREQUESTS" in process.stdout:
                log("TOOMANYREQUESTS")
                sys.exit()
            progress[key] = {"tag": tag, "returncode": process.returncode, "stderr": process.stderr, "stdout": process.stdout}
            if process.returncode == 0:
                progress[key]["done"] = True
            else:
                progress[key]["done"] = False

            with open(progress_file, "w") as f:
                json.dump(progress, f, indent=4, ensure_ascii=False)

            log(f"SCOUT Scanned {tag}, {progress[key]} \nSCOUT Processed {counter} / {len(tags)}")
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
    except:
        log("Exception" + traceback.format_exc())
    counter += 1




log("ALL DONE!!!")
