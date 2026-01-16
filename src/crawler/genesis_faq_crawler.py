from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import pandas as pd
import time
import tqdm

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://www.genesis.com/kr/ko/support/faq.html?anchorID=faq_tab")

faq_items = driver.find_elements(By.CLASS_NAME, "cp-faq__accordion-item")
faq_list = []

for item in faq_items:
    #질문 카테고리 및 질문 추출
    label = item.find_element(By.CLASS_NAME, "accordion-label").text.strip()
    q = item.find_element(By.CLASS_NAME, "accordion-title").text.strip()

    #답변 추출을 위해 클릭 후 스크롤해서 요소가 보이도록 함
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
    time.sleep(0.5)  # 스크롤 후 안정화 대기
    
    item.click()
    time.sleep(0.3)  # 에러방지용 딜레이
    
    a = item.find_element(By.CLASS_NAME, "accordion-panel-inner").text.strip()
    faq_list.append({
        "category": label,
        "question": q,
        "answer": a})
    
    tqdm.tqdm.write(f"Scraped FAQ: {label} - {q}")
    
driver.quit()

df = pd.DataFrame(faq_list)

# 정비 관련 필요한 카테고리만 필터링
df_filtered = df[df['category'].isin(['[정비예약]', '[빌트인 캠]'])].reset_index(drop=True)

# 필요한 형태로 변환
genesis_df = pd.DataFrame({
    'company_name': 'Genesis',
    'faq_pairs': df_filtered.apply(lambda row: {row['question']: row['answer']}, axis=1)
})

genesis_df.to_csv('genesis_faq.csv', index=False)