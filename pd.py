import base64

def encrypt(text):
    # Base64 加密
    base64_str = base64.b64encode(text.encode()).decode()
    
    # 凯撒密码右移6位
    result = ""
    for char in base64_str:
        if char.isalpha():
            # 处理字母
            ascii_offset = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - ascii_offset + 6) % 26 + ascii_offset
            result += chr(shifted)
        elif char.isdigit():
            # 处理数字
            shifted = (int(char) + 6) % 10
            result += str(shifted)
        else:
            # 保持其他字符不变
            result += char
            
    return result

def main():
    # 获取用户输入
    text = input("请输入要加密的文本: ")
    
    # 加密并输出结果
    encrypted = encrypt(text)
    print(f"加密结果: {encrypted}")

if __name__ == "__main__":
    main()

# asdf== asdfff