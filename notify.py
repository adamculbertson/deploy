#!/usr/bin/env python
import os
import sys
import logging

import yaml
import requests

config_path = os.path.expanduser("~/.config/deploy/deploy.yml")
log_path = os.path.expanduser("~/.cache/deploy.log")

#IFTTT trigger path:
# https://maker.ifttt.com/trigger/{event}/with/key/{key}
#POST with data:
#  { "value1" : "", "value2" : "", "value3" : "" }

# Since I don't use IFTTT anymore, I have no idea if this has changed
# It's pretty simple to support, so I'll leave it in
# This script was also made before acme.sh added built-in notification options, such as IFTTT
ifttt_url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG, filename=log_path, encoding="utf-8")

if __name__ == "__main__":
    if not os.path.exists(config_path):
        sys.stderr.write(f"Config file not found at {config_path}\n")
        sys.exit(1)

    with open(config_path, "rt") as f:
        config = yaml.safe_load(f)

    if len(sys.argv) < 4:
        sys.stderr.write(f"Usage: {sys.argv[0]} subject message status\n")
        sys.exit(1)

    subject = sys.argv[1]
    message = sys.argv[2]
    status = sys.argv[3]

    if "ifttt" in config:
        #Determine the appropriate event URL to fire
        url = ifttt_url.format(event=config['ifttt']['event'], key=config['ifttt']['key'])

        domain_field = config['ifttt']['domain_field']
        data = {domain_field: domain}

        r = requests.post(url, json=data)
        if r.status_code == 200:
            if "Congratulations" in r.text:
                sys.exit(0)
            else:
                sys.exit(5)
        else:
            sys.exit(6)

    if "ha" in config:
        base_url = f"{config['ha']['url']}/api/webhook"
        webhook = config['ha']['webhook']

        message = f"Status: {status}\n{message}"

        data = {
            "title": subject,
            "message": message
        }

        url = "{base_url}/{webhook}"
        r = requests.post(url, json=data)
        if r.status_code == 200:
            logging.info(f"Successfully sent HomeAssistant message: {message}")
            sys.exit(0)
        else:
            logging.error(f"Failed to send HomeAssistant message '{message}'. HA returned status code '{r.status_code}'")
            sys.exit(6)
