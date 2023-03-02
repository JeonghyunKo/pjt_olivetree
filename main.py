# Project olive tree
# let's pick some olives from the tree!

import re
import pandas as pd
import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import os 

url = 'https://www.oliveyoung.co.kr/store/main/main.do?oy=0' 
r = requests.get(url)

if r.status_code == 200:
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

else : 
    print(r.status_code)

events = soup.find_all(class_ = 'banner_link')

banner_title = []
banner_desc = []
banner_link = []

for event in events : 

    
    try : 
        if 'PlanShop' in event["href"]  : 
            banner_title.append(event.find("span").text)
            banner_desc.append(event.text)
            banner_link.append(event["href"])
        else : 
            continue
    except : 
        continue


promo_title = []
promo_start_dt = []
promo_end_dt = []
promo_contents = []
promo_catgs = []

for l in banner_link : 
    url = l
    r = requests.get(url)

    if r.status_code == 200:
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')

    else : 
        print(r.status_code)

    #title 
    try : 
        title = soup.find(id = "planTitle").text
    except : 
        title = 'none(기타)'
    #period
    try : 
        period = soup.find(class_ = "title-plan-view").find("span").text
        period = period.replace("\n", "").replace("\t", "").replace(" ", "")
        start_dt = period.split("-")[0]
        end_dt = period.split("-")[1]
    except : 
        start_dt = 'none'
        end_dt = 'none'
    #desc
    try : 
        desc = soup.find_all(class_ = 'oyblind')
        desc = [d.text.replace("\n", " ").replace("  ", " ").replace("  ", " ") for d in desc]
    except : 
        desc = 'none'
    #catg
    try : 
        catg = soup.find_all(class_ = 'plan-menu')[0].text.split("\n")
        catg = [c for c  in catg if c != '']
    except :
        catg = 'none'

    promo_title.append(title)
    promo_start_dt.append(start_dt)
    promo_end_dt.append(end_dt)
    promo_contents.append(desc)
    promo_catgs.append(catg)

    #img save
    promo_imgs = soup.find_all("img")
    promo_imgs = [i["src"] for i in promo_imgs if (("goods" not in i["src"]) and ('https' not in i["src"])) or ("planshop" in i["src"])]
    promo_imgs = ['https:'+i if "http" not in i else i for i in promo_imgs]
    path = "./result/images/" + start_dt.replace(".","") + title

    try : 
        os.mkdir(path)
        
        for num, img in enumerate(promo_imgs) : 
            urllib.request.urlretrieve(img, path + f"/{num}.jpg")
    except : 
        continue 


df1 = pd.DataFrame({"banner_title" : banner_title, 
            "banner_desc" : banner_desc,
            "banner_link" : banner_link} 
             )
df2 = pd.DataFrame({"banner_link" : banner_link, 
            "promo_title" : promo_title, 
            "promo_start_dt" : promo_start_dt,
            "promo_end_dt" : promo_end_dt, 
            "promo_contents" : promo_contents, 
            "promo_catgs" : promo_catgs} 
             )

result = pd.merge(left= df1, right = df2, how= "left")
result = result[["promo_title", "promo_start_dt", "promo_end_dt", "banner_title", "banner_desc", "promo_contents", "promo_catgs", "banner_link"]]

update_dt = datetime.now()
result_path = f'./result/result_{update_dt}.csv'

result.to_csv(result_path, encoding = 'utf-8-sig', index = False)