# nagios-check-domain-es

> **Archived — no longer functional.** Kept for historical reference only.

A Nagios/Icinga plugin that checked the expiration date of Spanish **.es** domain
names. Originally written by Juan Pedro Escalona Rueda
(`jpescalona@otioti.com`) under the GPL; I picked it up in 2016 when the original
repo went dead.

## Why this is archived

The plugin worked by **scraping a third-party whois web page** for the
expiration date, because `.es` never offered a clean way to read it
programmatically. That approach has fully rotted, and as of 2026 there is **no
free, scriptable source for the expiration date of an arbitrary `.es` domain**:

- The `.es` registry (Red.es) does **not** provide RDAP — `.es` isn't in the
  IANA RDAP bootstrap, and there's no `rdap.nic.es`.
- The official port‑43 WHOIS (`whois.nic.es`) only answers from **IP addresses
  authorised by Red.es**; an unauthorised query gets a terms-of-use notice and
  no data.
- The web source this script scraped (`whoises.com`) is gone, and generic whois
  aggregators can't even read `.es` registration status (some wrongly report
  registered domains as "available").

The expiration date *is* published — but only through gated channels:
the captcha-protected portal at **https://www.dominios.es** ("Ver datos" →
*Fecha de Caducidad*) and authorised port‑43 access. Neither is usable from an
unattended monitoring plugin on an arbitrary host.

## If you need this today

- **For domains you own:** read the expiry from your **registrar's API** or via
  **EPP `<domain:info>` → `exDate`** — exact and automatable.
- **For third-party `.es` domains:** a paid WHOIS API with Red.es‑authorised
  backend is the only realistic option, and coverage varies per provider.

The original Python 2 script is left untouched in `check_domain_es.py`.
