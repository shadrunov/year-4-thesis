
import json
import os
import traceback
import requests
import random
import subprocess
import sys

tags_file = "tags_flat.json"
# tags_file = "errors.json"
# progress_file = "progress_errors.json"
progress_file = "progress_last.json"
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
    message = "[GC] " + message
    print(message, flush=True)
    bot_token = ""
    bot_chatID = ""
    url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"
    # r = requests.get(url, params={"chat_id": bot_chatID, "parse_mode": "html", "text": message})


counter = 0
for tag in tags:
    try:
        key = tag.replace(":", "_").replace("/", "_")
        filename = f"{res_folder}/{key}.json"
        if os.path.exists(filename):
            progress[key] = {"tag": tag}
            progress[key]["done"] = True
            progress[key]["result_path"] = filename
        else:
            log(f"Scanning {tag}")
            # pull
            process = subprocess.run(
                f"docker pull europe-west1-docker.pkg.dev/proud-will-422321-e7/shadrunov/{tag}",
                shell=True,
                text=True,
                capture_output=True,
            )
            if "TOOMANYREQUESTS" in process.stderr:
                log("TOOMANYREQUESTS")
                sys.exit()

            process = subprocess.run(
                f"gcloud artifacts docker images describe europe-west1-docker.pkg.dev/proud-will-422321-e7/shadrunov/{tag} --show-package-vulnerability --format json > {filename}",
                shell=True,
                text=True,
                capture_output=True,
            )
            progress[key] = {"tag": tag}
            # if process.returncode == 0:
            progress[key]["done"] = True
            #     progress[key]["result_path"] = filename
            # else:
            #     progress[key]["done"] = False
            process = subprocess.run(
                f"docker image rm europe-west1-docker.pkg.dev/proud-will-422321-e7/shadrunov/{tag}",
                shell=True,
                text=True,
                capture_output=True,
            )

            log(f"Scanned {tag}, {progress[key]} \nProcessed {counter} / {len(tags)}")
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
    except:
        log("Exception" + traceback.format_exc())
    with open(progress_file, "w") as f:
        json.dump(progress, f, indent=4, ensure_ascii=False)
    counter += 1




log("ALL DONE!!!")
