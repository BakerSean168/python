f1 = open("1.png","rb")
f2 = open("2.png","wb")
all_data = f1.read()
lt = []
for i in all_data:
    if i == 0:
        lt.append(i)
    else:
        lt.append(0x100 - i)
f2.write(bytes(lt))
f1.close()
f2.close()