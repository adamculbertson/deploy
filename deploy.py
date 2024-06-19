#!/usr/bin/env python

import os
import sys
import shutil
import subprocess
import logging

import requests
import yaml

config_path = os.path.expanduser("~/.config/deploy.yml")
# If an ECC certificate is used, acme.sh will add _ecc to the end of the path
certs_path = os.path.expanduser("~/.acme.sh/%DOMAIN%%ECC%")

log_path = os.path.expanduser("~/.cache/deploy.log")

# Paths to each file in the certificates' directories
cert_file = os.path.join(certs_path, "%DOMAIN%.cer")
key_file = os.path.join(certs_path, "%DOMAIN%.key")
chain_file = os.path.join(certs_path, "fullchain.cer")
ca_file = os.path.join(certs_path, "ca.cer")

# TODO: Put these in the config file and have different destinations available per-domain
dest_cert_file = "domain.crt"
dest_key_file = "domain.key"
dest_chain_file = "chain.crt"
dest_ca_file = "ca.crt"

# IFTTT trigger path:
# https://maker.ifttt.com/trigger/{event}/with/key/{key}
# POST with data:
#  { "value1" : "", "value2" : "", "value3" : "" }

# Since I don't use IFTTT anymore, I have no idea if this has changed
# It's pretty simple to support, so I'll leave it in
ifttt_url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG, filename=log_path,
                    encoding="utf-8")


def get_cert_paths(domain, ecc=False):
    result = {
        "cert_file": cert_file.replace("%DOMAIN%", domain),
        "key_file": key_file.replace("%DOMAIN%", domain),
        "chain_file": chain_file.replace("%DOMAIN%", domain),
        "ca_file": ca_file.replace("%DOMAIN%", domain)
    }

    ecc_path = ""
    if ecc:
        ecc_path = "_ecc"

    result['cert_file'] = result['cert_file'].replace("%ECC%", ecc_path)
    result['key_file'] = result['key_file'].replace("%ECC%", ecc_path)
    result['chain_file'] = result['chain_file'].replace("%ECC%", ecc_path)
    result['ca_file'] = result['ca_file'].replace("%ECC%", ecc_path)

    return result


def type_local(target):
    ecc = False
    if "ecc" in target:
        ecc = target['ecc']

    cert_paths = get_cert_paths(domain, ecc)

    # Determine the destination paths for the cert files
    final_cert_path = os.path.join(target['destination'], dest_cert_file)
    final_key_path = os.path.join(target['destination'], dest_key_file)
    final_chain_path = os.path.join(target['destination'], dest_chain_file)
    
    try:
        shutil.copyfile(cert_paths['cert_file'], final_cert_path)
        shutil.copyfile(cert_paths['key_file'], final_key_path)
        shutil.copyfile(cert_paths['chain_file'], final_chain_path)
    except Exception as e:
        logging.error(f"Unable to copy certificate paths for target '{target['name']}': {e}")
        return False

    if "finished" in target:
        cmd = target['finished']

        try:
            result = subprocess.run(cmd, capture_output=True)
        except Exception as e:
            logging.error(f"Unable to execute '{cmd}' for target '{target['target']}': {e}")
            return False

        if result.returncode != 0:
            logging.error(f"Could not run '{cmd}' for target '{target['name']}'. Got return code: {result.returncode}")
            return False
            
        logging.info(f"{cmd} completed for {target['name']}")

    return True


