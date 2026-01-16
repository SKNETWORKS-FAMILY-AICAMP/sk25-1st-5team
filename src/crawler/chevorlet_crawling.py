import time
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm   


# 기본 세팅
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)

URL = "https://www.chevrolet.co.kr/faq/product-maintenance"
driver.get(URL)
time.sleep(2)


# FAQ 버튼 
def open_all_faq_buttons(driver):
    buttons = driver.find_elements(By.CSS_SELECTOR, "gb-expander .gb-expander-btn")
    print("FAQ 버튼 개수:", len(buttons))

    for i, btn in enumerate(tqdm(buttons, desc="FAQ 버튼 여는 중")): 
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
            time.sleep(0.3)

            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.5)

            print(f"{i + 1}번 열림")
        except Exception as e:
            print(f"{i + 1}번 실패:", e)


open_all_faq_buttons(driver)


# 수집 및 문자 제거 ([차량관리])
def scrape_faq(driver, company_name: str):
    faqs = driver.find_elements(By.CSS_SELECTOR, "gb-expander")
    faq_dict = {}

    for faq in tqdm(faqs, desc="FAQ 수집 중"): 
        try:
            # 질문
            question = faq.find_element(By.CSS_SELECTOR, "h6").text.strip()
            question = re.sub(r"^\[.*?\]\s*", "", question) 

            # 답변
            answer = faq.find_element(
                By.CSS_SELECTOR, ".gb-expander-content-body"
            ).text.strip()

            if not question or not answer:
                continue

            # 질문 중복 방지
            key = question
            if key in faq_dict:
                key = f"{question} (중복)"

            faq_dict[key] = answer

        except Exception as e:
            print("스킵:", e)

    return faq_dict


company = "chevrolet"
all_faq = {
    company: scrape_faq(driver, company)
}


#저장
rows = []

company = "Chevrolet"

for question, answer in all_faq[company.lower()].items():
    rows.append({
        "company_name": company,
        "faq_pairs": {question: answer}
    })

chevrolet_df = pd.DataFrame(rows)

chevrolet_df.to_csv("./skn_data/chevrolet_faq.csv", index=False, encoding="utf-8-sig")


driver.quit()