#!/bin/bash
ARCHIVE_PATH="/usr/syno/etc/certificate/_archive/RrxGIW"
LOCAL_PATH="/var/services/homes/adama/.certs"
DSM_PATH="/usr/syno/etc/certificate/system"
WEBDAV_PATH="/usr/local/etc/certificate/WebDAVServer/webdav"

cp "$LOCAL_PATH/ca.crt" "$DSM_PATH/default/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$DSM_PATH/FQDN/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$ARCHIVE_PATH/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$WEBDAV_PATH/chain.pem"

cp "$LOCAL_PATH/domain.crt" "$DSM_PATH/default/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$DSM_PATH/FQDN/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$ARCHIVE_PATH/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$WEBDAV_PATH/cert.pem"

cp "$LOCAL_PATH/chain.crt" "$DSM_PATH/default/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$DSM_PATH/FQDN/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$ARCHIVE_PATH/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$WEBDAV_PATH/fullchain.pem"

cp "$LOCAL_PATH/domain.key" "$DSM_PATH/default/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$DSM_PATH/FQDN/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$ARCHIVE_PATH/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$WEBDAV_PATH/privkey.pem"

rm $DSM_PATH/{default,FQDN}/root.pem  $DSM_PATH/{default,FQDN}/short-chain.pem

/usr/syno/bin/synosystemctl restart nginx
/var/packages/WebDAVServer/scripts/start-stop-status stop && /var/packages/WebDAVServer/scripts/start-stop-status start
