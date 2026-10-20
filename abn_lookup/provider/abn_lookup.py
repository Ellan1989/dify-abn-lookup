import httpx
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

# A well-known public ABN (Commonwealth Bank of Australia) used only to
# verify that the supplied API key is accepted by the ABN Lookup API.
_PROBE_ABN = "51824753556"

_API_BASE = "https://api.abn.business.gov.au"
_SEARCH_BY_ABN = f"{_API_BASE}/abr-abn-check/AbnValidationService.asmx/SearchByABN"


class ABNLookupProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        api_key = (credentials.get("abn_api_key") or "").strip()
        if not api_key:
            raise ToolProviderCredentialValidationError("ABN Lookup API key is required.")
        try:
            resp = httpx.get(
                _SEARCH_BY_ABN,
                params={"v3": "true", "searchString": _PROBE_ABN, "includeHistoricalDetails": "N"},
                headers={"x-vr-key": api_key, "accept": "application/json"},
                timeout=15,
            )
        except httpx.HTTPError as e:
            raise ToolProviderCredentialValidationError(f"Failed to reach the ABN Lookup API: {e}") from e
        if resp.status_code in (401, 403):
            raise ToolProviderCredentialValidationError(
                "The ABN Lookup API rejected the key. Please check that the key is active."
            )
        if resp.status_code == 429:
            return
        if resp.status_code != 200:
            raise ToolProviderCredentialValidationError(
                f"Unexpected response from the ABN Lookup API (HTTP {resp.status_code})."
            )
