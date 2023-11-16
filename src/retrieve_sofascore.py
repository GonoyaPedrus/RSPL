from lxml import html

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
# Get the page
headers = {
    'authority': 'api.sofascore.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'if-none-match': 'W/"4bebed6144"',
    'origin': 'https://www.sofascore.com',
    'referer': 'https://www.sofascore.com/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}
cookies = dict(CONSENT="YES+944")
url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
page = requests.get(url, headers=headers, cookies=cookies)
print(page.status_code)

soup = BeautifulSoup(page.text, 'html.parser')
soup.prettify()
print(soup)

table = soup.xpath('//*[@id="stats_standard"]')
# Si vous avez trouvé la table, vous pouvez la parcourir et extraire les données.
if table:
    for row in table[0].findall('.//tr'):
        cells = row.findall('.//td')
        for cell in cells:
            print(cell.text)
else:
    print("Table non trouvée avec l'expression XPath spécifiée.")