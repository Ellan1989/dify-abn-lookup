# Plugin Submission

## Plugin information

- **Author**: ellan1989
- **Plugin name**: abn_lookup
- **Version**: 0.0.1
- **Source repository**: https://github.com/Ellan1989/dify-abn-lookup
- **Contact**: Ellan1989@users.noreply.github.com

## Submission type

- [x] New plugin
- [ ] Version update

## What changed

New tool plugin that looks up Australian business details using the official
Australian Business Register (ABR) ABN Lookup API:

- `abn_lookup` tool — query an Australian business by ABN (11 digits) or ACN
  (9 digits); returns the registered entity name, business names, entity
  status, entity type, GST registration, and registered-address state/postcode.
  ACN input is converted to the matching ABN locally before querying.
- `acn_to_abn` tool — local (no network) ACN → ABN conversion with ABN/ACN
  checksum validation.

Requires a free ABN Lookup API key from the ABR developer portal
(https://api.abn.business.gov.au), configured as the `abn_api_key` credential.

## Risk level

- [x] Low risk
- [ ] Medium risk
- [ ] High risk

The plugin makes read-only GET requests to a single government API domain
(declared in `manifest.yaml` `network.domains`), and runs one pure-local
computation tool. No file, shell, database, or arbitrary-URL capabilities.

## Required checks

- [x] I have read and followed the [Marketplace submission requirements](https://github.com/langgenius/dify-plugins/blob/main/docs/plugin-submission-requirements.md).
- [x] I have read and comply with the Plugin Developer Agreement.
- [x] I tested this plugin on Dify Community Edition and Dify Cloud, or documented any limitation below.
- [x] The package contains only files needed at runtime.
- [x] The package does not contain secrets, local credentials, `.env` files, `.git` directories, virtual environments, caches, logs, or IDE files.
- [x] The package does not contain executables or bundled binaries, or I explained why they are required below.
- [x] The plugin README includes setup steps, usage instructions, required APIs or credentials, connection requirements, and the source repository link.
- [x] The plugin includes `PRIVACY.md` or a hosted privacy policy, and `manifest.yaml` references it.
- [x] All user-facing text is primarily in English, with any localized README files following the [i18n guidance](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/multilingual-readme).

## Security and privacy notes

None. The plugin forwards only the user-provided ABN/ACN string to the
official ABR endpoint `https://api.abn.business.gov.au` (JSON GET, API key in
the `x-vr-key` header stored as a Dify secret credential). No data is stored,
logged, or sent anywhere else. See PRIVACY.md.

## Local validation

Ran the official local validator from langgenius/dify-marketplace-toolkit:

```
python validator/validate-difypkg.py ellan1989/abn_lookup/abn_lookup-0.0.1.difypkg --output-dir ./validation-report
```

Result: **0 blocking failures**; all blocking checks PASS
(package_contents, package_secrets, package_binaries, manifest_metadata,
readme_metadata, package_dependencies, python_compile). Remaining warnings
are informational (single declared outbound domain; 2 pinned dependencies).

Also verified locally: the plugin loads under dify-plugin 0.10.2 (both tools
register), and ABN/ACN checksum logic round-trips against real registered
companies (e.g. Woolworths Group ABN 88000014675 / ACN 000014675, BHP Group
ABN 49004028077 / ACN 004028077).

## Reviewer notes

- Resubmission of #3428, which was closed because the previous PR body accidentally
  contained two non-English header lines from a local template file. The package is
  unchanged; this body is pure English per the submission template (verified locally
  with check-pr-body.py from dify-marketplace-toolkit).

- The ABR endpoint was unreachable from my development network, so live API
  calls against production were verified from an Australian network; payload
  parsing follows the published SearchByABN v3 JSON shape with defensive
  `.get()` access throughout.
- `dify-plugin` and `httpx` are pinned to exact versions in both
  `requirements.txt` and `pyproject.toml` per validator guidance.
