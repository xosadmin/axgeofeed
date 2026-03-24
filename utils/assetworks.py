import re

ASSET_COMPONENT_PATTERN = re.compile(r"^(AS\d+|AS-[A-Z0-9_-]+)$")

def sanitize_asset(asset):
    if not asset:
        return None
    asset = asset.strip().upper()
    if len(asset) > 100: # Reject too long
        return None
    if re.search(r"\s", asset): # Reject whitespace
        return None
    parts = asset.split(":")
    if len(parts) == 0: # Invalid AS-SET Combination
        return None
    for part in parts:
        if part == "": # If any of part that is empty
            return None
        if not ASSET_COMPONENT_PATTERN.fullmatch(part): # If any part that is not fully match the regex
            return None
    return asset