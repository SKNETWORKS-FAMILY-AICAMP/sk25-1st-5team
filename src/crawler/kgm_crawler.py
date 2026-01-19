import time
import re
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 기본세팅
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)

URL = "https://www.kg-mobility.com/sr/online-center/faq/detail?searchWord=&categoryCd=304"
driver.get(URL)

wait = WebDriverWait(driver, 15)


#로딩 대기
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.accordion-item")
    )
)


# 페이지 번호 가져옴
def get_current_page():
    btn = driver.find_element(
        By.XPATH,
        "//ul[contains(@class,'pagnation')]//button[contains(@class,'active')]"
    )
    return int(btn.text.strip())

# 페이지 번호 클릭
def go_to_page_number(page_num):
    buttons = driver.find_elements(
        By.XPATH,
        "//ul[contains(@class,'pagnation')]//button[normalize-space(text())!='']"
    )

    for b in buttons:
        if b.text.strip() == str(page_num):
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", b
            )
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", b)
            time.sleep(1.5)  # Vue 렌더링 대기
            return True

    return False


#다음페이지 (6페이지때문)
def click_page_group_next():
    try:
        btn = driver.find_element(
            By.XPATH,
            "//button[normalize-space()='다음 페이지' and not(contains(@style,'display: none'))]"
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn
        )
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)
        return True
    except:
        return False


# faq 열기
def open_all_kgm_faq():
    buttons = driver.find_elements(
        By.CSS_SELECTOR, "div.accordion-header button"
    )

    for btn in buttons:
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
            time.sleep(0.15)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.15)
        except:
            pass


# 크롤링
def scrape_kgm_faq():
    faq_dict = {}

    items = driver.find_elements(
        By.CSS_SELECTOR, "div.accordion-item"
    )

    for item in items:
        try:
            question = item.find_element(
                By.CSS_SELECTOR, "div.accordion-header p:last-child"
            ).text.strip()

            btn = item.find_element(
                By.CSS_SELECTOR, "div.accordion-header button"
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", btn)

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.accordion-item.active div.accordion-body")
                )
            )

            answer = item.find_element(
                By.CSS_SELECTOR, "div.accordion-body"
            ).text

            answer = re.sub(r"\s+", " ", answer).strip()

            if question in faq_dict:
                question = f"{question} (중복)"

            faq_dict[question] = answer

        except Exception as e:
            print("스킵:", e)

    return faq_dict


#전체 크롤링
company_key = "kgm"
all_faq = {company_key: {}}

visited_pages = set()

while True:
    current_page = get_current_page()

    if current_page in visited_pages:
        print("이미 방문한 페이지, 종료")
        break

    print(f" {current_page} 페이지 수집 중")
    visited_pages.add(current_page)

    open_all_kgm_faq()
    page_faq = scrape_kgm_faq()
    all_faq[company_key].update(page_faq)

    next_page = current_page + 1

    # 다음 숫자 페이지 시도
    if go_to_page_number(next_page):
        continue

    # 없으면 페이지 묶음 이동
    if click_page_group_next():
        continue

    print("마지막 페이지 ")
    break


#저장
rows = []

for question, answer in all_faq[company_key].items():
    rows.append({
        "company_name": "KGM",
        "faq_pairs": {question: answer}
    })

df = pd.DataFrame(rows)

os.makedirs("./skn_data", exist_ok=True)
df.to_csv("./skn_data/kgm_faq.csv", index=False, encoding="utf-8-sig")



driver.quit()

