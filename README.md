
# **QuickAZ** 

> QuickAZ, find (Maybe) attacks surfaces (Azure) 🚩🐍

![](static/Hello.jpeg)

```console
Usage: quickaz.py [OPTIONS] HOSTNAME

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    hostname      TEXT  [default: None] [required]                                                                                                                                                                                      │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --permutation-wordlist-path                           TEXT  Wordlist with common names to permute while brute force blobs and others services [default: wordlists/permutation.txt]                                                       │
│ --brute-blob                   --no-brute-blob              Enable brute force blobs [default: no-brute-blob]                                                                                                                            │
│ --brute-dev-blob               --no-brute-dev-blob          Enable brute force dev.azure.com/[org-id] [default: no-brute-dev-blob]                                                                                                       │
│ --paths-wordlist-path                                 TEXT  Wordlist with common paths to discover open containers [default: wordlists/paths.txt]                                                                                        │
│ --regions-wordlist-path                               TEXT  Wordlist with common regions to discover cloudpass [default: wordlists/regions.txt]                                                                                          │
│ --verbose                      --no-verbose                 [default: no-verbose]                                                                                                                                                        │
│ --emails                                              TEXT  Wordlist with emails to enumerate [default: None]                                                                                                                            │
│ --output                                              TEXT  Output folder [default: output]                                                                                                                                              │
│ --enum-mails                   --no-enum-mails              Enable enumerate emails from wordlist provided or from email generator [default: no-enum-mails]                                                                              │
│ --gen-emails                                          TEXT  Email pattern to generate emails based on schemas: foo.bar@example.com or fbar@example.com                                                                                   │
│ --first-names                                         TEXT  Wordlist with firstnames to generate with gen_emails flag [default: wordlists/names/brazil_firstnames.txt]                                                                   │
│ --last-names                                          TEXT  Wordlist with surname to generate with gen_emails flag [default: wordlists/names/brazil_secondname.txt]                                                                      │
│ --threads                                             TEXT  Threads while enumerate emails > 2 maybe you get false positives [default: 2]                                                                                                │
│ --enumall                      --no-enumall                 Enumerate web,queue,files and others [default: no-enumall]                                                                                                                   │
│ --proxy                                               TEXT  Proxy to use                                                                                                                                                                 │
│ --socks-proxy                                         TEXT  Socks proxy to use                                                                                                                                                           │
│ --tor                          --no-tor                     Use tor proxy [default: no-tor]                                                                                                                                              │
│ --install-completion                                        Install completion for the current shell.                                                                                                                                    │
│ --show-completion                                           Show completion for the current shell, to copy it or customize the installation.                                                                                             │
│ --help                                                      Show this message and exit.                                                                                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

##### TODO List :)

[https://github.com/rodnt/quickaz/blob/main/TODO.md](https://github.com/rodnt/quickaz/blob/main/TODO.md)

#### Features
- [x] Enumerate tenant
- [x] Enumerate users from a given hostname
- [x] Realm finder
- [x] Proxy Support
- [x] OpenID
- [x] Container finder
- [x] Storage finder
- [x] Find Tenant names
- [x] Find dev.azure.com/ORG names
- [x] Find OneDrive Urls 
- [x] Finding open queue,dfs,files,web
- [x] Enumerate mail users o365
  - [x] Given wordlist
  - [x] Schema generator

##### Usage

-  Brute force blobs
     - `python3 quickaz.py example.com --brute-blob`
- Enumerate emails at office 365 with list of know emails
  - `python3 quickaz.py example.com --enum-mails --emails <mails.txt> --output example`
- Brute Force all services
  - `python3 quickaz.py example --enumall --brute-blob --output example`
- Usage with proxy
  - `python3 quickaz.py example.com --enumall --output example --proxy 127.0.0.1:808`
- Help menu
  - `python3 quickaz.py --help`

##### Install

```bash

python3 -m pip install -r requirements.txt --user
```

##### Useful google dorks
```

GitHub:
  "#EXT#" AND onmicrosoft.com AND <target> lang:Shell OR lang:PowerShell 
  "https://" AND "blob.core.windows.net/newcontainer" AND sig
```

```console
<company-name>.blob.core.windows.net
<company-name>cloud.blob.core.windows.net
<company-name>images.blob.core.windows.net
<company-name>backup.blob.core.windows.net
<company-name>backups.blob.core.windows.net
<company-name>storage.blob.core.windows.net
<company-name>cdn.blob.core.windows.net
<company-name>assets.blob.core.windows.net
<company-name>files.blob.core.windows.net
<company-name>resources.blob.core.windows.net
<company-name>documents.blob.core.windows.net
<company-name>development.blob.core.windows.net
<company-name>production.blob.core.windows.net
<company-name>qa.blob.core.windows.net
<company-name>prod.blob.core.windows.net
<company-name>dev.blob.core.windows.net
<company-name>stage.blob.core.windows.net
<company-name>staging.blob.core.windows.net
<company-name>web.blob.core.windows.net
<company-name>website.blob.core.windows.net
<company-name>test.blob.core.windows.net
```
