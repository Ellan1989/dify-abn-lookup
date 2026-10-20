"""Local ACN -> ABN converter (no API call)."""

from collections.abc import Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.abn_lookup_tool import _digits, abn_from_acn, is_valid_abn, is_valid_acn


class ACNToABNTool(Tool):
    def _invoke(self, tool_parameters: dict) -> Generator[ToolInvokeMessage, None, None]:
        raw = _digits(str(tool_parameters.get("acn") or ""))
        if len(raw) == 11 and is_valid_abn(raw):
            yield self.create_text_message(f"'{raw}' is an ABN, not an ACN. Please pass a 9-digit ACN.")
            return
        if not is_valid_acn(raw):
            yield self.create_text_message(f"'{raw}' is not a valid ACN (9 digits with a correct checksum).")
            return

        abn = abn_from_acn(raw)
        result = {
            "acn": raw,
            "acn_valid": True,
            "abn": abn,
            "abn_valid": bool(abn and is_valid_abn(abn)),
        }
        yield self.create_json_message(result)
        yield self.create_text_message(f"ACN {raw} -> ABN {abn}")
