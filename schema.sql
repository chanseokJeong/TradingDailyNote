-- Supabase SQL Editor에서 실행하세요
-- trades 테이블 생성 (재실행 가능)

CREATE TABLE IF NOT EXISTS trades (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 기본 정보
    stock_name TEXT NOT NULL,           -- 종목명
    ticker TEXT NOT NULL,               -- 티커 (예: 005930.KS, TSLA)
    trade_date TIMESTAMP WITH TIME ZONE NOT NULL,  -- 매매일자
    trade_type TEXT NOT NULL,           -- 구분 (매수/매도/일일요약)

    -- 거래 정보
    price NUMERIC DEFAULT 0,            -- 단가
    quantity NUMERIC DEFAULT 0,         -- 수량

    -- 메타 정보
    mood TEXT,                          -- 나의 기분
    reason TEXT,                        -- 매매 근거
    themes TEXT[] DEFAULT '{}',         -- 테마/이슈 (배열)
    image_url TEXT                      -- 이미지 URL
);

-- 인덱스 생성 (검색 성능 향상, 재실행 가능)
CREATE INDEX IF NOT EXISTS idx_trades_ticker ON trades(ticker);
CREATE INDEX IF NOT EXISTS idx_trades_trade_date ON trades(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_stock_name ON trades(stock_name);

-- RLS (Row Level Security) 활성화
-- 필요시 주석 해제
-- ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기/쓰기 가능하도록 설정 (개인 프로젝트용)
-- 필요시 주석 해제
-- CREATE POLICY "Enable all access" ON trades FOR ALL USING (true);

COMMENT ON TABLE trades IS '주식 매매 일지 테이블';
COMMENT ON COLUMN trades.ticker IS 'DAILY_NOTE는 일일 요약을 의미함';

-- ============================================
-- Storage 버킷 설정 (이미지 업로드용)
-- ============================================

-- 버킷 생성
INSERT INTO storage.buckets (id, name, public)
VALUES ('trade-images', 'trade-images', true)
ON CONFLICT (id) DO NOTHING;

-- 정책 재정의 (재실행 가능하도록 기존 정책 정리)
DROP POLICY IF EXISTS "Public read access" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated upload access" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated delete access" ON storage.objects;
DROP POLICY IF EXISTS "Anon upload access" ON storage.objects;
DROP POLICY IF EXISTS "Anon delete access" ON storage.objects;

-- 공개 읽기 정책 (누구나 이미지 조회 가능)
CREATE POLICY "Public read access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'trade-images');

-- anon 키 기반 웹앱 업로드/삭제 허용
CREATE POLICY "Anon upload access"
ON storage.objects FOR INSERT
TO anon
WITH CHECK (bucket_id = 'trade-images');

CREATE POLICY "Anon delete access"
ON storage.objects FOR DELETE
TO anon
USING (bucket_id = 'trade-images');

-- 로그인 사용자 업로드/삭제 허용
CREATE POLICY "Authenticated upload access"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'trade-images');

CREATE POLICY "Authenticated delete access"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'trade-images');
