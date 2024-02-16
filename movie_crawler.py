from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import telegram
import asyncio

url = 'http://www.cgv.co.kr/theaters/?areacode=01&theaterCode=0059&date=20240212'

async def send(text, bot) :    
    await bot.sendMessage(chat_id='6726881667', text=text)

def job_function() :
    bot = telegram.Bot(token = '6788564300:AAHX3yeXXWoAxOdN90T3VHcR7v6WxlxbqZE')

    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)   

    driver.get(url)

    iframe_xpath='//iframe[@id="ifrm_movie_time_table"]'
    iframe=WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, iframe_xpath))
    )
    driver.switch_to.frame(iframe)

    iframe_content_xpath='//div[@class="showtimes-wrap"]'
    iframe_content=WebDriverWait(driver, 1).until(
    EC.presence_of_element_located((By.XPATH, iframe_content_xpath))
    ).get_attribute("outerHTML")

    driver.switch_to.default_content()

    driver.quit()

    soup = BeautifulSoup(iframe_content, 'html.parser')
    is_imax_list = soup.select('span.imax')
    imax_name_lst= []

    if len(is_imax_list) > 0 :
        for i in is_imax_list :
            imax = i.find_parent('div', class_='col-times')
            imax_name_lst.append(imax.select_one('div.info-movie > a > strong').text.strip())   

        asyncio.run(send(str(imax_name_lst) + " IMAX가 열렸습니다." , bot))
        sched.pause()
    else:
        asyncio.run(send("열린 IMAX가 없습니다." , bot))

sched = BlockingScheduler()
sched.add_job(job_function, 'interval', seconds=30)
sched.start()