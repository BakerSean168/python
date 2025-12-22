f=open("./python-code/misc5.png",'rb')
con=f.read()#二进制形式
with open('flag.png','wb') as nfile:
    for b in con:
        #这里的b是int形式，要转换成bytes时，使用bytes(),且里面的内容需要加[]
        nfile.write(bytes([b^0x50]))