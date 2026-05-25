import json
import os


def parse_x_tokens_txt(path='x_tokens.txt'):
    """Load X token values from x_tokens.txt using section-aware parsing."""
    if not os.path.exists(path):
        return {}

    global_fields = {
        'bearer token': 'bearer_token',
    }

    section_fields = {
        'oauth1': {
            'consumer key': 'oauth1_consumer_key',
            'consumer key secret': 'oauth1_consumer_secret',
            'access token': 'oauth1_access_token',
            'access token secret': 'oauth1_access_token_secret',
        },
        'oauth2': {
            'client id': 'oauth2_client_id',
            'client secret': 'oauth2_client_secret',
            'access token': 'oauth2_access_token',
            'refresh token': 'oauth2_refresh_token',
        }
    }

    data = {}
    pending_key = None
    current_section = None

    with open(path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            lower_line = line.lower()
            if lower_line.startswith('##oauth 1.0 keys##'):
                current_section = 'oauth1'
                pending_key = None
                continue
            if lower_line.startswith('##oauth 2.0 keys##'):
                current_section = 'oauth2'
                pending_key = None
                continue

            if pending_key:
                data[pending_key] = line
                pending_key = None
                continue

            if current_section and lower_line in section_fields[current_section]:
                pending_key = section_fields[current_section][lower_line]
                continue

            if lower_line in global_fields:
                pending_key = global_fields[lower_line]
                continue

    return data


def normalize_token_data(data):
    if not data:
        return {}

    data = dict(data)
    if 'client_id' in data and 'oauth2_client_id' not in data:
        data['oauth2_client_id'] = data['client_id']
    if 'client_secret' in data and 'oauth2_client_secret' not in data:
        data['oauth2_client_secret'] = data['client_secret']
    if 'consumer_key' in data and 'oauth1_consumer_key' not in data:
        data['oauth1_consumer_key'] = data['consumer_key']
    if 'consumer_secret' in data and 'oauth1_consumer_secret' not in data:
        data['oauth1_consumer_secret'] = data['consumer_secret']
    if 'access_token_secret' in data and 'oauth1_access_token_secret' not in data:
        data['oauth1_access_token_secret'] = data['access_token_secret']
    if 'access_token' in data:
        if 'oauth1_access_token' not in data and ('oauth1_access_token_secret' in data or 'access_token_secret' in data):
            data['oauth1_access_token'] = data['access_token']
        elif 'oauth2_access_token' not in data:
            data['oauth2_access_token'] = data['access_token']

    return data


def load_x_token_json(path='x_token.json'):
    if not os.path.exists(path):
        return {}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return normalize_token_data(json.load(f))
    except Exception:
        return {}


def write_x_token_json(token_data, path='x_token.json'):
    token_data = normalize_token_data(token_data)
    if not token_data or ('oauth1_access_token' not in token_data and 'oauth2_access_token' not in token_data):
        raise ValueError('Token data must include an OAuth1 or OAuth2 access token')

    output = {}
    allowed_keys = {
        'bearer_token',
        'oauth1_consumer_key',
        'oauth1_consumer_secret',
        'oauth1_access_token',
        'oauth1_access_token_secret',
        'oauth2_client_id',
        'oauth2_client_secret',
        'oauth2_access_token',
        'oauth2_refresh_token',
    }

    for key in allowed_keys:
        if token_data.get(key):
            output[key] = token_data[key]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f)

    return output
