from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os 

url = 'https://www.bmw.co.kr/ko/more-bmw/customer-support.html#accordion-4f704c5ddd-item-f8b73cd448'
source_code = requests.get(url).text

html = BeautifulSoup(source_code, "html.parser")

# 1. 질문과 답변 요소 다시 가져오기
q_elements = html.select(".cmp-accordion__title")
a_elements = html.select(".cmp-text__paragraph")

# 2. 텍스트 추출
questions = [q.get_text().strip() for q in q_elements]
all_answers = [a.get_text().strip() for a in a_elements]

# 3.답변 리스트 교정
# 앞의 2개(온라인 구매 안내, AI 어시스턴트 문구)를 제거하고
# 3번째(인덱스 2번)부터 가져오기
corrected_answers = all_answers[2:]

# 4. 데이터프레임 생성 (질문 개수에 맞춰 답변 매칭)
faq_list = []
for i in range(len(questions)):
    # 인덱스 에러 방지를 위해 답변이 존재할 때만 매칭
    ans = corrected_answers[i] if i < len(corrected_answers) else ""
    faq_list.append({
        "질문": questions[i],
        "답변": ans
    })

df = pd.DataFrame(faq_list)

#5. dic 형태로 변환
new_data = []

for index, row in df.iterrows():
    faq_dict = {row['질문']: row['답변']}
    
    new_data.append({
        '기업': 'bmw',
        'f&q': faq_dict
    })

new_df = pd.DataFrame(new_data)

# 6. csv파일로 저장
output_filename = 'bmw f&q.csv'

new_df.to_csv(output_filename, index=False, encoding='utf-8-sig')