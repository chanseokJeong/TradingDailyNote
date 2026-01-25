# Trading Daily Note

주식 매매일지 및 일일 노트 관리 도구입니다. 두 가지 버전을 제공합니다:

| 버전 | 설명 | 접속 방법 |
|------|------|-----------|
| **Daily Notes (Web)** | 간소화된 일일 노트 (GitHub Pages) | [chanseokjeong.github.io/TradingDailyNote](https://chanseokjeong.github.io/TradingDailyNote) |
| **Stock Journal (Desktop)** | 상세 매매 기록 (Streamlit) | `streamlit run app.py` |

---

## Daily Notes (GitHub Pages 버전)

모바일/PC 어디서든 접속 가능한 간소화된 일일 노트입니다.

### 주요 기능
- **이미지 드래그앤드롭** - 차트 캡처, 뉴스 스크린샷 바로 붙여넣기
- **Ctrl+V 붙여넣기** - 클립보드 이미지 직접 업로드
- **이미지 자동 압축** - 5MB 초과 시 자동 리사이즈 (1920x1080)
- **태그 시스템** - #테마명 형태로 검색 가능
- **태그 필터링** - 태그 클릭 시 해당 노트만 필터링
- **내보내기** - CSV (엑셀), JSON 형식 지원
- **노트 삭제** - 저장된 노트 삭제 기능

### 키보드 단축키
| 단축키 | 동작 |
|--------|------|
| `Ctrl + S` | 저장 |
| `Ctrl + ←` | 이전 날짜 |
| `Ctrl + →` | 다음 날짜 |
| `Ctrl + V` | 이미지 붙여넣기 |

### 첫 사용 설정
1. [chanseokjeong.github.io/TradingDailyNote](https://chanseokjeong.github.io/TradingDailyNote) 접속
2. 설정 모달에서 Supabase URL과 anon key 입력
3. 설정은 브라우저에 저장되어 다음부터 자동 연결

---

## Stock Journal Manager (Streamlit 버전)

데스크탑에서 상세한 매매 기록을 관리합니다.

### 설치 및 실행

```bash
# 1. 라이브러리 설치
pip install -r requirements.txt

# 2. 실행
streamlit run app.py
```

### 주요 기능
- 실시간 현재가 조회 (yfinance)
- 매매 기록 상세 입력 (가격, 수량, 기분, 근거)
- 이미지 업로드
- 데이터 조회 및 필터링

---

## Supabase 설정 (필수)

두 버전 모두 Supabase를 백엔드로 사용합니다.

### 1. 프로젝트 생성
1. [supabase.com](https://supabase.com) 접속 후 무료 계정 생성
2. "New Project" 클릭하여 새 프로젝트 생성

### 2. 데이터베이스 테이블 생성
Supabase Dashboard > **SQL Editor**에서 실행:

```sql
-- Daily Notes용 테이블
CREATE TABLE IF NOT EXISTS daily_notes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    note_date DATE NOT NULL DEFAULT CURRENT_DATE,
    content TEXT,
    tags TEXT[] DEFAULT '{}',
    image_urls TEXT[] DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_daily_notes_date ON daily_notes(note_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_notes_tags ON daily_notes USING GIN(tags);
```

> Stock Journal Manager도 사용하려면 `schema.sql` 파일도 실행하세요.

### 3. Storage 버킷 설정 (이미지 업로드용)
Supabase Dashboard > **Storage**에서:
1. "New bucket" 클릭
2. Name: `trade-images`
3. Public bucket: **ON** (체크)
4. 생성

또는 SQL Editor에서:
```sql
INSERT INTO storage.buckets (id, name, public)
VALUES ('trade-images', 'trade-images', true)
ON CONFLICT (id) DO NOTHING;
```

### 4. API 키 확인
Supabase Dashboard > **Settings** > **API**:
- **Project URL**: `https://xxxxx.supabase.co`
- **anon public key**: `eyJhbGciOiJI...`

---

## 파일 구조

```
TradingDailyNote/
├── docs/                    # GitHub Pages (Daily Notes)
│   ├── index.html          # 메인 페이지
│   └── style.css           # 스타일
├── daily/                   # Flask 버전 (로컬용)
│   ├── daily_app.py        # Flask 서버
│   ├── create_daily_notes_table.sql
│   ├── templates/
│   └── static/
├── app.py                   # Streamlit 앱
├── supabase_client.py       # Supabase 클라이언트
├── schema.sql               # trades 테이블 스키마
├── requirements.txt
└── README.md
```

---

## 문제 해결

| 증상 | 해결 방법 |
|------|-----------|
| 연결 에러 | URL과 API Key 확인 |
| 테이블 없음 | SQL Editor에서 테이블 생성 스크립트 실행 |
| 이미지 업로드 실패 | Storage에서 `trade-images` 버킷 생성 확인 |
| 설정 모달이 안 뜸 | 브라우저 캐시 삭제 후 재접속 |

---

## 라이선스

MIT License
