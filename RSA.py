from Crypto.Util.number import *

str = "ctf"

toNum = bytes_to_long(str.encode())

print(toNum)

num = 84150717615789492248
flag = long_to_bytes(num)

print(flag)