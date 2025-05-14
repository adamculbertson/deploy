#!/bin/bash
# Base script for the "shell" deployment type
# Accepts required parameters of --cert-file, --key-file, --chain-file, and --ca-file

# Exit on error
set -e

# Define short and long options
OPTIONS=""
LONGOPTS="cert-file:,key-file:,chain-file:,ca-file:,help"

# Use getopt to parse options
PARSED=$(getopt --options="$OPTIONS" --longoptions="$LONGOPTS" --name "$0" -- "$@")
if [[ $? -ne 0 ]]; then
    exit 2
fi

# Evaluate the parsed options into positional parameters
eval set -- "$PARSED"

CERT_FILE=""
KEY_FILE=""
CHAIN_FILE=""
CA_FILE=""

# Process options
while true; do
    case "$1" in
        --cert-file)
            CERT_FILE="$2"
            shift 2
            ;;
        --key-file)
            KEY_FILE="$2"
            shift 2
            ;;
        --chain-file)
            CHAIN_FILE="$2"
            shift 2
            ;;
        --ca-file)
            CA_FILE="$2"
            shift 2
            ;;

        --help)
            echo "Usage: $0 --cert-file VALUE --key-file VALUE --chain-file VALUE --ca-file VALUE"
            exit 0
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Programming error"
            exit 3
            ;;
    esac
done

if [[ -z "$CERT_FILE" ]]; then
  echo "--cert-file was not provided"
  exit 1
fi

if [[ -z "$KEY_FILE" ]]; then
  echo "--key-file was not provided"
  exit 1
fi

if [[ -z "$CHAIN_FILE" ]]; then
  echo "--chain-file was not provided"
  exit 1
fi

if [[ -z "$CA_FILE" ]]; then
  echo "--ca-file was not provided"
  exit 1
fi

# Code here to make use of the passed parameters
