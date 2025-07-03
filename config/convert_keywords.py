import json
import os

# Path to the keywords.json file (assumes script is in the same directory as keywords.json)
KEYWORDS_FILE = os.path.join(os.path.dirname(__file__), "keywords.json")

# --- Step 1: Load the old flat keywords.json ---
with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
    old_keywords = json.load(f)

# --- Step 2: Convert to new nested structure ---
# The new structure is: {category: {"exact": [list of exact matches], "contains": []}}
new_keywords = {}
for description, category in old_keywords.items():
    if category not in new_keywords:
        new_keywords[category] = {"exact": [], "contains": []}
    # Add the description to the 'exact' list for this category
    if description not in new_keywords[category]["exact"]:
        new_keywords[category]["exact"].append(description)

# --- Step 3: Overwrite keywords.json with the new structure ---
with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
    json.dump(new_keywords, f, indent=4, ensure_ascii=False)

# --- Comments ---
# 1. The script loads the old flat dictionary where each key is a description and each value is a category.
# 2. It creates a new dictionary where each key is a category, and the value is a dict with 'exact' and 'contains' lists.
# 3. All old descriptions are added to the 'exact' list for their category. The 'contains' list is left empty for manual editing later.
# 4. The script then overwrites the original keywords.json with the new nested structure.
# 5. You can run this script once to migrate your keywords file to the new format. 