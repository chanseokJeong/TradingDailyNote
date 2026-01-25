import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
from supabase_client import SupabaseClient
import os
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="Stock Journal Manager",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS 스타일링 (다크 테마 및 깔끔한 디자인) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 상태 관리 ---
if 'supabase_client' not in st.session_state:
    st.session_state.supabase_client = None

# --- Helper Functions ---
def get_env_path():
    """현재 스크립트와 같은 폴더의 .env 경로 반환"""
    return Path(__file__).parent / ".env"

def load_env_file():
    """기존 .env 파일 내용을 딕셔너리로 로드"""
    env_path = get_env_path()
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def save_env_file(url: str, key: str):
    """설정값을 .env 파일에 저장"""
    env_path = get_env_path()

    # 기존 환경변수 로드 (다른 설정 유지)
    env_vars = load_env_file()

    # Supabase 설정 업데이트
    env_vars["SUPABASE_URL"] = url
    env_vars["SUPABASE_KEY"] = key

    # 파일에 저장
    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    return True

def init_connection(url, key):
    try:
        client = SupabaseClient(url, key)
        client.test_connection()
        st.session_state.supabase_client = client
        st.success("✅ Supabase 연결 성공!")
        return True
    except Exception as e:
        st.error("❌ 연결 실패")
        st.error(f"내용: {e}")
        st.warning("""
        👉 **자주 발생하는 원인:**
        1. **잘못된 URL**: Supabase 프로젝트 URL 확인 (예: https://xxxxx.supabase.co)
        2. **잘못된 API Key**: Settings > API에서 `anon` 또는 `service_role` 키 확인
        3. **테이블 미생성**: `trades` 테이블이 생성되어 있는지 확인
        """)
        return False

def fetch_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.fast_info.last_price
    except:
        return None

# --- .env 파일에서 기본값 로드 ---
env_vars = load_env_file()
default_url = env_vars.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
default_key = env_vars.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

# --- Sidebar: 설정 ---
with st.sidebar:
    st.title("⚙️ 설정 (Settings)")

    supabase_url = st.text_input("Supabase URL", value=default_url, placeholder="https://xxxxx.supabase.co")
    supabase_key = st.text_input("Supabase API Key", value=default_key, type="password")

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("연결 확인"):
            if supabase_url and supabase_key:
                init_connection(supabase_url, supabase_key)
            else:
                st.warning("URL과 API Key를 모두 입력해주세요.")

    with col_btn2:
        if st.button("설정 저장"):
            if supabase_url and supabase_key:
                try:
                    save_env_file(supabase_url, supabase_key)
                    st.success("✅ .env 저장 완료!")
                except Exception as e:
                    st.error(f"저장 실패: {e}")
            else:
                st.warning("URL과 API Key를 입력해주세요.")

    st.markdown("---")
    st.info("💡 Supabase Dashboard > Settings > API 에서 URL과 anon key를 확인하세요.")

# --- Main Interface ---
st.title("📈 Stock Journal Manager")

if not st.session_state.supabase_client:
    st.warning("👈 왼쪽 사이드바에서 Supabase 설정을 먼저 완료해주세요.")
    st.stop()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 매매 기록 (Record)", "📊 기록 조회 (View)", "🌞 일일 루틴 (Daily)"])

