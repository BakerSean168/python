import base64
def caesar(plaintext):
    str_list = list(plaintext)
    i = 0
    while i < len(plaintext):
        if not str_list[i].isalpha():
            str_list[i] = str_list[i]
        else:
            a = "A" if str_list[i].isupper() else "a"
            str_list[i] = chr((ord(str_list[i]) - ord(a) + 5) % 26 + ord(a) or 5)
        i = i + 1

    return ''.join(str_list)

flag = "*************************"
str = caesar(flag)
print(str)

#str="U1hYSFlLe2R0em1mYWpwc3RiaGZqeGZ3fQ=="

def decode_caesar():
    encoded_str = "U1hYSFlLe2R0em1mYWpwc3RiaGZqeGZ3fQ=="
    decoded_bytes = base64.b64decode(encoded_str)
    decoded_str = decoded_bytes.decode()

    str_list = list(decoded_str)
    i = 0
    while i < len(str_list):
        if not str_list[i].isalpha():
            str_list[i] = str_list[i]
        else:
            a = "A" if str_list[i].isupper() else "a"
            str_list[i] = chr((ord(str_list[i]) - ord(a) - 5) % 26 + ord(a))
        i = i + 1

    return ''.join(str_list)

decoded_str = decode_caesar()
print(decoded_str)
        