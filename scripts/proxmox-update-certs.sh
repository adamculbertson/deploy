#!/bin/bash
#BEGIN CONFIGURATION OPTIONS
#Set this to the user name that is holding the certificates. It should probably be an admin user
#It's recommended to use something other than the default 'root' account, though
USER_NAME="root"
#END CONFIGURATION OPTIONS

CERT_PATH="/home/$USER_NAME/.certs"
DEST_PATH="/etc/pve/nodes/proxmox"

CERT_NAME_SRC="$CERT_PATH/chain.crt"
KEY_NAME_SRC="$CERT_PATH/domain.key"

CERT_NAME_DEST="$DEST_PATH/pveproxy-ssl.pem"
KEY_NAME_DEST="$DEST_PATH/pveproxy-ssl.key"

mv "$CERT_NAME_SRC" "$CERT_NAME_DEST"
mv "$KEY_NAME_SRC" "$KEY_NAME_DEST"
rm "$CERT_PATH/*"

systemctl restart pveproxy
