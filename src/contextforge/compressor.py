"""Ham JSON sonuçlarını özetler."""
import json
from typing import Any, Tuple


class ResultCompressor:
    def compress(self, tool_name: str, raw_result: Any) -> Tuple[str, float]:
        raw_text = json.dumps(raw_result) if not isinstance(raw_result, str) else raw_result
        original_tokens = len(raw_text) // 4

        if isinstance(raw_result, list):
            summary = self._compress_list(tool_name, raw_result)
        elif isinstance(raw_result, dict):
            summary = self._compress_dict(tool_name, raw_result)
        else:
            summary = str(raw_result)[:600]

        compressed_tokens = len(summary) // 4
        ratio = original_tokens / max(compressed_tokens, 1)

        return summary, ratio

    def _compress_list(self, tool_name: str, data: list) -> str:
        count = len(data)
        if count == 0:
            return f"{tool_name}: No results."
        samples = []
        for item in data[:3]:
            if isinstance(item, dict):
                pairs = [f"{k}={str(v)[:40]}" for k, v in list(item.items())[:3]]
                samples.append("{" + ", ".join(pairs) + "}")
            else:
                samples.append(str(item)[:80])
        return f"{tool_name}: {count} items. Samples: {' | '.join(samples)}{' ...' if count > 3 else ''}"

    def _compress_dict(self, tool_name: str, data: dict) -> str:
        keys = list(data.keys())
        status = data.get("status", data.get("success", "OK"))
        list_keys = [k for k, v in data.items() if isinstance(v, list)]
        if list_keys:
            list_summary = ", ".join(f"{k}({len(data[k])} items)" for k in list_keys[:2])
            return f"{tool_name}: status={status}, lists=[{list_summary}], keys={keys[:5]}"
        return f"{tool_name}: status={status}, keys=[{', '.join(keys[:5])}{'...' if len(keys)>5 else ''}]"
