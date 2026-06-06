import json
import os
import re
from datetime import datetime
from helpers.tool import Tool, Response


class IntelligenceExtractorTool(Tool):
    """
    Intelligence Extractor Tool - Parse Grok x_search JSON responses and
    extract confirmed binary findings, mapping them to the SSOT file.
    Tracks structural properties: word length, initials, vowels, consonants,
    numbers, categories, and any confirmed/rejected passphrase properties.
    """

    SSOT_PATH = "/a0/usr/projects/hackina0/usr/knowledge/hackinga0_grok_chat_analysis.md"

    # Known structural properties to track
    BINARY_PROPERTIES = [
        "word_count",         # number of words in passphrase
        "char_count",         # total characters
        "word1_length",       # first word length
        "word2_length",       # second word length
        "word1_initial",      # first letter of word 1
        "word2_initial",      # first letter of word 2
        "has_numbers",        # contains digits
        "has_special_chars",  # contains special characters
        "language",           # english, italian, etc.
        "category",           # noun, verb, adjective, etc.
        "starts_with_vowel",  # word starts with vowel
        "contains_vowels",    # specific vowel pattern
    ]

    def _read_ssot(self):
        """Read current SSOT content."""
        try:
            with open(self.SSOT_PATH, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "# SSOT not found - initialize first"

    def _parse_grok_response(self, grok_json):
        """Extract intelligence from Grok x_search JSON response."""
        findings = {
            "confirmed": [],
            "rejected": [],
            "hints": [],
            "raw_mentions": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Parse the content field for @hackingA0 responses
        content = grok_json.get("content", "")
        if not content:
            return findings

        # Pattern: look for confirmed/rejected properties in response
        # The target @hackingA0 often responds with patterns like:
        # "0/10 for all" -> all guesses rejected
        # "Still sealed" -> no progress
        # Partial confirmations may have different patterns

        # Extract structural clues from content
        content_lower = content.lower()

        # Detect rejection patterns
        rejection_patterns = [
            r"0/10",
            r"still sealed",
            r"vault sealed",
            r"nice try",
            r"nope",
            r"wrong",
            r"incorrect",
            r"not even close",
        ]

        for pattern in rejection_patterns:
            if re.search(pattern, content_lower):
                findings["rejected"].append({
                    "type": "response_pattern",
                    "pattern": pattern,
                    "context": content[:200],
                })

        # Detect confirmation patterns
        confirmation_patterns = [
            r"closer",
            r"warmer",
            r"almost",
            r"partial",
            r"one word correct",
            r"half right",
        ]

        for pattern in confirmation_patterns:
            if re.search(pattern, content_lower):
                findings["confirmed"].append({
                    "type": "response_pattern",
                    "pattern": pattern,
                    "context": content[:200],
                })

        # Extract any explicit property mentions
        # e.g., "two words", "5 letters", "starts with A"
        word_count_match = re.search(r"(\d+)\s*words?", content_lower)
        if word_count_match:
            findings["hints"].append({
                "property": "word_count",
                "value": int(word_count_match.group(1)),
                "source": "content_analysis",
            })

        length_match = re.search(r"(\d+)\s*letters?", content_lower)
        if length_match:
            findings["hints"].append({
                "property": "letter_count",
                "value": int(length_match.group(1)),
                "source": "content_analysis",
            })

        initial_match = re.search(r"starts?\s*with\s*['"]?([a-z])", content_lower)
        if initial_match:
            findings["hints"].append({
                "property": "initial_letter",
                "value": initial_match.group(1).upper(),
                "source": "content_analysis",
            })

        # Extract tweet URLs for further analysis
        url_pattern = r"https?://(?:www\.)?(?:x|twitter)\.com/\w+/status/(\d+)"
        urls = re.findall(url_pattern, content)
        for tweet_id in urls:
            findings["raw_mentions"].append({
                "type": "tweet_reference",
                "tweet_id": tweet_id,
            })

        # Also parse citations for additional data
        citations = grok_json.get("citations", [])
        for cit in citations:
            cit_text = cit.get("text", "")
            if cit_text:
                findings["raw_mentions"].append({
                    "type": "citation",
                    "text": cit_text[:300],
                    "author": cit.get("author", ""),
                    "date": cit.get("date", ""),
                })

        return findings

    def _format_findings_for_ssot(self, findings):
        """Format findings as SSOT-ready markdown section."""
        lines = []
        lines.append(f"### Intelligence Extract - {findings['timestamp']}")
        lines.append("")

        if findings["confirmed"]:
            lines.append("**✅ Confirmed:**")
            for c in findings["confirmed"]:
                lines.append(f"- [{c['type']}] {c['pattern']}")
            lines.append("")

        if findings["rejected"]:
            lines.append("**❌ Rejected:**")
            for r in findings["rejected"]:
                lines.append(f"- [{r['type']}] {r['pattern']}")
            lines.append("")

        if findings["hints"]:
            lines.append("**💡 Hints:**")
            for h in findings["hints"]:
                lines.append(f"- {h['property']}: **{h['value']}** (source: {h['source']})")
            lines.append("")

        if findings["raw_mentions"]:
            lines.append(f"**📎 Raw Mentions:** {len(findings['raw_mentions'])} items")
            lines.append("")

        return "\n".join(lines)

    async def execute(self, **kwargs):
        mode = kwargs.get("mode", "extract")  # extract | status | map_property
        grok_json_str = kwargs.get("grok_json", "")
        property_name = kwargs.get("property", "")
        property_value = kwargs.get("value", "")
        property_status = kwargs.get("status", "confirmed")  # confirmed | rejected | uncertain

        if mode == "status":
            # Return current SSOT content summary
            ssot_content = self._read_ssot()
            return Response(
                message=f"SSOT Path: {self.SSOT_PATH}\n\nContent preview:\n{ssot_content[:2000]}",
                break_loop=False,
            )

        elif mode == "map_property":
            # Manually map a confirmed/rejected property to SSOT
            if not property_name or not property_value:
                return Response(
                    message="ERROR: 'property' and 'value' required for map_property mode.",
                    break_loop=False,
                )

            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            status_icon = "✅" if property_status == "confirmed" else ("❌" if property_status == "rejected" else "❓")
            entry = f"\n| {timestamp} | {property_name} | {property_value} | {status_icon} {property_status} | Mapped via Intelligence Extractor |"

            try:
                with open(self.SSOT_PATH, "a") as f:
                    f.write(entry)
                result = {
                    "status": "mapped",
                    "property": property_name,
                    "value": property_value,
                    "confirmation": property_status,
                    "ssot_updated": True,
                }
                return Response(
                    message=json.dumps(result, indent=2),
                    break_loop=False,
                )
            except Exception as e:
                return Response(
                    message=f"ERROR: Failed to update SSOT: {str(e)}",
                    break_loop=False,
                )

        elif mode == "extract":
            # Parse a Grok JSON response and extract intelligence
            if not grok_json_str:
                return Response(
                    message="ERROR: 'grok_json' required for extract mode. Pass the Grok response JSON.",
                    break_loop=False,
                )

            try:
                if isinstance(grok_json_str, str):
                    grok_json = json.loads(grok_json_str)
                else:
                    grok_json = grok_json_str
            except json.JSONDecodeError as e:
                return Response(
                    message=f"ERROR: Invalid JSON: {str(e)}",
                    break_loop=False,
                )

            findings = self._parse_grok_response(grok_json)
            ssot_update = self._format_findings_for_ssot(findings)

            # Auto-append to SSOT
            try:
                with open(self.SSOT_PATH, "a") as f:
                    f.write("\n\n" + ssot_update)
                findings["ssot_updated"] = True
            except Exception as e:
                findings["ssot_update_error"] = str(e)

            return Response(
                message=json.dumps(findings, indent=2, ensure_ascii=False),
                break_loop=False,
            )

        else:
            return Response(
                message=f"ERROR: Unknown mode '{mode}'. Use: extract, status, map_property.",
                break_loop=False,
            )
