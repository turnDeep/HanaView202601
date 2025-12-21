"""
Algo Data Manager for HanaView
Algoスキャンデータの読み書きと管理
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AlgoDataManager:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.algo_dir = os.path.join(data_dir, 'algo')
        self.daily_dir = os.path.join(self.algo_dir, 'daily')
        self.symbols_dir = os.path.join(self.algo_dir, 'symbols')

        # ディレクトリ作成
        os.makedirs(self.daily_dir, exist_ok=True)
        os.makedirs(self.symbols_dir, exist_ok=True)

    def save_daily_summary(self, summary_data: Dict) -> bool:
        """デイリーサマリーを保存"""
        try:
            # latest.json
            latest_path = os.path.join(self.daily_dir, 'latest.json')
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

            # アーカイブ
            scan_date = summary_data.get('scan_date', datetime.now().strftime('%Y-%m-%d'))
            archive_path = os.path.join(self.daily_dir, f'algo_{scan_date}.json')
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Daily summary saved: {latest_path}, {archive_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving daily summary: {e}")
            return False

    def load_latest_summary(self) -> Optional[Dict]:
        """最新のサマリーをロード"""
        try:
            latest_path = os.path.join(self.daily_dir, 'latest.json')

            if not os.path.exists(latest_path):
                return None

            with open(latest_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading latest summary: {e}")
            return None

    def save_symbol_data(self, symbol: str, symbol_data: Dict) -> bool:
        """個別銘柄データを保存"""
        try:
            symbol_path = os.path.join(self.symbols_dir, f'{symbol.upper()}.json')

            with open(symbol_path, 'w', encoding='utf-8') as f:
                json.dump(symbol_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Symbol data saved: {symbol_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving symbol data for {symbol}: {e}")
            return False

    def load_symbol_data(self, symbol: str) -> Optional[Dict]:
        """個別銘柄データをロード"""
        try:
            symbol_path = os.path.join(self.symbols_dir, f'{symbol.upper()}.json')

            if not os.path.exists(symbol_path):
                return None

            with open(symbol_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading symbol data for {symbol}: {e}")
            return None
