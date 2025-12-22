import csv
import random
import string

with open('users.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['userAccount', 'planetCode'])
    
    for i in range(1, 1001):
        # 生成随机用户名
        username = 'user' + ''.join(random.choices(string.ascii_lowercase, k=5)) + str(i)
        # 生成星球编号
        planet_code = 10000 + i
        writer.writerow([username, planet_code])