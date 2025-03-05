import requests

def get_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_card_data(url):
    data = get_api_data(url)

    if data:
        print("Received JSON data:")
        return handle_card(data)
    else:
        print("Failed to retrieve data.")

def handle_card(data):
    print(data.get("name"))
    new_data = {
        "name": data.get("name"),
        "mana_cost": data.get("mana_cost"),
        "image_uri": data["image_uris"]["art_crop"],
        "type_line": data.get("type_line"),
        "oracle_text": data.get("oracle_text"),
        "power": data.get("power"),
        "toughness": data.get("toughness"),
        "loyalty": data.get("loyalty"),
    }
    return new_data

def get_random_card():
    url = f"https://api.scryfall.com/cards/random"
    return get_card_data(url)

def get_random_card_by_query(query):
    url = f"https://api.scryfall.com/cards/random?q={query}"
    return get_card_data(url)

def get_card_by_name(name):
    url = f"https://api.scryfall.com/cards/named?fuzzy={name}"
    return get_card_data(url)
