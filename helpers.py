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
    n1, n2 = range_string.split('-', 1)
    start = min(int(n1), int(n2))
    end = max(int(n1), int(n2))
    return [str(i) for i in range(start, end + 1)]


# print(translate_number_range('1990-2004'))


def interpret_noi(numbers: list[str]) -> list[str]:
    output = []
    for num in numbers:
        if '-' in num:
            output.extend(translate_number_range(num))
        else:
            output.append(num)

    return output


# print(interpret_noi(['6-10', '1', '19', '25-14', '80']))


def generate_email_permutations(first_name: str = None, last_name: str = None, middle_name: str = None, domain: str = None, noi: list[str] = None, masks: list[str] = None):
    perms = []
    # Appends a blank character to generate all combos without NOI
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
            for u, s in unsafe.items():
                perm = perm.replace(u, s)

            if not perm[0].isalnum():
                perm = perm[1:]

            perm = perm.lower()

            if perm not in perms:
                perms.append(perm)

    if domain.lower() in perms:
        perms.remove(domain.lower())

    return perms


# print(generate_email_permutations('John', 'X', 'Fake', '@gmail.com', ['10', '40', '99', '180'], ['%FIRST.%LAST%NOI%DOMAIN', '%F.%LAST%DOMAIN']))


def generate_username_permutations(username: str, noi: list[str], masks: list[str]):
    perms = []
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