# Stock Journal Manager (GUI Ver.)

Supabase와 Streamlit을 활용한 웹 기반 주식 매매일지 관리 도구입니다.

## 🛠 설치 및 실행 방법

### 1. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 2. Supabase 설정 (필수)

#### 2-1. Supabase 프로젝트 생성
1. [Supabase](https://supabase.com) 접속 후 무료 계정 생성
2. "New Project" 클릭하여 새 프로젝트 생성
3. 프로젝트 생성 완료까지 대기

#### 2-2. 데이터베이스 테이블 생성
1. Supabase Dashboard > **SQL Editor** 이동
2. `schema.sql` 파일 내용 복사하여 실행
3. 테이블 생성 확인

#### 2-3. API 키 확인
1. Supabase Dashboard > **Settings** > **API**
2. 다음 정보 확인:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJI...` (긴 문자열)

### 3. 실행
```bash
python -m streamlit run app.py
```
브라우저가 자동으로 열리면 사이드바에서 URL과 API Key를 입력하세요.

### 4. (선택) 환경변수 설정
매번 입력하기 번거로우면 `.env` 파일을 생성하세요:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJI...
```

## 🚀 주요 기능
- **대시보드 UI**: 깔끔한 웹 인터페이스에서 클릭 몇 번으로 기록 가능
- **실시간 데이터 조회**: 티커 입력 시 yfinance로 현재가 즉시 확인 및 괴리율 경고
- **시각적 조회**: 내가 기록한 매매일지를 표(DataFrame) 형태로 한눈에 확인
- **빠른 응답**: Supabase PostgreSQL 기반으로 Notion보다 빠른 조회/저장

## 📱 외부에서 데이터 확인하기

PC가 없을 때도 스마트폰이나 다른 기기에서 매매 기록을 확인할 수 있습니다.

### 방법 1: Supabase Dashboard (가장 간단)
1. 브라우저에서 [supabase.com](https://supabase.com) 접속 후 로그인
2. 프로젝트 선택 > **Table Editor** > `trades` 테이블 클릭
3. 필터 기능으로 원하는 날짜/종목 검색 가능

### 방법 2: REST API 직접 호출
브라우저 주소창이나 HTTP 클라이언트에서 직접 조회할 수 있습니다.

**오늘 매매 기록 조회:**
```
https://[PROJECT_ID].supabase.co/rest/v1/trades?trade_date=gte.2025-01-25&apikey=[ANON_KEY]
```

**특정 종목 조회 (예: TSLA):**
```
https://[PROJECT_ID].supabase.co/rest/v1/trades?ticker=eq.TSLA&order=trade_date.desc&apikey=[ANON_KEY]
```

**최근 10개 기록:**
```
https://[PROJECT_ID].supabase.co/rest/v1/trades?order=trade_date.desc&limit=10&apikey=[ANON_KEY]
```

> `[PROJECT_ID]`와 `[ANON_KEY]`는 Supabase Dashboard > Settings > API에서 확인

### 방법 3: iOS 단축어 / Android Tasker
REST API를 활용하여 자동화 앱에서 조회 가능합니다.

**iOS 단축어 예시:**
1. 단축어 앱 > 새 단축어 생성
2. "URL 내용 가져오기" 액션 추가
3. URL에 위 REST API 주소 입력
4. "사전에서 값 가져오기"로 원하는 필드 추출

### 방법 4: Google Sheets 연동
Supabase 데이터를 Google Sheets로 자동 동기화할 수 있습니다.

1. Google Sheets에서 Apps Script 열기
2. 아래 코드로 데이터 가져오기:
```javascript
function fetchTrades() {
  const url = 'https://[PROJECT_ID].supabase.co/rest/v1/trades?order=trade_date.desc&limit=100';
  const options = {
    headers: {
      'apikey': '[ANON_KEY]',
      'Authorization': 'Bearer [ANON_KEY]'
    }
  };
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());

  // 시트에 데이터 쓰기
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.clear();
  sheet.appendRow(['Date', 'Type', 'Ticker', 'Name', 'Price', 'Qty', 'Mood', 'Reason']);
  data.forEach(row => {
    sheet.appendRow([
      row.trade_date, row.trade_type, row.ticker,
      row.stock_name, row.price, row.quantity,
      row.mood, row.reason
    ]);
  });
}
```

## ⚠️ 문제 해결
- **연결 에러**: URL과 API Key가 올바른지 확인
- **테이블 없음 에러**: `schema.sql`을 SQL Editor에서 실행했는지 확인
- **권한 에러**: anon key 대신 service_role key 사용 시도 (주의: 보안상 anon 권장)
- **이미지 업로드 실패**: Storage 버킷(`trade-images`)이 생성되어 있는지 확인
