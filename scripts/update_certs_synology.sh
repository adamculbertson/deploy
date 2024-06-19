#!/bin/bash
#BEGIN CONFIGURATION OPTIONS
#In the directory '/usr/syno/etc/certificate/_archive/' are one or more randomly-generated directories. Each directory contains a certificate set up in DSM. If you only have one certificate, then there will only be one directory.
#Set this to the name of the directory that contains the certificate you want to replace
CERT_NAME=""

#Set this to the user name that is holding the certificates. It should probably be an admin user
#It's recommended to use something other than the default 'admin' account, though
USER_NAME="admin"
#END CONFIGURATION OPTIONS

ARCHIVE_PATH="/usr/syno/etc/certificate/_archive/$CERT_NAME"
LOCAL_PATH="/var/services/homes/$USER_NAME/.certs"
DSM_PATH="/usr/syno/etc/certificate/system"

cp "$LOCAL_PATH/ca.crt" "$DSM_PATH/default/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$DSM_PATH/FQDN/chain.pem"
cp "$LOCAL_PATH/ca.crt" "$ARCHIVE_PATH/chain.pem"

cp "$LOCAL_PATH/domain.crt" "$DSM_PATH/default/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$DSM_PATH/FQDN/cert.pem"
cp "$LOCAL_PATH/domain.crt" "$ARCHIVE_PATH/cert.pem"

cp "$LOCAL_PATH/chain.crt" "$DSM_PATH/default/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$DSM_PATH/FQDN/fullchain.pem"
cp "$LOCAL_PATH/chain.crt" "$ARCHIVE_PATH/fullchain.pem"

cp "$LOCAL_PATH/domain.key" "$DSM_PATH/default/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$DSM_PATH/FQDN/privkey.pem"
cp "$LOCAL_PATH/domain.key" "$ARCHIVE_PATH/privkey.pem"

rm $DSM_PATH/{default,FQDN}/root.pem  $DSM_PATH/{default,FQDN}/short-chain.pem

/usr/syno/bin/synosystemctl restart nginx
