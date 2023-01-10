import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json
main_url = 'https://coinmarketcap.com/ru/'
def get_cur():
    req = requests.get(main_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    data = json.loads(soup.find('script', id='__NEXT_DATA__').get_text())
    for dt in data['props']['quotesLatestData']:
        if dt['symbol'] == 'RUB':
            return float(dt['p'])
def get_pages():
    req = requests.get(main_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    pages = soup.findAll('li',class_='page')[-1].find('a').get_text()
    return int(pages)
def get_data(requests):
    cur = get_cur()
    soup = BeautifulSoup(requests,"html.parser")
    table = soup.find('table')
    x = (len(table.findAll('tr')) - 1)
    for row in table.findAll('tr')[1:x]:
        col = row.findAll('td')
        name = col[2].find('a')['href'].replace('/ru/currencies/','').replace('/','')
        price = col[3].getText()
        if '$' in price:
            price = float(price.replace('$','').replace(',','')) / cur
        else:
            price = float(price.replace('₽', '').replace(',', '').replace('...', '0000000000').replace('…','').replace('<',''))
        with open('data.csv', 'a') as f:
            f.write(f'{name},{price:.2f}\n')

# Function to fetch data from server
def fetch(session, base_url):
    with session.get(base_url) as response:
        data = response.text
        if response.status_code != 200:
            print("FAILURE::{0}".format(base_url))
        return data

async def get_data_asynchronous():
    pages = get_pages()
    urls = [f'{main_url}?page={i}' for i in range(pages+1)]
    with ThreadPoolExecutor(max_workers=20) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url) # Allows us to pass in multiple arguments to `fetch`
                )
                for url in urls
            ]
            for response in await asyncio.gather(*tasks):
                get_data(response)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(get_data_asynchronous())
    except KeyboardInterrupt:
        pass
main()