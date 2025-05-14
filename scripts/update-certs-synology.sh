#!/bin/bash
# Modify the following configuration options
ARCHIVE_NAME="" # Random string, you can check this name by looking at the directory in $ARCHIVE_PATH
LOCAL_PATH="/var/services/homes/root/.certs" # Path to where the certificates are located

# These paths should not need to be changed, unless a major DSM update causes them to change
ARCHIVE_PATH="/usr/syno/etc/certificate/_archive/$ARCHIVE_NAME"
DSM_PATH="/usr/syno/etc/certificate/system"
WEBDAV_PATH="/usr/local/etc/certificate/WebDAVServer/webdav"

# Update chain.pem
cp "$LOCAL_PATH/ca.crt" "$DSM_PATH/default/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$DSM_PATH/FQDN/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$ARCHIVE_PATH/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$WEBDAV_PATH/chain.pem"

# Update cert.pem
cp "$LOCAL_PATH/domain.crt" "$DSM_PATH/default/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$DSM_PATH/FQDN/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$ARCHIVE_PATH/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$WEBDAV_PATH/cert.pem"

# Update fullchain.pem
cp "$LOCAL_PATH/chain.crt" "$DSM_PATH/default/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$DSM_PATH/FQDN/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$ARCHIVE_PATH/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$WEBDAV_PATH/fullchain.pem"

# Update privkey.pem
cp "$LOCAL_PATH/domain.key" "$DSM_PATH/default/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$DSM_PATH/FQDN/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$ARCHIVE_PATH/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$WEBDAV_PATH/privkey.pem"

# Remove default certiciates
rm $DSM_PATH/{default,FQDN}/root.pem  $DSM_PATH/{default,FQDN}/short-chain.pem

# Restart services to make use of the new certificates
/usr/syno/bin/synosystemctl restart nginx
/var/packages/WebDAVServer/scripts/start-stop-status stop && /var/packages/WebDAVServer/scripts/start-stop-status start