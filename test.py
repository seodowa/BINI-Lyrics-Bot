import json

with open("lyrics\\Bini - B Hu u r.json", encoding="utf-8") as f:
    lyrics = json.load(f)

[print(line, end="") for line in lyrics]