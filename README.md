# 1. 팀 소개
| 박연정 | 박지현 | 여해준 | 이상민 | 이채림 |
|:--:|:--:|:--:|:--:|:--:|
| <img src="./assets/team/햄버거(연정).jpg" width="90" /> | <img src="./assets/team/히터(지현).jpg" width="90" /> | <img src="./assets/team/좀비(해준).jpg" width="90" /> | <img src="./assets/team/택시(상민).jpg" width="90" /> | <img src="./assets/team/초코(채림).jpg" width="90" /> |
| `@yeony-park` | `@qkrwlgus89` | `@inoocap-ux` | `@Sangmin630` | `@chaechae18` |
| 담당 업무 요약 | 담당 업무 요약 | 담당 업무 요약 | 담당 업무 요약 | 담당 업무 요약 |

---

# 2. 프로젝트 기간

- **2026.01.16 ~ 2026.01.19**

# 3. 프로젝트 개요

## 📕 프로젝트명

## ✅ 프로젝트 배경 및 목적

## 🖐️ 프로젝트 소개

## 👤 대상 사용자

# 4. 프로젝트 설계
## 4.1 프로젝트 디렉토리 구조

```text
sk25-1st-5team/
├── .env                     # 로컬 환경변수 파일 (gitignore로 관리)
├── .gitignore               
├── app.py                   
├── README.md                
├── requirements.txt         
├── util.py                  # DB 데이터 조회/로딩 함수 모음
├── .streamlit/              # Streamlit 설정
│   └── config.toml
├── assets/                  # README/문서용 리소스
│   ├── docs/                # ERD, 화면설계서, 기능정의서 등 문서 이미지
│   │   └── erd.png
│   ├── screenshots/         # 실행 화면 캡처
│   └── team/                # 팀원 프로필 이미지
│       ├── 좀비(해준).jpg
│       ├── 초코(채림).jpg
│       ├── 택시(상민).jpg
│       ├── 햄버거(연정).jpg
│       └── 히터(지현).jpg
├── components/              # 공통 UI/레이아웃 컴포넌트
│   └── layout.py
├── data/                    # 프로젝트 데이터(CSV)
│   ├── Annual_Vehicle_Registrations.csv
│   ├── bmw_faq.csv
│   ├── chevrolet_faq.csv
│   ├── genesis_faq.csv
│   ├── hyundai_faq.csv
│   ├── kgm_faq.csv
│   ├── kia_faq.csv
│   ├── repair_shop_final.csv
│   └── total_population_2021_2025_final3.csv
├── img/
│   └── autok_logo.png       # 로고 이미지
├── pages/                   # Streamlit 페이지 모음
│   ├── faq.py
│   ├── main.py
│   ├── maintenance.py
│   ├── population.py
│   └── repair_ratio_map.py
└── src/
    ├── crawler/             # FAQ 크롤러 스크립트
    │   ├── chevorlet_crawling.py
    │   ├── genesis_faq_crawler.py
    │   └── kgm_crawling.py
    └── DB/                  # DB 테이블 생성 스크립트
        └── db_faq.py
```

## 4.2 ERD
<div align="left"> <a href="./assets/docs/erd.png"> <img src="./assets/docs/erd.png" alt="ERD" width="800" /> </a> </div>

## 4.3 테이블 요약

## 4.4 화면·기능 설계서
### Main Page
<div align="left">
  <a href="./assets/docs/ui_function_p1_main.png">
    <img src="./assets/docs/ui_function_p1_main.png" alt="Main page" width="800" />
  </a>
</div>

### Population Page
<div align="left">
  <a href="./assets/docs/ui_function_p2_population.png">
    <img src="./assets/docs/ui_function_p2_population.png" alt="Population page" width="800" />
  </a>
</div>

### Repair Ratio Map Page
<div align="left">
  <a href="./assets/docs/ui_function_p3_repair_ratio_map.png">
    <img src="./assets/docs/ui_function_p3_repair_ratio_map.png" alt="Repair ratio map page" width="800" />
  </a>
</div>

### Maintenance Page
<div align="left">
  <a href="./assets/docs/ui_function_p4_maintenance.png">
    <img src="./assets/docs/ui_function_p4_maintenance.png" alt="Maintenance page" width="800" />
  </a>
</div>

### FAQ Page
<div align="left">
  <a href="./assets/docs/ui_function_p5_faq.png">
    <img src="./assets/docs/ui_function_p5_faq.png" alt="FAQ page" width="800" />
  </a>
</div>

---

# 5. 기술 스택

---

# 6. 수행 결과

---

# 7. 한 줄 회

# 6. 수행결과

# 7. 한 줄 회고
