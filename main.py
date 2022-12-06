# Selenium 관련 import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# 기타 import
import os
from pathlib import Path
import shutil
import subprocess
import pyperclip
import platform
from pyvirtualdisplay import Display
from datetime import datetime

# pyperclip.copy() 대체 - 리눅스용 copy
def copy_clipboard(msg):
    with subprocess.Popen(['xclip','-selection', 'clipboard'], stdin=subprocess.PIPE) as pipe:
        pipe.communicate(input=msg.encode('utf-8'))

########################################################################################## 네이버 ##########################################################################################
# 네이버 홍보글 맨 위에 있는지 확인 (최신화 확인)
def naver_isontop(driver, keyword):
    driver.get('http://ff14.game.naver.com/community/freecompany')
    return keyword in driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/table/tbody/tr[1]/td[2]/span[1]/a/strong').text

# 네이버 로그인 후 자동 리다이렉트
def naver_login(driver, id, pw):
    driver.get('https://nid.naver.com/nidlogin.login?url=https%3A%2F%2Fgame.naver.com%2Flogin.nhn%3FnxtUrl%3Dhttp%253A%252F%252Fff14.game.naver.com%252Fcommunity%252Ffreecompany')
    try: pyperclip.copy(id)
    except pyperclip.PyperclipException: copy_clipboard(id)
    driver.find_element(By.ID, 'id').send_keys(Keys.CONTROL + 'v') # 아이디 입력
    try: pyperclip.copy(pw)
    except pyperclip.PyperclipException: copy_clipboard(pw)
    driver.find_element(By.ID, 'pw').send_keys(Keys.CONTROL + 'v') # 비밀번호 입력
    try: pyperclip.copy('')
    except pyperclip.PyperclipException: copy_clipboard('')
    driver.find_element(By.ID, 'log.login').click() # 로그인 버튼
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/form/fieldset/span[2]/a').click() # 브라우저 등록 안 함

