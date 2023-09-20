from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import requests

app = Flask(__name__)

# 멜론 차트 크롤링 함수
def get_melon_chart():
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://www.melon.com/chart/'
    html = requests.get(url, headers=header).text

    soup = BeautifulSoup(html, 'html.parser')

    chart = []
    for item in soup.select("#lst50"):
        rank = item.select_one('.rank').get_text(strip=True)
        title = item.select_one('.ellipsis.rank01').get_text(strip=True)
        artist = item.select_one('.checkEllipsis').get_text(strip=True)
        chart.append({"rank": rank, "title": title, "artist": artist})

    return chart

#지니 차트 크롤링 함수
def get_genie_chart():
    header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.genie.co.kr/chart/top200',headers=header)

    soup = BeautifulSoup(data.text, 'html.parser')

    chart = soup.select('#body-content > div.newest-list > div > table > tbody > tr')

    genie = []

    for tr in chart:
        title = tr.select_one('td.info > a.title.ellipsis').text.strip()
        artist = tr.select_one('td.info > a.artist.ellipsis').text.strip()
        rank = tr.select_one('td.number').text[0:2].strip()

        genie.append({"rank": rank, "title": title, "artist": artist})
    
    return genie

# 멜론 댓글 크롤링 함수
def search_melon_comment(title):
    driver = webdriver.Chrome('chromedriver.exe')
    driver.implicitly_wait(10)
    driver.get('https://www.melon.com')
    element = driver.find_element(By.ID, 'top_search')
    element.send_keys(title)
    element.send_keys(Keys.RETURN)
    time.sleep(4)
    
    tab = driver.find_element(By.ID, 'divCollection')
    li = tab.find_elements(By.TAG_NAME,'li')
    li[2].click()
    time.sleep(2)

    wrap = driver.find_elements(By.CLASS_NAME, 'ellipsis')
    wrap0 = wrap[0]
    list = wrap0.find_elements(By.CLASS_NAME, 'odd_span')
    list[2].click()
    time.sleep(2)
    
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    contents = soup.find_all('div', {'class':'cmt_text d_cmtpgn_cmt_full_contents'})

    comments = []
    for item in contents:
        comment = item.get_text(strip=True)
        comments.append(comment)

    return comments

#지니댓글 크롤링 함수
def search_genie_comment(title):
    driver = webdriver.Chrome('chromedriver.exe')
    driver.implicitly_wait(10)
    url = f"https://www.genie.co.kr/search/searchMain?query={title}"
    driver.get(url)
    time.sleep(2)

    table = driver.find_element(By.CLASS_NAME,'list-wrap')
    tr = table.find_elements(By.CLASS_NAME,'list')
    tr0=tr[0]
    a = tr0.find_elements(By.TAG_NAME,'a')
    a[1].click()
    time.sleep(2)

    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    list = soup.find('div',{'class':'commnt-list'})
    contents = list.find_all('p')

    comments = []
    for item in contents:
        comment = item.get_text(strip=True)
        comments.append(comment)

    return comments
    

@app.route("/")
def index():
    melon_chart = get_melon_chart()
    genie_chart = get_genie_chart()
    return render_template("chart.html", melon_chart=melon_chart,genie_chart=genie_chart)

@app.route("/search_melon_comment")
def search_melon_page():
    selected_title = request.args.get("selected_title", "")
    comments = search_melon_comment(selected_title)
    return render_template("comments.html", selected_title=selected_title, comments=comments)

@app.route("/search_genie_comment")
def search_genie_page():
    selected_title = request.args.get("selected_title", "")
    comments = search_genie_comment(selected_title)
    return render_template("comments.html", selected_title=selected_title, comments=comments)
if __name__ == "__main__":
    app.run(debug=True)
