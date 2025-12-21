"""
Gemini API Client for HanaView
google-genai ライブラリを使用した統一クライアント
"""

import os
import logging
from typing import Optional
from google import genai

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set")

        # Initialize client only if key is present to avoid immediate crash
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

        self.model = 'gemini-3-flash-preview'

    def generate_content(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Gemini APIでコンテンツを生成

        Args:
            prompt: プロンプトテキスト
            max_retries: リトライ回数

        Returns:
            生成されたテキスト、失敗時はNone
        """
        if not self.client:
            logger.error("Gemini Client not initialized (Missing API Key)")
            return None

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )

                if response.text:
                    return response.text
                else:
                    logger.warning(f"Empty response from Gemini API (attempt {attempt + 1}/{max_retries})")

            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error("All Gemini API attempts failed")
                    return None

        return None

# グローバルインスタンス
gemini_client = GeminiClient()
