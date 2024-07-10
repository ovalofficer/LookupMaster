import re


def has_trailing_int(text: str) -> bool:
    if len(text) < 1:
        return False
    return text[len(text) - 1].isdigit()


def add_trailing_int(text: str) -> str:
    # This return value can be changed to start index at 0 or 1. 1 seems more intuitive for users.
    return text + "_1"


def get_trailing_int(text: str) -> int:
    full_num = ""
    # Iterate the string backwards to find the trailing numbers
    for c in text[::-1]:
        if c.isdigit():
            # If the current character is a digit, add it to our new number to return
            full_num += c
        else:
            # Reverse the string that contains the int and cast to an integer, return
            return int(full_num[::-1])

    # Grabs ALL ints from text, not continuous
    # return int(''.join(c for c in text[::-1] if c.isdigit())[::-1])


def increment_trailing_int(text: str) -> str:
    # Returns the text with the incremented trailing int
    return text[:-len(str(get_trailing_int(text)))] + str(get_trailing_int(text) + 1)


def get_alternate_name(text: str, directory: dict) -> str:
    # If the file name already exists and doesn't end in a trailing integer, give it a trailing integer
    if not has_trailing_int(text):
        text = add_trailing_int(text)

    # While the text exists in directory keys, increment the integer
    while text in directory.keys():
        text = increment_trailing_int(text)

    # Return new text with incremented integer or new integer
    return text


def letter_to_number(letter):
    # T9 letter to number dict
    ltn = {'abc': 2,
           'def': 3,
           'ghi': 4,
           'jkl': 5,
           'mno': 6,
           'pqrs': 7,
           'tuv': 8,
           'wxyz': 9}

    for letters, number in ltn.items():
        if letter.lower() in letters:
            return str(number)


def remove_non_digits(num: str):
    return ''.join(c for c in num if c.isdigit())


def remove_all_whitespace(s: str) -> str:
    return re.sub(r'(\s|\u180B|\u200B|\u200C|\u200D|\u2060|\uFEFF)+', '', s)


def remove_special_characters(num: str):
    return ''.join(c for c in num if c.isalnum())


def validate_email_format(email: str) -> bool:
    # very basic email regex from stackoverflow
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,9}\b'
    return re.fullmatch(email_regex, email) is not None


# print(validate_email_format('123@gmail.com'))
# print(validate_email_format('123gmail.com'))


def clean_phone_number(num: str):
    # converts all letters to numbers and then removes non-digits
    result = ''
    for n in num:
        if n.isalpha():
            result += letter_to_number(n) or ''
        else:
            result += n

    return remove_non_digits(result)


def translate_phone_mask(mask: str, mask_char: str, phone_number: str):
    # Expected masks: XXX-XXX-XXXX \ area=XXX&rest=XXXXXXX
    n = clean_phone_number(phone_number)
    current_index = 0
    result = ''
    for c in mask:
        if c == mask_char:
            result += n[current_index]
            current_index += 1
        else:
            result += c

    return result


# print(translate_phone_mask('XXX-XXX-XXXX', 'X', '1234567890'))
# print(translate_phone_mask('?s=XXX?m=XXX?l=XXXX','X',  '1234567890'))

def translate_number_range(range_string: str) -> list[str]:
    # translates "1-10" to a list containing 1, 2, 3, etc. for processing number ranges in permutator
    n1, n2 = range_string.split('-', 1)
    start = min(int(n1), int(n2))
    end = max(int(n1), int(n2))
    return [str(i) for i in range(start, end + 1)]


# print(translate_number_range('1990-2004'))


def interpret_noi(numbers: list[str]) -> list[str]:
    # interpret numbers of interest: processes the NOI field from permutator and uses applicable translators
    output = []
    for num in numbers:
        if '-' in num:
            output.extend(translate_number_range(num))
        else:
            output.append(num)

    return output


# print(interpret_noi(['6-10', '1', '19', '25-14', '80']))


def generate_email_permutations(first_name: str = None, middle_name: str = None, last_name: str = None,
                                domain: str = None, noi: list[str] = None, masks: list[str] = None):
    perms = []
    # Appends a blank character to also generate all combos without NOI
    noi.append('')

    for mask in masks:
        for num in noi if '%NOI' in mask else [None]:

            perm = mask
            mask_resolve = {
                "%FIRST": first_name or '',
                "%MIDDLE": middle_name or '',
                "%LAST": last_name or '',
                "%NOI": num or '',
                "%DOMAIN": domain if '@' in domain else '@' + domain,
                "%F": first_name[0] if len(first_name) > 0 else '',
                "%M": middle_name[0] if len(middle_name) > 0 else '',
                "%L": last_name[0] if len(last_name) > 0 else ''
            }

            # translates the mask with the supplied variables

            for key, replacement in mask_resolve.items():
                perm = perm.replace(key, replacement)

            unsafe = {
                '..': '.',
                '--': '-',
                '__': '_',
                '-@': '@',
                '.@': '@',
                '_@': '@'
            }

            # removes doubles and unsafe variables
            for u, s in unsafe.items():
                perm = perm.replace(u, s)

            # remove leading special characters
            while not perm[0].isalnum():
                perm = perm[1:]

            # lowercase current permutation
            perm = perm.lower()

            # if the permutation exists already, don't add duplicate

            if perm not in perms:
                perms.append(perm.lower())

    if domain.lower() in perms:
        perms.remove(domain.lower())

    return perms


# print(generate_email_permutations('John', 'X', 'Fake', '@gmail.com', ['10', '40', '99', '180'], ['%FIRST.%LAST%NOI%DOMAIN', '%F.%LAST%DOMAIN']))


def generate_username_permutations(username: str, noi: list[str], masks: list[str]):
    perms = []
    # Appends a blank character to generate all combos without NOI
    noi.append('')
    for mask in masks:
        for num in noi if '%NOI' in mask else [None]:
            perm = mask
            mask_resolve = {
                "%USERNAME": username,
                "%NOI": num or ''
            }

            for key, replacement in mask_resolve.items():
                perm = perm.replace(key, replacement)

            if perm not in perms:
                perms.append(perm)

    return perms

# print(generate_username_permutations('catman', ['15153', '180', '99'], ['%USERNAME%NOI']))
