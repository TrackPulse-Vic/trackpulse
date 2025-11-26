import json


def checkKey(key):
    with open('databases/apiKeys.json', 'r') as f:
        api_keys = json.load(f)
        if key in api_keys:
            user_id = api_keys[key]["user_id"]
            privileged = api_keys[key]["privlidged"] == "True"
            return user_id, privileged
    return None, False