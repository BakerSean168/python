import requests
from bs4 import BeautifulSoup
import concurrent.futures

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}

def fetch_url(companyId):
    url = 'https://www.butian.net/Company/' + str(companyId)
    response = requests.get(url=url, headers=header)
    response.encoding = "UTF-8"
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find div with class 'firmname'
    firmname_div = soup.find('div', class_='firmName1')

    if firmname_div:
        return firmname_div.text + '\n'
    else:
        return ''

with open('a.txt', 'a', encoding='utf-8') as file:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, companyId): companyId for companyId in range(4127, 64848)}
        for future in concurrent.futures.as_completed(future_to_url):
            data = future.result()
            file.write(data)