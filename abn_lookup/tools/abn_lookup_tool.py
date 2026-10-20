"""ABN / ACN lookup tool backed by the official ABR ABN Lookup API."""

from collections.abc import Generator
from datetime import date, datetime

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

_API_BASE = "https://api.abn.business.gov.au"
_SEARCH_BY_ABN = f"{_API_BASE}/abr-abn-check/AbnValidationService.asmx/SearchByABN"

_ABN_WEIGHTS = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
_ACN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 1]


def _digits(value: str) -> str:
    return "".join(c for c in value if c.isdigit())


def is_valid_abn(abn: str) -> bool:
    if len(abn) != 11 or not abn.isdigit():
        return False
    total = sum(w * (int(d) - (1 if i == 0 else 0)) for i, (w, d) in enumerate(zip(_ABN_WEIGHTS, abn)))
    return total % 89 == 0


def is_valid_acn(acn: str) -> bool:
    if len(acn) != 9 or not acn.isdigit():
        return False
    total = sum(w * int(d) for w, d in zip(_ACN_WEIGHTS, acn[:8]))
    return (10 - total % 10) % 10 == int(acn[8])


def abn_from_acn(acn: str) -> str | None:
    """Derive the ABN that embeds a given ACN (the last 9 digits of an ABN are its ACN)."""
    if not is_valid_acn(acn):
        return None
    for prefix in range(100):
        candidate = f"{prefix:02d}{acn}"
        if is_valid_abn(candidate):
            return candidate
    return None


def _format_date(value) -> str | None:
    if not value:
        return None
    if isinstance(value, dict):
        value = value.get("value") or value.get("date") or value.get("effectiveFrom")
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value[: len(fmt) + 2], fmt).date().isoformat()
            except ValueError:
                continue
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value) if value else None


def _pick_entity_name(payload: dict) -> tuple[str | None, list[str]]:
    """Return (main name, other business names) from an ABR SearchByABN response."""
    names: list[str] = []
    main_name = payload.get("mainName") or {}
    org_name = main_name.get("organisationName")
    legal_name = payload.get("legalName") or {}
    given = legal_name.get("givenName", "")
    middle = legal_name.get("otherGivenName", "")
    family = legal_name.get("familyName", "")
    if org_name:
        primary = org_name
    elif given or family:
        primary = " ".join(x for x in (given, middle, family) if x)
    else:
        primary = None
    for n in payload.get("businessName") or []:
        if n.get("organisationName"):
            names.append(n["organisationName"])
    for n in payload.get("mainTradingName") or []:
        if n.get("organisationName"):
            names.append(n["organisationName"])
    return primary, names


class ABNLookupTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        api_key = (self.runtime.credentials.get("abn_api_key") or "").strip()
        if not api_key:
            yield self.create_text_message("ABN Lookup API key is missing. Please configure the plugin credentials first.")
            return

        raw = _digits(str(tool_parameters.get("abn_or_acn") or ""))
        include_history = bool(tool_parameters.get("include_history", False))

        if is_valid_abn(raw):
            abn = raw
        elif is_valid_acn(raw):
            abn = abn_from_acn(raw)
            if not abn:
                yield self.create_text_message(f"'{raw}' is a well-formed ACN but no matching ABN could be derived.")
                return
        else:
            yield self.create_text_message(
                f"'{raw}' is not a valid ABN (11 digits) or ACN (9 digits). Checksum validation failed."
            )
            return

        try:
            resp = httpx.get(
                _SEARCH_BY_ABN,
                params={
                    "v3": "true",
                    "searchString": abn,
                    "includeHistoricalDetails": "Y" if include_history else "N",
                },
                headers={"x-vr-key": api_key, "accept": "application/json"},
                timeout=30,
            )
        except httpx.HTTPError as e:
            yield self.create_text_message(f"Failed to reach the ABN Lookup API: {e}")
            return

        if resp.status_code in (401, 403):
            yield self.create_text_message("The ABN Lookup API rejected the configured API key.")
            return
        if resp.status_code == 429:
            yield self.create_text_message("ABN Lookup API rate limit reached. Please retry later.")
            return
        if resp.status_code != 200:
            yield self.create_text_message(f"ABN Lookup API returned HTTP {resp.status_code}: {resp.text[:300]}")
            return

        payload = resp.json()
        exception = payload.get("exception") if isinstance(payload, dict) else None
        if exception:
            desc = exception.get("exceptionDescription") if isinstance(exception, dict) else str(exception)
            yield self.create_text_message(f"ABN Lookup API error: {desc}")
            return

        if not isinstance(payload, dict) or not payload:
            yield self.create_text_message(f"No record found for ABN {abn}.")
            return

        entity_name, other_names = _pick_entity_name(payload)
        abn_block = payload.get("abn") or {}
        abn_value = abn_block.get("identifierValue") or abn
        abn_status = abn_block.get("isCurrent")
        entity_status = payload.get("entityStatusCode")
        entity_type = (payload.get("entityType") or {}).get("entityTypeDescription")

        gst = payload.get("goodsAndServicesTax") or {}
        gst_from = _format_date(gst.get("effectiveFrom"))
        gst_registered = gst_from is not None if gst else False

        acn_value = None
        for ref in payload.get("entityRef") or []:
            if isinstance(ref, dict) and ref.get("entityRefTypeCode") == "ACN":
                acn_value = ref.get("entityRefValue")

        result = {
            "abn": abn_value,
            "acn": acn_value,
            "entity_name": entity_name,
            "other_business_names": other_names,
            "status": entity_status or ("Active" if abn_status else None),
            "entity_type": entity_type,
            "gst_registered": gst_registered,
            "gst_effective_from": gst_from,
            "address_state": payload.get("addressState"),
            "address_postcode": payload.get("addressPostcode"),
        }
        if include_history:
            result["entity_history"] = payload.get("entityHistory") or []

        yield self.create_json_message(result)

        lines = [f"ABN {result['abn']}: {entity_name or '(no name returned)'}"]
        if result["acn"]:
            lines.append(f"ACN: {result['acn']}")
        if result["status"]:
            lines.append(f"Status: {result['status']}")
        if result["entity_type"]:
            lines.append(f"Entity type: {result['entity_type']}")
        lines.append(f"GST registered: {'Yes' if result['gst_registered'] else 'No'}")
        if other_names:
            lines.append(f"Business name(s): {', '.join(other_names)}")
        location = ", ".join(x for x in (payload.get("addressState"), payload.get("addressPostcode")) if x)
        if location:
            lines.append(f"Location: {location}")
        yield self.create_text_message("\n".join(lines))
