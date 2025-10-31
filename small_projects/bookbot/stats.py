def words_counter(book):
	num_words = len(book.split())

	return f'Found {num_words} total words'


def character_counter(book):
	lower_book = book.lower()
	unique_chars = set(lower_book)
	count_dict = {}
	for c in unique_chars:
		char_count = lower_book.count(c)
		count_dict[c] = char_count

	return count_dict


def character_list(char_dict):
	char_list = []

	for k, v in char_dict.items():
		if k.isalpha():
			char_list.append({"char": k, "num": v})

	return sorted(char_list, key=lambda x: x["num"], reverse=True)



if __name__ == "__main__":
	# print(words_counter())
	test_text = 'Ba,NA.na'
	char_dict = character_counter(test_text)
	print(character_list(char_dict))
