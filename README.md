# deploy
A Python script to deploy certificates renewed via [acme.sh](https://github.com/acmesh-official/acme.sh) to multiple servers.  

Note that this is my first public GitHub repo, so it is a work in progress.

## Setup
Unfortuantely, if you already have acme.sh set up to renew your certificates, you will have to set it up again, unless you feel like modifying its various configuration files (which this document will not be covering). Various configuration parameters will need to be tweaked based on your needs in the `deploy.yml` file.

Here is how my deployment works, using ECC certificates:
```bash
DOMAIN='your.domain.here'
acme.sh --issue --dns dns_cf -d "$DOMAIN" --keylength ec-384 --post-hook "/path/to/deploy.py "$DOMAIN"
```
The above example uses an already configured Cloudflare DNS challenge to issue an ec-384 certificate. For information on how to set up the DNS challenge, please see the `acme.sh` repository. There are two places where the domain needs to be specified in the command, be aware of that. The second place passes the domain to `deploy.py`. 

## Configuration
There is an example `deploy.yml` file in the `examples` directory, but configuring it for SSH access probably needs some explanation. The example in the configuration file uses a `config` value of "target1". For reference, here are the relevant options, but slightly condensed:
```yaml
targets:
  remote_target:
    type: ssh
    config: target1
    destination: /path/to/remote/certs
    domain: '*.example.com'
    ecc: true
```
The `config` parameter references the `Host` section in the user's `~/.ssh/config` file. A very basic example based on the above config can be found below:
```
Host target1
  HostName      your.ip.here
  User		      your.user.here
  IdentityFile 	/path/to/passwordless/private/key
```
It is **very** important that the private key not have a password on it, so make sure that it is stored in as secure of a location as possible.

## Certificate files
At the moment, there are some hard-coded file names that are sent to the remote host. The mapping of what `deploy.py` renames them to is shown below. `DOMAIN` is replaced by the actual domain name, whereas `domain` is the literal word:
* `DOMAIN.cer` -> `domain.crt`
* `DOMAIN.key` -> `domain.key`
* `fullchain.cer` -> `chain.crt`
* `ca.cer` -> `ca.crt`

## Synology DSM
Configuring `deploy.py` to work with DSM takes a bit of work. You will need to know the path to where the certificates are stored. You can find some information on [this guide](https://dokuwiki.bitaranto.ch/doku.php?id=synologyimportcertfrompfsense).

For my own deployment, I store the certificates in a `.certs` directory in my admin user's home directory. User's homes are located in `/var/services/homes`. For an admin user simply called `admin`, this would be in `/var/services/homes/admin`.

These certificates need to be copied to the appropriate locations. To do that, see the file `update_certs_synology.sh` in the `scripts` directory. This file will need to be modified with your admin user's name as well as the name of the directory your certs are stored in the `_archive` directory. See the linked guide for more information on that.

After the `update_certs_synology.sh` file is edited, it needs to be placed somewhere safe where it won't be modified by DSM when it updates. For my setup, it's in the `.certs` directory mentioned above, but `chown root:root` and `chmod 600` permissions set on it so that only `root` can access it.

Now we need to run the update script. In the `examples/sudoers` directory is a `synology_update_certs` file. Modify that file to point to the path where you placed the `update_certs_synology.sh` file. It is important that the path is correct, otherwise a password will be prompted upon certificate renewal. Place the `synology_update_certs` file in the `/etc/sudoers.d` directory of your NAS.

## Putting it all together.
This will be an example using a Synology NAS. We'll have the following setup. Note that `bob` is an Administrator of the NAS:
* User: `bob`
* Certs path: `/var/services/homes/bob/.certs`
* SSH host: nas
* Domain: *.example.com
* _archive path: `RyUtyt5`

First, we set up SSH access on the machine running `acme.sh`. It's assumed the key is already created:
`~/.ssh/config`:
```
Host nas
  HostName      192.168.1.9
  User		      bob
  IdentityFile 	~/.ssh/nas.key
```

Next, we create our deployment configuration (this is a snippet):
`~/.config/deploy.yml`:
```yaml
targets:
  remote_target:
    type: ssh
    config: nas
    destination: /var/services/homes/bob/.certs
    domain: '*.example.com'
    ecc: true
    finished: sudo /var/services/home/bob/.certs/update_certs.sh
```

The `update_certs_synology.sh` file is located in `/var/services/homes/bob/.certs/update_certs.sh` for this example.
Using the guide, we found that the location of the certs in this fake NAS is `RyUtyt5` (no idea if that is valid or not, but it does not matter for the example). We modify the top of `examples/scripts/update_certs_synology.sh` to have the following and save it to `/var/services/homes/bob/.certs/update_certs.sh`:
```bash
...
CERT_NAME="RyUtyt5"
USER_NAME="bob"
...
```
File permissions for the `update_certs.sh` file:
```
ls -l /var/services/homes/bob/.certs/update_certs.sh
-rw------- 1 root  root   954 Sep 23  2023 update_certs.sh
```
Now we add the script to the sudoers file:
`/etc/sudoers.d/synology_update_certs`:
```
%administrators ALL = (root) NOPASSWD: /var/services/homes/bob/.certs/update_certs.sh
```

Finally, we set up `acme.sh` to renew the certificate. It is assumed that Cloudflare DNS has already been set up. We want to issue a certificate for the wildcard domain `*.example.com`:
```bash
acme.sh --issue --dns dns_cf -d '*.example.com' --keylength ec-384 --post-hook "/home/bob/deploy/deploy.py '*.example.com'
```
The only thing not configured in this example is sending a notification. That can be handled with the Home Assistant webhook and is outside the scope of this document. Actually configuring `deploy.py` to call a webhook is quite simple and can be found in the `examples/deploy.yml` file. It's part of the `ha` section of the file.