# === Tab 1: 매매 기록 ===
with tab1:
    st.header("새로운 매매 기록")

    col1, col2 = st.columns(2)

    with col1:
        ticker = st.text_input("티커 (Ticker)", placeholder="005930.KS, TSLA").upper()
        name = st.text_input("종목명 (Name)", placeholder="삼성전자")

        # 티커 입력 시 현재가 자동 조회
        current_price = 0.0
        if ticker:
            cp = fetch_current_price(ticker)
            if cp:
                st.info(f"📍 '{ticker}' 현재가: {cp:,.2f}")
                current_price = cp
            else:
                st.caption("⚠️ 현재가 조회 실패 혹은 잘못된 티커")

    with col2:
        trade_type = st.selectbox("구분", ["매수", "매도"])
        date = st.date_input("매매일자", datetime.date.today())
        time_val = st.time_input("시간", datetime.datetime.now().time())

    col3, col4 = st.columns(2)
    with col3:
        price = st.number_input("단가 (Price)", min_value=0.0, step=100.0, format="%.2f")
        # 현재가와 비교 경고
        if current_price > 0 and price > 0:
            diff_pct = abs(price - current_price) / current_price * 100
            if diff_pct > 10:
                st.warning(f"⚠️ 현재가와 {diff_pct:.1f}% 차이가 납니다.")

    with col4:
        qty = st.number_input("수량 (Qty)", min_value=0.0, step=1.0)

    st.markdown("---")

    col5, col6 = st.columns(2)
    with col5:
        mood = st.selectbox("나의 기분", ["차분", "흥분", "공포", "탐욕", "지루함", "패닉"])
        issue = st.text_input("테마/이슈 (쉼표 구분)")

    with col6:
        reason = st.text_area("매매 근거 (Why?)", height=100)

    # 이미지 업로드 섹션
    st.markdown("---")
    st.subheader("📷 이미지 첨부 (Chart/News)")

    # Step 1: 이미지 선택 (Input)
    with st.container():
        st.markdown("##### 1️⃣ 이미지 선택")
        image_option = st.radio(
            "이미지 첨부 방식",
            ["업로드", "URL 입력", "없음"],
            horizontal=True,
            label_visibility="collapsed"
        )

        uploaded_file = None
        image_url = None

        if image_option == "업로드":
            uploaded_file = st.file_uploader(
                "이미지 파일 선택",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                help="차트 캡처나 뉴스 스크린샷을 업로드하세요"
            )
        elif image_option == "URL 입력":
            image_url = st.text_input("이미지 URL", placeholder="https://...")

    # Step 2: 미리보기 (Preview)
    st.markdown("##### 2️⃣ 미리보기")
    preview_container = st.container()
    
    with preview_container:
        if image_option == "업로드" and uploaded_file:
            st.image(uploaded_file, caption="업로드 이미지 미리보기", use_container_width=True)
        elif image_option == "URL 입력" and image_url:
            try:
                st.image(image_url, caption="URL 이미지 미리보기", use_container_width=True)
            except:
                st.error("이미지를 불러올 수 없습니다. URL을 확인해주세요.")
        else:
            st.info("이미지가 선택되지 않았습니다.")

    if st.button("기록 저장 (Save Trade)", use_container_width=True):
        if not ticker or price <= 0 or qty <= 0:
            st.error("종목명, 티커, 단가, 수량은 필수입니다.")
        else:
            with st.spinner("Supabase에 저장 중..."):
                try:
                    full_datetime = datetime.datetime.combine(date, time_val).isoformat()

                    # 테마를 리스트로 변환
                    themes = [i.strip() for i in issue.split(",") if i.strip()] if issue else []

                    # 이미지 처리
                    final_image_url = None
                    if image_option == "업로드" and uploaded_file:
                        # Supabase Storage에 업로드
                        file_data = uploaded_file.getvalue()
                        file_name = uploaded_file.name
                        content_type = uploaded_file.type or "image/png"
                        final_image_url = st.session_state.supabase_client.upload_image(
                            file_data, file_name, content_type
                        )
                        st.toast(f"이미지 업로드 완료!")
                    elif image_option == "URL 입력" and image_url:
                        final_image_url = image_url

                    data = {
                        "stock_name": name if name else ticker,
                        "ticker": ticker,
                        "trade_date": full_datetime,
                        "trade_type": trade_type,
                        "price": price,
                        "quantity": qty,
                        "mood": mood,
                        "reason": reason,
                        "themes": themes,
                        "image_url": final_image_url
                    }

                    st.session_state.supabase_client.create_trade(data)
                    st.success("✅ 저장 완료!")
                except Exception as e:
                    st.error(f"저장 실패: {e}")

# === Tab 2: 기록 조회 ===
with tab2:
    st.header("📋 매매 일지 조회")

    search_keyword = st.text_input("검색 (티커/종목명)", "")

    if st.button("조회 하기"):
        with st.spinner("데이터 불러오는 중..."):
            try:
                results = st.session_state.supabase_client.query_trades(
                    search_keyword=search_keyword.upper() if search_keyword else None
                )

                if not results:
                    st.info("데이터가 없습니다.")
                else:
                    # 데이터 가공
                    rows = []
                    for record in results:
                        # DAILY_NOTE는 일일 루틴이므로 제외
                        if record.get("ticker") == "DAILY_NOTE":
                            continue
                        try:
                            trade_date = record.get("trade_date", "")
                            if trade_date:
                                trade_date = trade_date[:16].replace("T", " ")

                            rows.append({
                                "Date": trade_date,
                                "Type": record.get("trade_type", ""),
                                "Ticker": record.get("ticker", ""),
                                "Name": record.get("stock_name", ""),
                                "Price": record.get("price", 0),
                                "Qty": record.get("quantity", 0),
                                "Mood": record.get("mood", ""),
                                "Reason": record.get("reason", ""),
                                "Image": record.get("image_url", "")
                            })
                        except Exception as parse_err:
                            continue

                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True)

                    # 이미지가 있는 기록 표시
                    records_with_images = [r for r in rows if r.get("Image")]
                    if records_with_images:
                        st.markdown("#### 📷 첨부 이미지")
                        for r in records_with_images[:5]:  # 최근 5개만 표시
                            with st.expander(f"{r['Date']} - {r['Ticker']} ({r['Type']})"):
                                st.image(r["Image"], use_container_width=True)

            except Exception as e:
                st.error(f"조회 중 오류: {e}")

# === Tab 3: 일일 루틴 ===
with tab3:
    st.header("🌞 Daily Routine & Summary")

    summary_date = st.date_input("날짜", datetime.date.today(), key="daily_date")
    daily_theme = st.text_input("오늘의 주도 테마", key="daily_theme")
    daily_summary = st.text_area("시장 요약 및 이슈 정리", height=200, key="daily_text")

    if st.button("일일 요약 저장"):
        if not daily_summary:
            st.warning("내용을 입력해주세요.")
        else:
            with st.spinner("저장 중..."):
                try:
                    data = {
                        "stock_name": f"Daily Summary - {summary_date}",
                        "ticker": "DAILY_NOTE",
                        "trade_date": summary_date.isoformat(),
                        "trade_type": "일일요약",
                        "price": 0,
                        "quantity": 0,
                        "mood": None,
                        "reason": daily_summary,
                        "themes": [daily_theme] if daily_theme else [],
                        "image_url": None
                    }

                    st.session_state.supabase_client.create_trade(data)
                    st.success("✅ 일일 요약 저장 완료!")
                except Exception as e:
                    st.error(f"저장 실패: {e}")
