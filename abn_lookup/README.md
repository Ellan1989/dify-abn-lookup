# ABN Lookup

A [Dify](https://dify.ai) tool plugin that looks up Australian business details from the **Australian Business Register (ABR)** using the official **ABN Lookup API**, plus a local ACN-to-ABN converter.

## Tools

### 1. ABN Lookup

Look up an Australian business by **ABN (11 digits)** or **ACN (9 digits)** and return:

- Registered entity name (company name, or legal name for individuals/sole traders)
- Business names registered under the ABN
- Entity status (Active / Cancelled)
- Entity type (e.g. *Australian Public Company*, *Sole Trader*)
- GST registration and its effective date
- Registered address state and postcode
- Optional: entity history (previous names, status changes)

If you pass a 9-digit ACN, the plugin derives the matching ABN locally (the last 9 digits of an ABN embed the ACN) and queries it.

### 2. ACN to ABN Converter

Converts a 9-digit ACN to its equivalent 11-digit ABN and validates the checksum of both numbers. Pure local computation — no API call, no credentials used.

## Credentials

The `ABN Lookup` tool requires an **ABN Lookup API key**:

1. Register at the ABR developer portal: <https://api.abn.business.gov.au>
2. Subscribe to the free **ABN Lookup Keys** product and create a key.
3. In Dify, open **Tools → ABN Lookup → Authorize**, and paste the key into the `ABN Lookup API key` field.

The key is sent as the `x-vr-key` request header on every API call. The `ACN to ABN Converter` tool works without any credential.

## Usage

1. Install the plugin from the Dify Marketplace (or install the `.difypkg` package via *Install from local file*).
2. Authorize it with your ABN Lookup API key.
3. Add either tool to an Agent or Workflow node, e.g. pass `51824753556` to get the entity details of that ABN.

## Data & privacy

See [PRIVACY.md](PRIVACY.md). In short: the plugin only forwards the ABN/ACN you pass to the official ABR endpoint and returns the result; nothing is stored or sent anywhere else.

## Source

<https://github.com/Ellan1989/dify-abn-lookup>

## License

Apache-2.0