def type_ssh(target):
    ecc = False
    if "ecc" in target:
        ecc = target['ecc']

    cert_paths = get_cert_paths(domain, ecc)
    
    dest_cert_path = os.path.join(target['destination'], dest_cert_file)
    dest_key_path = os.path.join(target['destination'], dest_key_file)
    dest_chain_path = os.path.join(target['destination'], dest_chain_file)
    dest_ca_path = os.path.join(target['destination'], dest_ca_file)

    if "config" in target:
        cmds = [["scp", cert_paths['cert_file'], f"{target['config']}:{dest_cert_path}"],
                ["scp", cert_paths['key_file'], f"{target['config']}:{dest_key_path}"],
                ["scp", cert_paths['chain_file'], f"{target['config']}:{dest_chain_path}"],
                ["scp", cert_paths['ca_file'], f"{target['config']}:{dest_ca_path}"]]
    else:
        logging.error(f"No 'config' specified for target {target['name']}")
        return False

    for params in cmds:
        cmd = params[0]
        try:
            result = subprocess.run(params, capture_output=True)
        except Exception as e:
            logging.error(f"Unable to execute '{cmd}' for target '{target['name']}': {e}")
            return False

        if result.returncode != 0:
            run = " ".join(params)
            logging.error(f"Could not run '{run}' for target '{target['name']}'. Got return code: {result.returncode}")
            return False

    if "finished" in target:
        cmd = ["ssh", target['config'], target['finished']]

        try:
            result = subprocess.run(cmd, capture_output=True)
        except Exception as e:
            logging.error(f"Unable to execute '{cmd}' for target '{target['name']}': {e}")
            return False

        if result.returncode != 0:
            logging.error(f"Could not run '{cmd}' for target '{target['name']}'. Got return code: {result.returncode}")
            return False

    return True

# For SSH, "config" specifies the host in the ssh config file to use. It should not require a password to access
#  The value %CERTS_PATH% is also replaced in the file with the value given for "destination"


if __name__ == "__main__":
    if not os.path.exists(config_path):
        sys.exit(1)

    with open(config_path, "rt") as f:
        config = yaml.safe_load(f)

    # Make sure the domain was specified
    try:
        domain = sys.argv[1]
    except IndexError:
        sys.stderr.write(f"Usage: {sys.argv[0]} domain\n")
        sys.exit(1)

    # Gather a list of domains from each target
    config['domains'] = []
    for target in config['targets']:
        if config['targets'][target][domain] not in config['domains']:
            config['domains'].append(config['targets'][target][domain])

    # Verify that the domain is in the list of domains
    found = False
    try:
        for i in range(len(config['domains'])):
            if config['domains'][i] == domain:
                found = True
                break
        if not found:
            logging.error(f"Domain '{domain}' was not found in the list of domains!")
            sys.exit(2)
    except KeyError:
        logging.error("Configuration is missing the list of domains!\n")
        sys.exit(3)

    results = {}
    # Find the targets that match the domain
    # Any invalid domain indexes will be automatically skipped
    # TODO: Maybe try and handle invalid indexes?
    for key in config['targets']:
        target = config['targets'][key]
        # Skip non-matching domains
        if target['domain'] != domain:
            continue

        target['name'] = key
        if target['type'] == "local":
            results[key] = type_local(target)
        elif target['type'] == "ssh":
            results[key] = type_ssh(target)
        else:
            logging.error(f"Invalid type '{target['type']}' for target '{key}'")
            sys.exit(4)

    # Determine if the deployment was successful
    # If either Home Assistant (ha) or IFTTT are enabled, then send the results to them
    success = True
    for key in results.keys():
        if not results[key]:
            success = False
            break

    if "ifttt" in config:
        # Determine the appropriate event URL to fire
        if success:
            url = ifttt_url.format(event=config['ifttt']['event_success'], key=config['ifttt']['key'])
        else:
            url = ifttt_url.format(event=config['ifttt']['event_fail'], key=config['ifttt']['key'])

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
        if success:
            title = f"{domain} Successfully Renewed"
            message = f"The certificate for {domain} was successfully renwed"
        else:
            title = f"{domain} Renewal Failure"
            message = f"The certificate for {domain} failed to renew"

        data = {
            "title": title,
            "message": message
        }

        url = f"{base_url}/{webhook}"
        r = requests.post(url, json=data)
        if r.status_code == 200:
            logging.info(f"Successfully sent HomeAssistant message: {message}")
            sys.exit(0)
        else:
            logging.error(f"Failed to send HomeAssistant message '{message}'. HA returned status code '{r.status_code}'")
            sys.exit(6)
