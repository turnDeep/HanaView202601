"""
Algo Scanner for HanaView
MarketAlgoXのデータを取得し、StageAlgoで分析を実行
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
from pathlib import Path

# Adjust imports to use the local modules we just created
from .gemini_client import gemini_client
from .algo_data_manager import AlgoDataManager

# Import MarketAlgoX modules
# Since we are inside backend package, we can use relative imports
from .market_algo_x.ibd_screeners import IBDScreeners
from .market_algo_x.ibd_data_collector import IBDDataCollector

# Import StageAlgo modules
from .stage_algo.gamma_plotter import GammaPlotter
from .stage_algo.quantlib_ai_analyzer import QuantLibAnalyzer
from .stage_algo.quantlib_timeseries_analyzer import TimeSeriesQuantLibAnalyzer

logger = logging.getLogger(__name__)

# Paths
CHARTS_ALGO_PATH = os.getenv("CHARTS_ALGO_PATH", "/app/frontend/charts/algo")

class AlgoScanner:
    def __init__(self):
        self.data_manager = AlgoDataManager()
        os.makedirs(CHARTS_ALGO_PATH, exist_ok=True)
        # Ensure FMP API Key is present
        self.fmp_api_key = os.getenv("FMP_API_KEY")
        if not self.fmp_api_key:
            logger.warning("FMP_API_KEY is not set. MarketAlgoX data collection will fail.")

    async def run_scan(self) -> Dict:
        """
        Algoスキャンを実行

        Returns:
            スキャン結果のサマリー
        """
        logger.info("Starting Algo scan...")

        # 1. MarketAlgoXのスクリーニング実行 (Data Collection + Screening)
        market_data = await self.run_market_algox()

        if not market_data:
            raise Exception("MarketAlgoX execution failed or returned no data")

        # 2. 各スクリーナーの銘柄を分析
        summary = {}
        volatility_distribution = {"contraction": 0, "transition": 0, "expansion": 0}

        for screener_key, symbols in market_data.items():
            # symbols is list of tickers
            logger.info(f"Analyzing screener: {screener_key} ({len(symbols)} symbols)")

            analyzed_symbols = []

            for ticker in symbols:
                try:
                    # StageAlgoで分析
                    analysis_result = await self.analyze_symbol(ticker)

                    if analysis_result:
                        # スクリーナー情報をマージ (symbol_data in this case is just ticker or simple dict)
                        # We construct the object
                        merged_data = {
                            'ticker': ticker,
                            'symbol': ticker, # Keep compatibility
                            **analysis_result
                        }
                        analyzed_symbols.append(merged_data)

                        # ボラティリティ分布を集計
                        regime = analysis_result.get('volatility_regime', 'transition')
                        volatility_distribution[regime] = volatility_distribution.get(regime, 0) + 1

                except Exception as e:
                    logger.error(f"Error analyzing {ticker}: {e}")
                    continue

            # バッチでGemini解説を生成
            if analyzed_symbols:
                gemini_results = await self.generate_batch_gemini_analysis(screener_key, analyzed_symbols)

                # 結果を統合して保存
                for symbol_data in analyzed_symbols:
                    ticker = symbol_data['ticker']
                    gemini_analysis = gemini_results.get(ticker)

                    # リスト内のデータにも解説を追加（フロントエンド表示用）
                    symbol_data['gemini_analysis'] = gemini_analysis

                    # 個別銘柄データを保存
                    self.data_manager.save_symbol_data(ticker, {
                        **symbol_data,
                        'gemini_analysis': gemini_analysis,
                        'screener_sources': [screener_key],
                        'last_updated': datetime.now().isoformat()
                    })

            summary[screener_key] = analyzed_symbols

        # 2.5 Top 5 AI Picksの生成
        top_picks = await self.generate_top_picks(summary)

        # 3. サマリーを保存
        summary_data = {
            'scan_date': datetime.now().strftime('%Y-%m-%d'),
            'scan_time': datetime.now().strftime('%H:%M:%S'),
            'total_scanned': sum(len(symbols) for symbols in summary.values()),
            'summary': summary,
            'top_picks': top_picks,
            'volatility_distribution': volatility_distribution,
            'updated_at': datetime.now().isoformat()
        }

        self.data_manager.save_daily_summary(summary_data)

        logger.info(f"Algo scan completed: {summary_data['total_scanned']} symbols analyzed")

        return summary_data

    async def run_market_algox(self) -> Dict[str, List[str]]:
        """
        MarketAlgoXのデータ収集とスクリーニングを実行
        Returns:
            Dict[screener_name, List[ticker]]
        """
        try:
            logger.info("Running MarketAlgoX Data Collection...")

            # Run in thread pool to avoid blocking async loop
            loop = asyncio.get_event_loop()

            def collect_and_screen():
                # 1. Data Collection
                collector = IBDDataCollector(self.fmp_api_key, debug=True)
                # For full run: collector.run_full_collection(use_full_dataset=False)
                # But that takes time. Let's assume we fetch tickers and run.
                # For now, let's run a lighter version or full version depending on env?
                # Let's run full collection but with limited scope if needed.
                # Warning: running full collection might take time.
                # For this implementation, we will trust IBDDataCollector logic.
                collector.run_full_collection(use_full_dataset=True, max_workers=5)
                collector.close()

                # 2. Screening
                logger.info("Running MarketAlgoX Screeners...")
                screeners = IBDScreeners()
                results = screeners.run_all_screeners()
                screeners.close()
                return results

            results = await loop.run_in_executor(None, collect_and_screen)
            return results

        except Exception as e:
            logger.error(f"MarketAlgoX run failed: {e}")
            return {}

    async def analyze_symbol(self, ticker: str) -> Optional[Dict]:
        """
        StageAlgoで銘柄を分析
        """
        try:
            loop = asyncio.get_event_loop()

            def run_stage_algo_tools():
                # 1. Gamma Plotter
                gp = GammaPlotter(ticker)
                if gp.fetch_data():
                    gp.calculate_current_gamma_levels()
                    gp.calculate_historical_metrics()
                    gamma_plot_path = gp.plot_analysis(output_dir=CHARTS_ALGO_PATH)
                    gamma_flip = gp.gamma_flip
                else:
                    gamma_plot_path = None
                    gamma_flip = None

                # 2. QuantLib AI Analyzer
                qa = QuantLibAnalyzer(ticker)
                ai_strategy = qa.run() # Returns dict

                # 3. Time Series Analyzer
                ts = TimeSeriesQuantLibAnalyzer(ticker)
                if ts.fetch_history():
                    ts.calculate_metrics()
                    ts_plot_path = ts.plot_analysis(output_dir=CHARTS_ALGO_PATH)
                    ts_report = ts.generate_report()
                    volatility_regime = ts_report.get('cycle_phase', 'transition').lower()
                    if 'contraction' in volatility_regime: volatility_regime = 'contraction'
                    elif 'expansion' in volatility_regime: volatility_regime = 'expansion'
                    else: volatility_regime = 'transition'

                    expected_move = ts_report.get('expected_move_30d')
                else:
                    ts_plot_path = None
                    volatility_regime = 'transition'
                    expected_move = None

                return {
                    'volatility_regime': volatility_regime,
                    'gamma_flip': gamma_flip,
                    'expected_move_30d': expected_move,
                    'analysis_data': {
                        'gamma_plot': f'/charts/algo/{os.path.basename(gamma_plot_path)}' if gamma_plot_path else None,
                        'timeseries_plot': f'/charts/algo/{os.path.basename(ts_plot_path)}' if ts_plot_path else None,
                        'ai_strategy': ai_strategy
                    }
                }

            return await loop.run_in_executor(None, run_stage_algo_tools)

        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return None

    async def generate_batch_gemini_analysis(self, screener_key: str, symbols_data: List[Dict]) -> Dict[str, str]:
        """Gemini APIで一括解説生成"""
        try:
            # プロンプト用のデータを構築
            prompt_data = []
            for item in symbols_data:
                prompt_data.append({
                    "ticker": item['ticker'],
                    "gamma_flip": item.get('gamma_flip'),
                    "volatility_regime": item.get('volatility_regime'),
                    "expected_move_30d": item.get('expected_move_30d'),
                    "ai_strategy": item.get('analysis_data', {}).get('ai_strategy', {})
                })

            prompt = f"""
