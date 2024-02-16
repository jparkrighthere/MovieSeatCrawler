from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup


import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import asyncio
import datetime
import re

from apscheduler.schedulers.blocking import BlockingScheduler


def setUrl(date) :
    if date == '' :
        date = datetime.datetime.now().strftime("%Y%m%d")
    
    url = 'http://www.cgv.co.kr/theaters/?areacode=01&theaterCode=0013&date={}'.format(date)
    return url

#텔레그램 봇이 메시지 전달하도록
async def send(text, bot, chat_id) :
     #텔레그램 봇의 메시지 전달은 비동기..
    await bot.sendMessage(chat_id=chat_id, text=text)


def check_args(context) :
    
    text_caps = context.args
    
    if len(text_caps) > 0 :
        if re.match(r'^([\s\d]+){8}$', text_caps[0]) and check_is_valid_date(text_caps[0]) :            
            return text_caps[0]
        else :
            return ''
    else :
        return ''


def check_is_valid_date(text) :
    try :
        datetime_format = "%Y%m%d"
        datetime_result = datetime.datetime.strptime(text, datetime_format)

        max_datetime = datetime.datetime.now() + datetime.timedelta(days=22)

        if datetime_result > max_datetime or datetime_result < datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) :            
            return False

        return True
    except ValueError as e :
        return False

async def job_function(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    date = check_args(context)
    
    url = setUrl(date)

    #텔레그램 봇 인스턴스 생성
    bot = context.bot
    chat_id = update.effective_chat.id

    #Firefox의 'headless' 옵션을 사용하기 위함.
    options = FirefoxOptions()
    options.add_argument("--headless")
    # selenium의 webdriver를 통해 firefox 실행
    # headless 옵션이 사용되었으므로, firefox 창이 뜨지 않음. headless 없으면 firefox 창이 뜸.
    driver = webdriver.Firefox(options=options)

    # 대상 웹 페이지로 이동.
    driver.get(url)

    # iframe의 XPath를 찾아서 해당 iframe으로 전환.
    iframe_xpath = '//iframe[@id="ifrm_movie_time_table"]'  # 실제 웹 페이지의 iframe ID에 맞게 수정
    # 페이지가 로드될 때까지 대기.
    iframe = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, iframe_xpath))
    )
    
    # iframe 태그로 전환
    driver.switch_to.frame(iframe)

    # iframe 내용이 로드될 때까지 대기.
    iframe_content_xpath = '//body'  # 실제 웹 페이지의 iframe 내용에 맞게 수정
    iframe_content = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, iframe_content_xpath))
    ).get_attribute("outerHTML")

    # iframe에서 벗어나 원래의 상위 레벨로.
    driver.switch_to.default_content()

    # WebDriver를 종료.
    driver.quit()

    # 강의를 따라하다보니 bs4 모듈로 html 태그를 이용할 수 있도록.
    soup = BeautifulSoup(iframe_content, 'html.parser')
    # print(soup)

    # imax가 존재하는 태그 리스트
    is_imax_list = soup.select('span.imax')
    imax_name_lst= []
    if len(is_imax_list) > 0:
        for i in is_imax_list :
            #imax가 존재하는 태그
            imax = i.find_parent('div', class_='col-times')
            #imax가 존재하는 영화의 이름
            imax_name_lst.append(imax.select_one('div.info-movie > a > strong').text.strip())

        # 챗봇으로 전송.
        await send(date + ' ' + str(imax_name_lst) + " IMAX가 열렸습니다." , bot, chat_id)
        # sched.pause()
    else :
        # 챗봇으로 전송.
        await send(date + ' ' + "열린 IMAX가 없습니다." , bot, chat_id)    


# sched = BlockingScheduler()
# sched.add_job(job_function, 'cron', hour=0, minute=0)
# sched.start()


if __name__ == "__main__" :
    application = ApplicationBuilder().token('6788564300:AAHX3yeXXWoAxOdN90T3VHcR7v6WxlxbqZE').build()
    
    start_handler = CommandHandler('start', job_function)
    application.add_handler(start_handler)
    
    application.run_polling()