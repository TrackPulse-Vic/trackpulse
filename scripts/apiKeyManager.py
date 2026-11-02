import json
import os
import secrets


API_KEYS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'databases', 'apiKeys.json')


def checkKey(key):
    try:
        with open(API_KEYS_PATH, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None, False

    key_info = api_keys.get(key)
    if key_info:
        user_id = key_info.get("user_id")
        privileged_value = key_info.get("privileged", key_info.get("privlidged", False))
        privileged = privileged_value is True or str(privileged_value).lower() == "true"
        return user_id, privileged
    return None, False


def generateKey(user_id):
    if not user_id:
        raise ValueError('A user ID is required to generate an API key')

    try:
        with open(API_KEYS_PATH, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
    except FileNotFoundError:
        api_keys = {}
    except json.JSONDecodeError as exc:
        raise RuntimeError('The API key store contains invalid JSON') from exc

    key = secrets.token_urlsafe(32)
    while key in api_keys:
        key = secrets.token_urlsafe(32)

    api_keys[key] = {
        'user_id': user_id,
        'privileged': False,
    }

    with open(API_KEYS_PATH, 'w', encoding='utf-8') as f:
        json.dump(api_keys, f, indent=4)
        f.write('\n')

    return key