あなたはプロの株式トレーダーです。以下の銘柄リスト（スクリーナー: {screener_key}）について、各銘柄の分析とトレーディング戦略を日本語で作成してください。

【入力データ】
{json.dumps(prompt_data, ensure_ascii=False, indent=2)}

【要件】
1. 各銘柄について、ガンマ分析とボラティリティ分析に基づいた具体的な戦略を記述すること。
2. エントリー/エグジットレベルとリスク管理のポイントを含めること。
3. 出力は**必ず以下のJSON形式**のみとすること。Markdownのコードブロックなどは含めないこと。
{{
  "TICKER": "解説テキスト（400文字以内）",
  ...
}}
"""

            response_text = gemini_client.generate_content(prompt)

            if not response_text:
                return {}

            # JSONパース（Markdownのバッククォートが含まれている場合の除去処理）
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)

        except Exception as e:
            logger.error(f"Error generating batch Gemini analysis: {e}")
            return {}

    async def generate_top_picks(self, summary_data: Dict[str, List[Dict]]) -> List[Dict]:
        """
        全スクリーナー結果からGeminiでTOP5を選定・解説
        """
        try:
            logger.info("Generating Top 5 AI Picks...")

            # 全銘柄データを収集（重複排除）
            unique_symbols = {}
            for screener_key, symbols_list in summary_data.items():
                for symbol_data in symbols_list:
                    ticker = symbol_data['ticker']
                    if ticker not in unique_symbols:
                        # 必要なデータのみ抽出
                        unique_symbols[ticker] = {
                            "ticker": ticker,
                            "screener": screener_key,
                            "volatility_regime": symbol_data.get('volatility_regime'),
                            "gamma_flip": symbol_data.get('gamma_flip'),
                            "expected_move_30d": symbol_data.get('expected_move_30d'),
                            # 前段で生成されたAI解説を含める
                            "ai_commentary": symbol_data.get('gemini_analysis', ''),
                            # AI戦略データ
                            "ai_strategy": symbol_data.get('analysis_data', {}).get('ai_strategy', {}),
                        }
                    else:
                        # 複数スクリーナーにヒットした場合はタグを追加するなどの処理が可能だが、今回はシンプルにスキップ
                        pass

            if not unique_symbols:
                return []

            # リスト化
            candidates = list(unique_symbols.values())

            prompt = f"""
