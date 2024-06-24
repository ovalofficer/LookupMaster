def letter_to_number(letter):
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


def remove_special_characters(num: str):
    return ''.join(c for c in num if c.isdigit() or c.isalpha())


def clean_phone_number(num: str):
    result = ''
    for n in num:
        if n.isalpha():
            result += letter_to_number(n) or ''
        else:
            result += n

    return remove_non_digits(result)


def translate_mask(mask: str, phone_number: str):
    # Expected masks: XXX-XXX-XXXX \ area=XXX&rest=XXXXXXX
    n = clean_phone_number(phone_number)
    current_index = 0
    result = ''
    for c in mask:
        if c == 'X':
            result += n[current_index]
            current_index += 1
        else:
            result += c

    return result
