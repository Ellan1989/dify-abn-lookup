# Privacy Policy — ABN Lookup Dify Plugin

Last updated: 2026-10-20

This plugin ("ABN Lookup") is a tool plugin for the Dify platform. It calls the
official Australian Business Register (ABR) ABN Lookup API on behalf of the
Dify user who invokes it.

## What the plugin collects

Nothing. The plugin itself does not collect, store, log, or share any personal
data. It has no analytics, no telemetry, and no third-party services besides
the ABR API described below.

## What the plugin transmits, and where

- **Tool input you provide** (an ABN or ACN number) is sent to the official
  ABR endpoint `https://api.abn.business.gov.au` to perform the lookup, and
  the API response is returned to your Dify app.
- **Your ABN Lookup API key** is stored by Dify as plugin credentials and sent
  to the ABR API as the `x-vr-key` request header. It is never sent anywhere
  else and never included in tool output.
- The `ACN to ABN Converter` tool performs local computation only and makes no
  network request at all.

## Third-party service

Requests are made to the Australian Business Register (ABR), operated by the
Australian Government. Their own privacy terms apply to that service:
<https://api.abn.business.gov.au>

## Contact

For any questions about this plugin, open an issue at
<https://github.com/Ellan1989/dify-abn-lookup>.
