import sys
from stats import (
    character_counter,
	character_list,
    words_counter,
)


if len(sys.argv) < 2:
    print("Usage: python3 main.py <path_to_book>")
    sys.exit(1)


script_name = sys.argv[0]
sys_book_path = sys.argv[1]


def get_book_text(book_path):
	with open(f"/home/blaise/Workspace/repos/bookbot/{book_path}") as f:
		file_contents = f.read()

	return file_contents


def generate_report(book):
	report_text = f"""
============ BOOKBOT ============
Analyzing book found at {sys_book_path}...
----------- Word Count ----------
Found {words_counter(book)} total words
--------- Character Count -------
"""
	count_dict = character_counter(book)
	char_list = character_list(count_dict)

	for c in char_list:
		report_text += f"{c['char']}: {c['num']}\n"

	report_text += "============= END ==============="
	return report_text


book_text = get_book_text(book_path=sys.argv[1])
print(generate_report(book=book_text))
