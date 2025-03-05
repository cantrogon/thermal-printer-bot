from cards_handler import get_random_card_by_query, get_card_by_name, get_random_card
from printer_main import print_request
import re


def replace_character(input_string, old_char, new_char):
	return re.sub(old_char, new_char, input_string)

def print_card(data, print_type="sideways"):
	if data is None:
		print("Error: Card not found")
		return None

	name = f"{data["name"]} - {data["mana_cost"]}" if data["mana_cost"] else data["name"]
	image_url = data["image_uri"]
	type_line = replace_character(data["type_line"], "—", "-")
	oracle_text = data["oracle_text"]
	oracle_text = replace_character(oracle_text, "—", "-")
	oracle_text = replace_character(oracle_text, "•", "-")
	oracle_text = replace_character(oracle_text, "\n", "\n\n")
	oracle_text = re.sub(r"\(.*?\)", "", oracle_text)
	pt = f"{data["power"]}/{data["toughness"]}"
	loyalty = data["loyalty"]

	if print_type == "straight":
		print_obj = [
			{"type": "text", "content": name},
			{"type": "image_url", "content": image_url},
			{"type": "text", "content": type_line},
			{"type": "text", "content": oracle_text},
		]

		if data["power"] is not None and data["toughness"] is not None:
			print_obj.append({"type": "text", "content": pt})
		if loyalty is not None:
			print_obj.append({"type": "text", "content": loyalty})

	elif print_type == "sideways":
		joiner = '\n\n'
		main_text = joiner.join([type_line, oracle_text])
		if data["power"] is not None and data["toughness"] is not None:
			main_text = joiner.join([main_text, pt])
		if loyalty is not None:
			main_text = joiner.join([main_text, loyalty])

		# height is percentage of page height, padding is percentage of height
		print_obj = [
			{"type": "text", "content": name, "height": 0.1},
			{"type": "image_url", "content": image_url, "height": 0.4, "padding_top": 0.1, "padding_bottom": 0.1},
			{"type": "text", "content": main_text, "height": 0.5},
		]

	print_request(print_obj, print_type=print_type)
	return True


def print_random():
	return print_card(get_random_card())

def print_random_by_query(query):
	return print_card(get_random_card_by_query(query))

def print_random_creature_by_cmc(cmc):
	query = f"t:creature cmc={cmc}"
	card = get_random_card_by_query(query)
	return print_card(card)

def print_card_by_name(name):
	return print_card(get_card_by_name(name))


if __name__ == "__main__":
	# print_random_creature_by_cmc(2)
	# print_card_by_name("A-Urza, Powerstone Prodigy")
	# print_card_by_name("gala gree")
	# print_card_by_name("grizwz bear")
	# print_card_by_name("Vengeful Strangler // Strangling Grasp")
	# print_text_windows(None)

	# card_data = get_random_card_by_query("cmc=2")
	# print_card(card_data, print_type="straight")
	# print_card(card_data, print_type="sideways")

	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))
	print_card(get_random_card_by_query("t:instant"))

