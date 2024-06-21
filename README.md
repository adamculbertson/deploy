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

Take a look at the wiki for configuration options, notifications, and anything else.
