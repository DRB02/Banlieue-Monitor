import requests
import time
from bs4 import BeautifulSoup
import threading
from datetime import datetime
from discord_webhook import DiscordEmbed, DiscordWebhook

site = ['https://www.clandebanlieue.com/shop-all/?sort=newest&limit=24&sort=newest&brand=0', 'https://www.clandebanlieue.com/shop-all/']

#unquote which one you need
#WebhookUrl = 'webhook1'
#WebhookUrl = ['webhook1', 'webhook2']
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}
#information for webhook
def post_discord(name, picture, price, url, sizelist):
    webhook = DiscordWebhook(url=WebhookUrl, username='Banlieue Shop Monitor', avatar_url='https://www.soccerfanshop.nl/wp-content/uploads/2019/05/1A-2-845x321.png')
    embed = DiscordEmbed(title=name, color=0x9062CD, url=url)
    embed.set_author(name='Banlieue Shop Monitor', url='https://www.clandebanlieue.com/shop-all/?sort=newest&limit=24&sort=newest&brand=0')
    embed.add_embed_field(name='Sizes:', value=sizelist)    
    embed.add_embed_field(name='Price:', value='€'+ price)
    embed.add_embed_field(name='Links:', value='[Login](https://www.clandebanlieue.com/account/login/)' + ' | ' + '[Cart](https://www.clandebanlieue.com/cart/)' + ' | ' + '[Checkout](https://www.clandebanlieue.com/checkout/)',inline=False)
    embed.set_thumbnail(url=picture)
    embed.set_footer(text='Developed by DRB02#0001')
    embed.set_timestamp()
    webhook.add_embed(embed)
    webhook.execute()


def main(site):
    while True:
        try:
            source = requests.get(site, headers=headers).text
            soup = BeautifulSoup(source, 'lxml')
            #gets product info
            for ProductName in soup.find_all('li', class_='product'):
                #name = ProductName.find("h3").a.text
                url = ProductName.find("h3").a.get('href')
                link = url + '?format=json'
                api = requests.get(link, headers=headers).json()
                name = api['product']['fulltitle']
                pid = api['product']['image']
                picture = 'https://cdn.webshopapp.com/shops/277743/files/'+(str(pid))+'/image.jpg'
                price = (str(api['product']['price']['price']))
                
                sizelist = ''
                try:
                    sizes = api['product']['matrix']['size']['values']               
                    #check api for available sizes
                    for key in sizes:
                        size = sizes[key]
                        sizename = size['title']
                        #store sizes to var
                        sizelist += sizename + '\n'
                except:
                    sizelist = 'N/A'
                #file to store links in
                filename = 'banlieuelinks.txt'
                #checks .txt files if it is a new link
                with open(filename, 'r') as rf:
                    read = rf.read()
        
                if url not in read:
                    with open(filename, 'a') as af:
                        af.write(url + '\n')
                    #sends webhook
                    print(str(datetime.now()) + ' ' + url)
                    post_discord(name, picture, price, url, sizelist)
                # else:
                #     print("Not a new link")
            #delay
            print(str(datetime.now()))
            print('Product check done waiting for next check...')
            time.sleep(60)
        except:
            print('Something went wrong with: ' + link)
            time.sleep(120)

if __name__ == "__main__":
    for i in site:
        threading.Thread(target=main,args=(i,)).start()
