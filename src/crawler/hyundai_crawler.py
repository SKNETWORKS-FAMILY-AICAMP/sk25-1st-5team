import time
import os
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 기본 세팅
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)

URL = "https://www.hyundai.com/kr/ko/e/customer/center/faq"
driver.get(URL)

wait = WebDriverWait(driver, 15)

# FAQ 리스트 로딩 대기 (기본 list-item 기준)
wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".list-item"))
)


# 0) 차량정비 탭 클릭 + 전체 필터 클릭
def select_repair_tab_and_all_filter():
    # 차량정비 탭 클릭(정확히)
    repair_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='차량정비']]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", repair_btn)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", repair_btn)
    time.sleep(1.5)

    # 전체 필터 클릭
    all_filter = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[normalize-space()='전체']"))
    )
    driver.execute_script("arguments[0].click();", all_filter)
    time.sleep(1.2)

    # 리스트 로딩 대기
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".list-item")))


select_repair_tab_and_all_filter()


# 페이징 유틸
def get_pager_root():
    try:
        one = driver.find_element(By.XPATH, "//*[self::a or self::button][normalize-space()='1']")
        pager = one.find_element(By.XPATH, "./ancestor::*[self::nav or self::ul or self::div][1]")
        return pager
    except:
        return driver


def get_current_page():
    pager = get_pager_root()

    # active class를 가진 버튼/링크 찾기
    active = pager.find_elements(
        By.XPATH,
        ".//*[self::a or self::button][contains(@class,'active') or contains(@aria-current,'page')]"
    )
    if active:
        txt = active[0].text.strip()
        if txt.isdigit():
            return int(txt)

    # fallback: 현재 페이지 표시가 없으면 1로 간주
    return 1


def go_to_page_number(page_num: int) -> bool:
    pager = get_pager_root()

    for _ in range(15):
        targets = pager.find_elements(
            By.XPATH,
            f".//*[self::a or self::button][normalize-space()='{page_num}']"
        )
        if targets:
            driver.execute_script("arguments[0].click();", targets[0])
            time.sleep(1.2)
            # 리스트 로딩 대기
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".list-item")))
            return True

        next_btns = pager.find_elements(
            By.XPATH,
            ".//*[self::a or self::button][normalize-space()='>' or contains(@aria-label,'다음') or contains(@aria-label,'next')]"
        )
        if next_btns:
            driver.execute_script("arguments[0].click();", next_btns[0])
            time.sleep(1.0)
            pager = get_pager_root()
        else:
            return False

    return False


# FAQ 열기 / 스크랩
def open_all_hyundai_faq():
    items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
    for i in range(len(items)):
        try:
            items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
            it = items[i]

            btns = it.find_elements(By.CSS_SELECTOR, "button.list-title")
            if not btns:
                continue

            btn = btns[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.15)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.15)
        except:
            pass


def scrape_hyundai_faq():
    faq_dict = {}

    items_count = len(driver.find_elements(By.CSS_SELECTOR, ".list-item"))
    for i in range(items_count):
        try:
            # DOM 안정성 위해 매번 재조회
            items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
            it = items[i]

            btns = it.find_elements(By.CSS_SELECTOR, "button.list-title")
            if not btns:
                continue
            btn = btns[0]

            # 질문 클릭
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.8)

            # 클릭 후 DOM 반영된 동일 index item 재조회
            it = driver.find_elements(By.CSS_SELECTOR, ".list-item")[i]

            cats = it.find_elements(By.CSS_SELECTOR, "span.list-category")
            qs = it.find_elements(By.CSS_SELECTOR, "span.list-content")

            category = cats[0].text.strip() if cats else ""
            question = qs[0].text.strip() if qs else ""

            # 답변 후보
            answer = ""
            ans_candidates = it.find_elements(By.CSS_SELECTOR, "div.list-content")
            if ans_candidates:
                answer = ans_candidates[0].text.strip()

            if not answer:
                alt = it.find_elements(By.CSS_SELECTOR, "div.contents, div.conts, div[class*='content']")
                if alt:
                    answer = alt[0].text.strip()

            # 정리
            answer = re.sub(r"\s+", " ", answer).strip()

            # 여기서는 질문만 key로 저장(기아/KGM 스타일)
            if question in faq_dict:
                question = f"{question} (중복)"

            faq_dict[question] = answer

        except Exception as e:
            print("스킵:", e)

    return faq_dict


# 전체 크롤링
company_key = "hyundai"
all_faq = {company_key: {}}
visited_pages = set()

current_page = get_current_page()

MAX_PAGE = 8

while True:
    current_page = get_current_page()

    if current_page in visited_pages:
        print("이미 방문한 페이지, 종료")
        break

    print(f"{current_page} 페이지 수집 중")
    visited_pages.add(current_page)

    open_all_hyundai_faq()
    page_faq = scrape_hyundai_faq()
    all_faq[company_key].update(page_faq)

    next_page = current_page + 1

    if next_page > MAX_PAGE:
        print("설정한 마지막 페이지 도달")
        break

    # 다음 페이지 이동 시도
    if go_to_page_number(next_page):
        continue

    print("마지막 페이지")
    break


# 저장
rows = []
for question, answer in all_faq[company_key].items():
    rows.append({
        "company_name": "현대",
        "faq_pairs": {question: answer}
    })

df = pd.DataFrame(rows)

os.makedirs("./skn_data", exist_ok=True)
df.to_csv("./skn_data/hyundai_faq.csv", index=False, encoding="utf-8-sig")

driver.quit()
