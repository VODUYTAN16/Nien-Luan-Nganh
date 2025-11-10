# ml/search_engine.py
from typing import List


class SearchEngine:
    def __init__(self):
        # TODO: load model + index thật
        self.ready = True

    def search_by_text(self, model_code: str, query: str, top_k: int = 20) -> List[str]:
        if not query:
            return []
        # Trả về danh sách base_name
        return ["coaster_001", "coaster_002", "coaster_003"][:top_k]

    def search_by_image_bytes(self, model_code: str, data: bytes, top_k: int = 20) -> List[str]:
        if not data:
            return []
        return ["coaster_002", "coaster_010", "coaster_005"][:top_k]


search_engine = SearchEngine()