# 네이버 keyword가 들어간 모든 홍보글 삭제
def naver_delete(driver, keyword):
    driver.get(f'http://ff14.game.naver.com/community/freecompany?search=title&keyword={keyword}')
    while len(driver.find_elements(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/table/tbody/tr/td[2]/span[1]/a/strong')): # 게시판 글 제목 부분
        driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/table/tbody/tr/td[2]/span[1]/a/strong').click() # 게시판 글 제목 부분
        driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/div[2]/input[1]').click() # 삭제 버튼
        Alert(driver).accept() # 정말 삭제하시겠습니까?
        Alert(driver).accept() # 삭제되었습니다.
        driver.get(f'http://ff14.game.naver.com/community/freecompany?search=title&keyword={keyword}')

# 네이버 홍보 글 쓰기
def naver_write(driver, title, image_path, content):
    driver.get('http://ff14.game.naver.com/community/freecompany')
    driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/div[2]/input').click() # 글 쓰기 버튼
    driver.find_element(By.ID, 'Title').send_keys(title) # 글 쓰기 제목 입력
    driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/form/div[3]/div[2]/div/input[1]').click() # 이미지 첨부 버튼
    driver.find_element(By.ID, 'imgFile').send_keys(image_path) # 이미지 주소 첨부 (찾아보기)
    driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[3]/div/div/div[3]/input[1]').click() # 확인 버튼 (이미지 업로드)
    driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe')) # 글 쓰기 에디터 iframe으로 전환
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/ul[3]/li[2]/button').click() # 가운데 정렬
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/ul[1]/li[2]/button').click() # 글자 크기
    driver.find_element(By.XPATH, '/html/body/div/div/div[1]/div/ul[1]/li[2]/div/div/ul/li[9]/button').click() # 글자 크기 (24pt)
    driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe')) # 글 쓰기 입력 iframe으로 전환
    driver.find_element(By.XPATH, '/html/body').send_keys('\n' + content) # 글 쓰기 입력
    driver.switch_to.default_content() # iframe 나와서 기본 컨텐츠
    driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/div[2]/div/input[1]').click() # 확인 버튼 (글 쓰기)

# 네이버 종합 함수
def naver_do(driver, id, pw, keyword, title, image_path, content):
    if not naver_isontop(driver, keyword):
        try: naver_login(driver, id, pw)
        except Exception as e: print(e)
        try:
            naver_delete(driver, keyword)
            naver_write(driver, title, image_path, content)
        except Exception as e: print(e)


########################################################################################## 인벤 ##########################################################################################
# 인벤 홍보글 맨 위에 있는지 확인 (최신화 확인)
def inven_isontop(driver, keyword):
    driver.get('https://www.inven.co.kr/board/ff14/4468')
    return keyword in driver.find_element(By.CLASS_NAME, 'subject-link').text

# 인벤 로그인
def inven_login(driver, id, pw, keyword):
    driver.get(f'https://www.inven.co.kr/board/ff14/4468?query=list&p=1&sterm=&name=subject&keyword={keyword}')
    driver.find_element(By.CLASS_NAME, 'login-btn').click()
    driver.find_element(By.ID, 'user_id').send_keys(id) # 아이디 입력
    driver.find_element(By.ID, 'password').send_keys(pw) # 비밀번호 입력
    driver.find_element(By.ID, 'loginBtn').click() # 로그인 버튼
    try: driver.find_element(By.ID, 'btn-extend').click() # 비밀번호 변경 '다음에 변경하기' 버튼
    except Exception as e: print(e)

# 인벤 keyword가 들어간 모든 홍보글 삭제
def inven_delete(driver, keyword):
    driver.get(f'https://www.inven.co.kr/board/ff14/4468?query=list&p=1&sterm=&name=subject&keyword={keyword}')
    while len(driver.find_elements(By.CLASS_NAME, 'subject-link')): # 게시판 글 제목 부분
        driver.find_element(By.CLASS_NAME, 'subject-link').click() # 게시판 글 제목 부분
        driver.find_element(By.CSS_SELECTOR, 'div.articleTopMenu > span > a:nth-child(2)').click() # 삭제 버튼
        Alert(driver).accept() # 삭제하시겠습니까?
        driver.get(f'https://www.inven.co.kr/board/ff14/4468?query=list&p=1&sterm=&name=subject&keyword={keyword}')

# 인벤 홍보 글 & 댓글 쓰기
def inven_write(driver, title, server, content, keyword, comment):
    # 글 쓰기
    driver.get('https://www.inven.co.kr/board/ff14/4468')
    driver.find_element(By.CSS_SELECTOR, 'a.btn.dark.write').click() # 글 쓰기 버튼
    driver.find_element(By.NAME, 'SUBJECT').send_keys(title) # 글 쓰기 제목 입력
    Select(driver.find_element(By.NAME, 'CATEGORY')).select_by_value(server) # 글 카테고리 (서버) 선택
    driver.find_elements(By.NAME, 'HTML')[1].click() # html 쓰기로 전환
    driver.find_element(By.NAME, 'CONTENT').send_keys(content) # 글 쓰기 입력
    driver.find_element(By.ID, 'bttnComplete1').click() # 작성 완료 버튼 (글 쓰기)

    # 댓글 쓰기
    driver.get(f'https://www.inven.co.kr/board/ff14/4468?query=list&p=1&sterm=&name=subject&keyword={keyword}')
    driver.find_element(By.CLASS_NAME, 'subject-link').click() # 최신 홍보글 클릭
    if '(' not in driver.find_element(By.CSS_SELECTOR, 'strong[id^="cmtCount"]').text: # 댓글 (0) 인지 확인
        driver.find_element(By.ID, 'cmtComment').send_keys(comment) # 댓글 입력
        driver.find_element(By.CSS_SELECTOR, 'button[id^="bttnCmtF1"]').click() # 등록 버튼 (댓글 쓰기)

# 인벤 종합 함수
def inven_do(driver, id, pw, keyword, title, server, content, comment):
    if not inven_isontop(driver, keyword):
        try: inven_login(driver, id, pw, keyword)
        except Exception as e: print(e)
        try:
            inven_delete(driver, keyword)
            inven_write(driver, title, server, content, keyword, comment)
        except Exception as e: print(e)


########################################################################################## 메인 ##########################################################################################
# naver 관련 github action secret
naver_id = os.environ['NAVERID']
naver_pw = os.environ['NAVERPW']
naver_keyword = os.environ['KEYWORD']
naver_title = os.environ['NAVERTITLE']
naver_image_path = str(Path.cwd()/Path(os.environ['IMAGEPATH']).resolve()) # 절대 경로로 변경
naver_content = os.environ['NAVERCONTENT']

# inven 관련 github action secret
inven_id = os.environ['INVENID']
inven_pw = os.environ['INVENPW']
inven_keyword = os.environ['KEYWORD']
inven_title = os.environ['INVENTITLE']
inven_server = os.environ['SERVER']
inven_content = os.environ['INVENCONTENT']
inven_comment = os.environ['COMMENT']

# setting 관련 github action secret
wait_time = int(os.environ['WAIT'])

# selenium 쿠키 / 캐쉬파일 경로 변수
datadir = str(Path(Path.cwd(), 'chrometemp'))

# selenium 쿠키 / 캐쉬파일 삭제
try:
    shutil.rmtree(datadir)
except FileNotFoundError:
    pass

# selenium 구동
print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Selenium 실행 중..')
if platform.system() == "Windows": # 윈도우 플랫폼
    try:
        sp = subprocess.Popen(['C:\Program Files (x86)\Google\Chrome\Application\chrome.exe', '--remote-debugging-port=9222', '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--disable-infobars', '--disable-extentions', '--disable-dev-shm-usage', '--no-sandbox', '--blink-settings=imagesEnabled=false', '--log-level=3', '--user-data-dir=' + datadir]) # 디버거 크롬 구동
    except FileNotFoundError:
        sp = subprocess.Popen(['C:\Program Files\Google\Chrome\Application\chrome.exe', '--remote-debugging-port=9222', '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--disable-infobars', '--disable-extentions', '--disable-dev-shm-usage', '--no-sandbox', '--blink-settings=imagesEnabled=false', '--log-level=3', '--user-data-dir=' + datadir]) # 디버거 크롬 구동

elif platform.system() == "Linux": # 리눅스 플랫폼
    display = Display(visible=0, size=(800, 600))
    display.start()
    sp = subprocess.Popen(['/usr/bin/google-chrome-stable', '--remote-debugging-port=9222', '--no-first-run', '--no-default-browser-check', '--disable-gpu', '--disable-infobars', '--disable-extentions', '--disable-dev-shm-usage', '--no-sandbox', '--blink-settings=imagesEnabled=false', '--log-level=3', '--user-data-dir=' + datadir]) # 디버거 크롬 구동

option = Options()
option.add_argument("--ignore-certificate-error")
option.add_argument("--ignore-ssl-errors")
option.add_argument("--ignore-certificate-errors-spki-list")
option.add_argument("--log-level=3")
option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

# implicitly_wait가 필요하면 추가
driver.implicitly_wait(wait_time)

success = True
print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 홍보글 게시 시작')
try:
    naver_do(driver, naver_id, naver_pw, naver_keyword, naver_title, naver_image_path, naver_content)
except:
    success = False
try:
    inven_do(driver, inven_id, inven_pw, inven_keyword, inven_title, inven_server, inven_content, inven_comment)
except:
    success = False

if success:
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 홍보글 게시 성공')
else:
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 홍보글 게시 실패')

driver.quit()
sp.terminate()
if platform.system() == "Linux": # 리눅스 플랫폼
    display.stop()
print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 안전 종료')
