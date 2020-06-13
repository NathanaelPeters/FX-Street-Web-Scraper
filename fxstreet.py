import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from datetime import datetime
import schedule
import time
from FXstreetNLU import CurrencyGrm as NLU
import os

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.fxstreet.com/news?q=&hPP=17&idx=FxsIndexPro&p=0')

url = "https://www.fxstreet.com/news?q=&hPP=17&idx=FxsIndexPro&p=0"
driver.get(url)
timesRefreshed = 0
NLCode = 0
CurrentTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

pairs = ["NZD/CAD","GBP/CAD","EUR/CAD","CAD/CHF","AUD/CAD","NZD/USD","AUD/USD","USDCNH","USD/RUB","USD/SEK","EUR/JPY"]

def refresher():
    global NLCode
    WebDriverWait(driver,120).until(EC.presence_of_element_located((By.CSS_SELECTOR,"h4.fxs_headline_tiny a")))
    news_elems = driver.find_elements_by_css_selector("h4.fxs_headline_tiny a")
    NewestLink = news_elems[0].get_attribute('href')
    LenNewestLink = len(news_elems[0].get_attribute('href'))
    url = news_elems[0].get_attribute('href')
    response = requests.get(url)
    articlePage = BeautifulSoup(response.content, "html.parser")
    global timesRefreshed
    timesRefreshed+=1
    if(NLCode != int(NewestLink[(LenNewestLink-12): LenNewestLink])):
        print("there's been a new article: ", datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], NewestLink)
        paragraphs = articlePage.find_all('div', {"class":"fxs_article_body"})
        texts = []
        for p in paragraphs:
            texts.append(p.text)
            nlu = NLU()["Currency"]
            currenciesObj = nlu.extracting(p.text.lower())
            currencies = []
            report = ""
            print(currenciesObj)
            if currenciesObj:
                count = 0
                for el in currenciesObj:
                    if el == "USD":
                        currencies.append(el + "CAD")
                        count += 1
                    if el == "CAD":
                        currencies.append("USD" + el)
                        count += 1
                    if el == "GBP":
                        currencies.append(el + "USD")
                        count += 1
                    if el == "JPY":
                        currencies.append("USD" + el)
                        count += 1
                    if el == "EUR":
                        currencies.append(el + "USD")
                        count += 1
                    if el == "AUD":
                        currencies.append(el + "USD")
                        count += 1
                    if el == "NZD":
                        currencies.append(el + "USD")
                        count += 1
                if len(currencies) < 1: 
                    for cur in pairs:
                        if cur in p.text:
                            currencies.append(cur[0:3]+cur[4:6])
                            count += 1      
                report += str(count) + "\n"
                if len(currencies) >= 1:
                    for el in currencies:
                        report += datetime.utcnow().strftime('%Y.%m.%d %H:%M:%S:%f')[:-3] + "," + el + "\n"
                    print(report)
                    if os.path.exists("C:\\Users\\natep\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\FXstreet"):
                        os.remove("C:\\Users\\natep\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\FXstreet")
                        print("it was removed")
                    else:
                        print("The file does not exist")
                    time.sleep(1)
                    fh = open("C:\\Users\\natep\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\FXstreet", "w+")
                    fh.write(report)
                    print("it was created")
                    fh.close
        NLCode = int(NewestLink[(LenNewestLink-12): LenNewestLink])        

while True:
    refresher()
    time.sleep(10)
    driver.refresh()