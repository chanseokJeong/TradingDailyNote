from supabase import create_client, Client
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class SupabaseClient:
    """
    Supabase와의 통신을 담당하는 클라이언트 클래스입니다.
    CRUD 및 이미지 업로드 기능을 제공합니다.
    """

    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.client: Client = create_client(url, key)
        self.table_name = "trades"
        self.bucket_name = "trade-images"

    def create_trade(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        새로운 매매 기록을 생성합니다.

        Args:
            data: 매매 기록 데이터
                - stock_name: 종목명
                - ticker: 티커
                - trade_date: 매매일자 (ISO format)
                - trade_type: 구분 (매수/매도)
                - price: 단가
                - quantity: 수량
                - mood: 나의 기분
                - reason: 매매 근거
                - themes: 테마/이슈 (리스트)
                - image_url: 이미지 URL (선택)
        """
        response = self.client.table(self.table_name).insert(data).execute()

        if not response.data:
            raise Exception(f"레코드 생성 실패")

        return response.data[0]

    def query_trades(
        self,
        search_keyword: Optional[str] = None,
        order_by: str = "trade_date",
        ascending: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        매매 기록을 조회합니다.

        Args:
            search_keyword: 검색어 (티커 또는 종목명)
            order_by: 정렬 기준 컬럼
            ascending: 오름차순 여부
            limit: 최대 조회 개수
        """
        query = self.client.table(self.table_name).select("*")

        if search_keyword:
            # 티커 또는 종목명으로 검색
            query = query.or_(
                f"ticker.ilike.%{search_keyword}%,stock_name.ilike.%{search_keyword}%"
            )

        query = query.order(order_by, desc=not ascending).limit(limit)
        response = query.execute()

        return response.data if response.data else []

    def update_trade(self, trade_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        특정 매매 기록을 업데이트합니다.

        Args:
            trade_id: 수정할 레코드의 ID
            data: 업데이트할 데이터
        """
        response = (
            self.client.table(self.table_name)
            .update(data)
            .eq("id", trade_id)
            .execute()
        )

        if not response.data:
            raise Exception(f"레코드 수정 실패")

        return response.data[0]

    def delete_trade(self, trade_id: str) -> bool:
        """
        특정 매매 기록을 삭제합니다.

        Args:
            trade_id: 삭제할 레코드의 ID
        """
        response = (
            self.client.table(self.table_name)
            .delete()
            .eq("id", trade_id)
            .execute()
        )

        return True

    def test_connection(self) -> bool:
        """
        연결 테스트를 수행합니다.
        """
        try:
            response = self.client.table(self.table_name).select("id").limit(1).execute()
            return True
        except Exception as e:
            raise Exception(f"연결 테스트 실패: {e}")

    def upload_image(self, file_data: bytes, file_name: str, content_type: str = "image/png") -> str:
        """
        이미지를 Supabase Storage에 업로드하고 공개 URL을 반환합니다.

        Args:
            file_data: 이미지 파일의 바이트 데이터
            file_name: 원본 파일명
            content_type: MIME 타입

        Returns:
            업로드된 이미지의 공개 URL
        """
        # 고유한 파일명 생성
        ext = file_name.split(".")[-1] if "." in file_name else "png"
        unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

        # Storage에 업로드
        response = self.client.storage.from_(self.bucket_name).upload(
            path=unique_name,
            file=file_data,
            file_options={"content-type": content_type}
        )

        # 공개 URL 생성
        public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_name)

        return public_url

    # ============ Daily Notes 메서드 ============

    def create_daily_note(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        새로운 일일 노트를 생성합니다.

        Args:
            data: 일일 노트 데이터
                - note_date: 노트 날짜 (YYYY-MM-DD)
                - content: 메모 내용
                - tags: 태그 배열 (선택)
                - image_urls: 이미지 URL 배열 (선택)
        """
        response = self.client.table("daily_notes").insert(data).execute()

        if not response.data:
            raise Exception("일일 노트 생성 실패")

        return response.data[0]

    def get_daily_note_by_date(self, note_date: str) -> Optional[Dict[str, Any]]:
        """
        특정 날짜의 일일 노트를 조회합니다.

        Args:
            note_date: 조회할 날짜 (YYYY-MM-DD)
        """
        response = (
            self.client.table("daily_notes")
            .select("*")
            .eq("note_date", note_date)
            .execute()
        )

        return response.data[0] if response.data else None

    def update_daily_note(self, note_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        특정 일일 노트를 업데이트합니다.

        Args:
            note_id: 수정할 노트의 ID
            data: 업데이트할 데이터
        """
        response = (
            self.client.table("daily_notes")
            .update(data)
            .eq("id", note_id)
            .execute()
        )

        if not response.data:
            raise Exception("일일 노트 수정 실패")

        return response.data[0]

    def query_daily_notes(
        self,
        search_tag: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        일일 노트를 조회합니다.

        Args:
            search_tag: 검색할 태그
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            limit: 최대 조회 개수
        """
        query = self.client.table("daily_notes").select("*")

        if search_tag:
            query = query.contains("tags", [search_tag])

        if start_date:
            query = query.gte("note_date", start_date)

        if end_date:
            query = query.lte("note_date", end_date)

        query = query.order("note_date", desc=True).limit(limit)
        response = query.execute()

        return response.data if response.data else []

    def delete_daily_note(self, note_id: str) -> bool:
        """
        특정 일일 노트를 삭제합니다.

        Args:
            note_id: 삭제할 노트의 ID
        """
        self.client.table("daily_notes").delete().eq("id", note_id).execute()
        return True
