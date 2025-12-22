
with open("1.txt", "r", encoding='utf-8') as f:  #打开文本
    data = f.read()   #读取文本
    g =	data[::-1]
    print(g)
f.close()