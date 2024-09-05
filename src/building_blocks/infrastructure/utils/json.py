import json


# tutaj nie zmieniać uprawnień, zrobi się jakieś fixtures żeby generowało jsony jako komendę CLI?
def load_json_data(path: str) -> list[dict]:
    with open(path, "r") as file:
        return json.load(file)
