import base64

# 泄露的结果
encoded_flag = "4A5A4C564B36434E4B5241544B5432454E4E32465552324E47424758534D44594C4657564336534D4B5241584F574C4B4B463245365643424F35485649534C584A5A56454B4D4B5049354E47593D3D3D"

# Base16 解码
base16_decoded = base64.b16decode(encoded_flag)

# Base32 解码
base32_decoded = base64.b32decode(base16_decoded)

# Base64 解码
original_var = base64.b64decode(base32_decoded)

# 打印解码后的结果
print(original_var.decode())

print(original_var)