あなたは高度なオプション取引とテクニカル分析の専門家です。
以下の候補銘柄リスト（各銘柄には事前のAI分析結果が含まれています）から、
本日最もトレードチャンスがあると思われる**TOP 5銘柄**を選定してください。

【候補銘柄リスト】
{json.dumps(candidates, ensure_ascii=False, indent=2)}

【指示】
1. オプション初心者にもわかりやすく、かつテクニカルトレーダーが納得する論理的な解説を行ってください。
2. ボラティリティ・レジーム、ガンマ・フリップ、期待変動率などを考慮し、リスクリワードが良い銘柄を優先してください。
3. 各銘柄について、以下の項目を具体的に示してください。
    - **選定理由**: なぜこの銘柄がチャンスなのか（テクニカル/オプション視点）
    - **損切りライン**: 具体的な価格または条件
    - **利確ライン**: 具体的な価格目標
    - **リスクリワード**: 現状の比率（例: 1:2.5）

【出力形式】
**必ず以下のJSON配列形式**のみで出力してください。Markdownのコードブロックは不要です。

[
  {{
    "ticker": "AAPL",
    "reason": "解説テキスト...",
    "stop_loss": "150ドル割れ",
    "take_profit": "165ドル付近",
    "risk_reward": "1:3"
  }},
  ...
]
"""
            response_text = gemini_client.generate_content(prompt)

            if not response_text:
                logger.error("Empty response from Gemini for Top Picks")
                return []

            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            top_picks = json.loads(clean_text)

            # リスト形式であることを確認
            if isinstance(top_picks, list):
                return top_picks[:5] # 念のため5件に制限
            else:
                logger.error("Gemini response format error: Not a list")
                return []

        except Exception as e:
            logger.error(f"Error generating Top Picks: {e}")
            return []

# グローバルインスタンス
algo_scanner = AlgoScanner()

async def run_algo_scan() -> Dict:
    """Algoスキャンを実行（エントリーポイント）"""
    return await algo_scanner.run_scan()

async def analyze_single_ticker_algo(ticker: str) -> Optional[Dict]:
    """単一銘柄を分析（検索機能用）"""
    return await algo_scanner.analyze_symbol(ticker)
