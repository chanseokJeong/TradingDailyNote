-- Daily Notes 테이블 생성 스크립트
-- Supabase SQL Editor에서 실행하세요

CREATE TABLE IF NOT EXISTS daily_notes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    note_date DATE NOT NULL DEFAULT CURRENT_DATE,
    content TEXT,                    -- 짧은 메모
    tags TEXT[] DEFAULT '{}',        -- 해시태그 배열
    image_urls TEXT[] DEFAULT '{}'   -- 이미지 URL 배열 (여러 장)
);

-- note_date에 인덱스 추가 (날짜별 조회 성능 향상)
CREATE INDEX IF NOT EXISTS idx_daily_notes_date ON daily_notes(note_date DESC);

-- tags에 GIN 인덱스 추가 (태그 검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_daily_notes_tags ON daily_notes USING GIN(tags);

-- RLS (Row Level Security) 정책 설정 (선택사항)
-- 필요한 경우 아래 주석을 해제하세요

-- ALTER TABLE daily_notes ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Enable all for authenticated users" ON daily_notes
--     FOR ALL
--     USING (true)
--     WITH CHECK (true);

-- 또는 anon 키로 모든 접근 허용
-- CREATE POLICY "Enable all for anon" ON daily_notes
--     FOR ALL
--     TO anon
--     USING (true)
--     WITH CHECK (true);

COMMENT ON TABLE daily_notes IS '간소화된 일일 주식 노트';
COMMENT ON COLUMN daily_notes.note_date IS '노트 날짜';
COMMENT ON COLUMN daily_notes.content IS '메모 내용';
COMMENT ON COLUMN daily_notes.tags IS '해시태그 배열 (예: {#반도체, #종가베팅})';
COMMENT ON COLUMN daily_notes.image_urls IS '첨부 이미지 URL 배열';
