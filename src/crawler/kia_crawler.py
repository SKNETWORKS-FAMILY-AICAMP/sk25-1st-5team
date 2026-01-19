import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# 기본 세팅
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)

URL = "https://www.kia.com/kr/customer-service/center/faq#none"
driver.get(URL)

wait = WebDriverWait(driver, 15)


# 카테고리 선택 (차량정비) - 모바일/PC 분기
def select_maintenance_category():
    try:
        drop_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dic-tab__mo-list"))
        )
        driver.execute_script("arguments[0].click();", drop_btn)
        time.sleep(0.5)

        maint_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[self::button or self::a][contains(normalize-space(),'차량') and contains(normalize-space(),'정비')]"
            ))
        )
        driver.execute_script("arguments[0].click();", maint_btn)
        time.sleep(1.2)
        return "mobile"

    except TimeoutException:
        pass

    # PC 탭/필터 방식
    try:
        maint_btn_pc = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[self::button or self::a][contains(normalize-space(),'차량정비') or (contains(normalize-space(),'차량') and contains(normalize-space(),'정비'))]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", maint_btn_pc)
        time.sleep(0.2)
        driver.execute_script("arguments[0].click();", maint_btn_pc)
        time.sleep(1.2)
        return "pc"

    except TimeoutException:
        raise RuntimeError("차량정비 카테고리 버튼을 찾지 못했습니다. (셀렉터 변경 가능)")


ui_mode = select_maintenance_category()

# FAQ 로딩 대기
wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cmp-accordion__item"))
)


# 페이지 번호 클릭 (있으면) / 다음 묶음 이동
def click_page_num(page_num: int) -> bool:
    xpath = (
        "//*[contains(@class,'paging') or contains(@class,'paging-list') or contains(@class,'pagination')]"
        f"//*[self::a or self::button][normalize-space()='{page_num}']"
    )
    targets = driver.find_elements(By.XPATH, xpath)
    if not targets:
        return False

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", targets[0])
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", targets[0])
    time.sleep(1.5)
    return True


def click_page_group_next() -> bool:
    next_btns = driver.find_elements(By.CSS_SELECTOR, "button.pagigation-btn-next, button.pagination-btn-next")
    if not next_btns:
        return False

    btn = next_btns[0]
    # 비활성 체크
    if btn.get_attribute("disabled") is not None or btn.get_attribute("aria-disabled") == "true":
        return False

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1.5)
    return True


def go_to_page_number(page_num: int) -> bool:
    # 현재 화면에 page_num이 있으면 클릭, 없으면 다음 묶음으로 넘겨서 다시 시도
    for _ in range(25):
        if click_page_num(page_num):
            return True
        if not click_page_group_next():
            return False
    return False


# FAQ 열기 (현재 페이지 전체)
def open_all_kia_faq():
    buttons = driver.find_elements(By.CSS_SELECTOR, "button.cmp-accordion__button")
    for btn in buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.15)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.15)
        except:
            pass


# 크롤링 (현재 페이지)
def scrape_kia_faq():
    faq_dict = {}

    items = driver.find_elements(By.CSS_SELECTOR, "div.cmp-accordion__item")
    for item in items:
        try:
            btn = item.find_element(By.CSS_SELECTOR, "button.cmp-accordion__button")
            question = item.find_element(By.CSS_SELECTOR, "span.cmp-accordion__title").text.strip()

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", btn)

            panel_id = btn.get_attribute("aria-controls")
            answer = ""
            if panel_id:
                # 답변 패널 텍스트 가져오기
                answer = driver.find_element(By.ID, panel_id).text.strip()

            if question in faq_dict:
                question = f"{question} (중복)"

            faq_dict[question] = answer

        except Exception as e:
            print("스킵:", e)

    return faq_dict


# 전체 크롤링
company_key = "kia"
all_faq = {company_key: {}}

visited_pages = set()
MAX_PAGE = 16

# 1페이지 먼저 수집
current_page = 1
print(f"{current_page} 페이지 수집 중")
visited_pages.add(current_page)

open_all_kia_faq()
page_faq = scrape_kia_faq()
all_faq[company_key].update(page_faq)

# 2~MAX_PAGE
for p in range(2, MAX_PAGE + 1):
    if not go_to_page_number(p):
        print(f"{p} 페이지로 이동 실패. 마지막 페이지로 판단하고 종료")
        break

    # 페이지 로딩 대기
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cmp-accordion__item")))

    print(f"{p} 페이지 수집 중")
    visited_pages.add(p)

    open_all_kia_faq()
    page_faq = scrape_kia_faq()
    all_faq[company_key].update(page_faq)


# 저장
rows = []
for question, answer in all_faq[company_key].items():
    rows.append({
        "company_name": "KIA",
        "faq_pairs": {question: answer}
    })

df = pd.DataFrame(rows)

os.makedirs("./skn_data", exist_ok=True)
df.to_csv("./skn_data/kgm_faq.csv", index=False, encoding="utf-8-sig")


driver.quit()
