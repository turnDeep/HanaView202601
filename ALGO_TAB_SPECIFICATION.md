# Algoタブ 実装仕様書

## 概要

HanaView202601に新しい「Algo」タブを追加し、MarketAlgoXの6つのスクリーナーで抽出された銘柄について、StageAlgoの分析ツールを使用して画像出力とGemini APIによる解説を提供する機能を実装する。

---

## 1. 機能要件

### 1.1 タブ構成

- **タブ名**: Algo
- **配置**: 既存のタブ群に追加
- **表示順**: ユーザーインターフェースの適切な位置に配置

### 1.2 スクリーナー種類

MarketAlgoXリポジトリ (https://github.com/turnDeep/MarketAlgoX) から以下の6つのIBDスタイルスクリーナーを利用:

#### 1. **Momentum 97** (短期中期長期の最強銘柄)
- **説明**: 1ヶ月、3ヶ月、6ヶ月のすべての期間でトップ3%のパフォーマンスを示す銘柄
- **抽出条件**: 短期・中期・長期すべてでトップパフォーマンス

#### 2. **Explosive Estimated EPS Growth** (爆発的EPS成長銘柄)
- **説明**: 前年同期比100%以上の四半期EPSグロースを示す銘柄
- **抽出条件**: 積極的な収益拡大を示す企業

#### 3. **Up on Volume** (出来高急増上昇銘柄)
- **説明**: 平均出来高比20%以上の増加を伴って上昇している銘柄
- **抽出条件**: 出来高を伴って上昇中の銘柄

#### 4. **Top 2% RS Rating** (相対強度トップ2%銘柄)
- **説明**: RS Rating 98以上の極めて高い相対的強さを持つ銘柄
- **抽出条件**: 市場全体に対する相対的強さが極めて高い

#### 5. **4% Bullish Yesterday** (急騰直後銘柄)
- **説明**: 前営業日に4%以上の強い上昇を見せた銘柄
- **抽出条件**: 前日に顕著な上昇を示した銘柄

#### 6. **Healthy Chart Watch List** (健全チャート銘柄)
- **説明**: 理想的な移動平均線の並び（MA順序）と健全なチャートパターンを持つ銘柄
- **抽出条件**: Stage 2（上昇トレンド）で健全なテクニカルパターンを維持

### 1.3 分析ツール

StageAlgoリポジトリ (https://github.com/turnDeep/StageAlgo) から以下の3つのツールを利用:

#### 1.3.1 **gamma_plotter.py** - オプションガンマ分析

**機能概要**:
- オプション市場のガンマダイナミクスと過去のボラティリティを分析
- yfinanceを使用して1年間の株価データとオプションチェーンを取得
- QuantLibのBlack-Scholesモデルでガンマを計算

**出力内容**:
- **Zero Gamma Flip**: ネットガンマエクスポージャーの符号が変わる価格レベル
- **Magnet/Wall**: 最大正ガンマのストライク（価格引き寄せゾーン）
- **Acceleration Zone**: 最大負ガンマのストライク（価格加速ゾーン）
- 20日間の過去ボラティリティ（HV）
- ATMストラドル価格による30日間の期待移動率
- ±10%移動の確率

**画像出力**: `{ticker}_gamma_analysis.png` (3パネルチャート)
1. ガンマレベル付き株価チャート + HVヒートマップ
2. 30日間期待移動バンド
3. 上昇/下降確率スキュー

#### 1.3.2 **quantlib_ai_analyzer.py** - QuantLib AI戦略分析

**機能概要**:
- QuantLibを使用した高度なオプション・ボラティリティ分析
- AI駆動のトレーディング戦略生成

**分析内容**:
- **ボラティリティメトリクス**: 20日間HVと年間レンジの追跡
- **市場サイクル分類**: Contraction（収縮）、Expansion（拡大）、Transition（移行）
- **IV vs HV比較**: インプライドボラティリティと過去ボラティリティの乖離分析
- **ガンマエクスポージャープロファイル**:
  - 全ストライクのコール/プットOI取得
  - Black-Scholes-Mertonでストライクごとのガンマ計算
  - Zero Gamma Flipレベル特定
  - 正/負GEXゾーン（レジスタンス vs 加速エリア）の特定
- **確率分析**: リスクニュートラル評価による±10%移動確率とスキューバイアス定量化

**AI戦略生成**:
- 分析結果をClaude/ChatGPT用のプロンプトに構造化
- ガンマレベルを「見えざる力」として、ディーラーヘッジフローが価格に与える影響を分析
- 具体的なガンマ定義価格レベルに紐づいたアクション可能なトレーディングトリガーを提供

**出力形式**: JSON（比較マトリクスとトリガーベース戦略）

#### 1.3.3 **quantlib_timeseries_analyzer.py** - 時系列統計分析

**機能概要**:
- QuantLibと金融データライブラリを使用した定量的時系列分析
- yfinanceで1年間の日次株価データを取得

**分析内容**:
- **ボラティリティメトリクス**: 年率換算20日間HVとレジーム推移追跡
- **オプションベースリスク測定**:
  - Black-Scholesモデルで30日間期待移動率を計算
  - ATMストラドル（コール+プット）価格による期待移動率
  - ±10%移動の30日間確率推定
  - 下方リスク vs 上方リスクのスキューバイアスメトリクス
- **サイクル分類**: ボラティリティが過去の高値/安値付近にあるかに基づき、「Contraction」「Expansion」「Transition」に分類

**可視化出力**: 3パネルチャート
1. ボラティリティレジームで色分けされた価格チャート（緑/黄/赤 = 低/通常/高ボラティリティ）
2. 時系列での理論的期待移動率パーセンテージ
3. 下方/上方移動の比較確率曲線

**出力形式**: チャート画像 + 現在のリスク状況のサマリー統計

### 1.4 UI/UX設計

#### 1.4.1 スクリーナー切り替えボタン

- **配置**: 200MAタブの「当日ブレイクアウト」「直近5営業日」「監視銘柄」ボタンと同じ位置
- **構成**: 6つのボタンを横並びで配置（画面サイズに応じて2行に折り返し可能）
- **ボタンラベル**:
  1. `Momentum 97`
  2. `Explosive EPS`
  3. `Up on Volume`
  4. `Top 2% RS`
  5. `4% Bullish`
  6. `Healthy Chart`
- **動作**:
  - 各ボタンをクリックすると、対応するスクリーナーの結果リストを表示
  - アクティブなボタンはハイライト表示（200MAタブと同様のスタイル）

#### 1.4.2 銘柄リスト表示

**リストアイテム構成**:
- **銘柄名** (ティッカーシンボル)
- **ボラティリティステータスバッジ** (緑/黄/赤)
- **分析画像** (gamma_plotter.pyで生成された3パネルチャート)
- **メタ情報** (RS Rating、EPS成長率、出来高増加率など、スクリーナーによって異なる)

**ソート順** (上から順に):
1. 🟢 **緑色 (Contraction / Low Vol)**: 「凪（なぎ）」の状態 - ボラティリティ収縮期
2. 🟡 **黄色 (Transition / Normal)**: 通常運転の状態 - 移行期
3. 🔴 **赤色 (Expansion / High Vol)**: 「嵐（パニック）」の状態 - ボラティリティ拡大期

**画像の操作**:
- **ダブルタップ**: 画像を拡大表示 + Gemini APIによる解説テキストを表示
- 拡大表示時は背景オーバーレイで他のコンテンツを隠す
- オーバーレイクリックで元の画面に戻る
- **解説内容**:
  - ガンマレベルの解説（Zero Gamma Flip、Magnet/Wall、Acceleration Zone）
  - 現在のボラティリティレジーム
  - 期待移動率と確率的リスク分析
  - トレーディング戦略の示唆（quantlib_ai_analyzerからの情報）

#### 1.4.3 検索機能

**動作仕様**:
1. 検索ボックスにティッカーシンボルを入力
2. 全6スクリーナーのリストから該当銘柄を検索
3. **該当あり**:
   - その銘柄のデータとチャートを表示
   - どのスクリーナーに該当するか表示
   - Gemini APIによる完全な解説を表示
4. **該当なし**:
   - その場でStageAlgoの分析ツール（gamma_plotter.py）を実行し、画像を生成
   - 生成した画像を表示
   - **重要**: スクリーナーにない銘柄はGemini解説を出力しない（画像のみ表示）
   - 「この銘柄はスクリーナーに含まれていません。チャート分析のみ表示します。」とメッセージを表示

---

## 2. 認証・権限管理

### 2.1 アクセス権限

| 権限レベル | 200MAタブ | Algoタブ |
|----------|----------|---------|
| standard | ❌ | ❌ |
| secret | ✅ 閲覧・通知 | ❌ |
| **ura** | ✅ 閲覧・通知 | ✅ **閲覧・通知** |

- **Algoタブは `ura` コードの人のみアクセス可能**
- uraコード以外のユーザーにはタブを非表示にする
- フロントエンドの `applyTabPermissions()` 関数で制御

### 2.2 Push通知

- **対象者**: `ura` 権限保持者のみ
- **通知タイミング**: Algoスキャン完了時（月〜金 8:00 AM実行後）
- **通知内容**:
  - 「Algoスキャン完了」
  - 「新規シグナル: {total_signals}件」
  - 各スクリーナーの銘柄数内訳

---

## 3. Cronジョブ設定

### 3.1 実行スケジュール

```bash
月曜日〜金曜日の朝8時 (JST)
```

MarketAlgoXは火曜〜土曜の6時に実行されるため、その2時間後に実行することで、MarketAlgoXのスクリーニング結果を取得できる。

### 3.2 実行内容

1. **MarketAlgoXのスクリーニング結果を取得**
   - MarketAlgoXのJSON出力ファイル（`YYYYMMDD.json`）を読み込み
   - 6つのスクリーナーそれぞれの銘柄リストを取得

2. **StageAlgoの分析を実行**
   - 各銘柄に対して以下の3つのツールを並列実行:
     - `gamma_plotter.py` → `{ticker}_gamma_analysis.png`
     - `quantlib_ai_analyzer.py` → `{ticker}_ai_analysis.json`
     - `quantlib_timeseries_analyzer.py` → `{ticker}_timeseries_analysis.png`

3. **ボラティリティレジーム分類**
   - `quantlib_timeseries_analyzer.py` の出力から各銘柄を分類:
     - **Contraction** (Low Vol) → 緑
     - **Transition** (Normal) → 黄
     - **Expansion** (High Vol) → 赤

4. **Gemini APIで解説生成**
   - `quantlib_ai_analyzer.py` の出力JSONと画像を元に、Gemini APIで各銘柄の解説を生成
   - プロンプト:
     ```
     以下のガンマ分析とボラティリティ分析に基づいて、この銘柄のトレーディング戦略を日本語で簡潔に説明してください:

     【ガンマレベル】
     - Zero Gamma Flip: {value}
     - Magnet/Wall: {value}
     - Acceleration Zone: {value}

     【ボラティリティ】
     - 現在のレジーム: {regime}
     - 20日間HV: {hv}
     - 30日間期待移動率: {expected_move}
     - 下方リスク確率: {downside_prob}
     - 上方リスク確率: {upside_prob}

     【AI戦略】
     {ai_strategy_from_quantlib_ai_analyzer}

     トレーダーが実際に使える具体的なエントリー/エグジットレベルと、リスク管理のポイントを含めてください。
     ```

5. **データをJSONファイルに保存**
   - `data/algo/daily/latest.json` (最新のサマリー)
   - `data/algo/daily/algo_YYYY-MM-DD.json` (日付別アーカイブ)
   - `data/algo/symbols/{TICKER}.json` (個別銘柄データ)

6. **ura権限ユーザーにPush通知を送信**
   - `_send_notifications_to_permission_level("ura", ...)` を使用

### 3.3 Cronエントリ

```bash
# Algoスキャン実行（月〜金 8:00 AM JST）
0 8 * * 1-5 . /app/backend/cron-env.sh && /app/backend/cron_job_algo.sh >> /app/logs/cron_error.log 2>&1
```

**Dockerfileへの追加**:
```dockerfile
RUN chmod +x /app/backend/cron_job_algo.sh
```

---

## 4. API設計

### 4.1 Gemini API統一

**重要**: OpenAI APIからGemini APIに全面移行

- **使用モデル**: `gemini-3-flash-preview` (2025年12月時点の最新モデル)
- **API呼び出し**: `google-genai` ライブラリを使用（`google-generativeai`は非推奨）
- **既存のOpenAI API呼び出しをすべてGemini APIに置き換える**

**実装例**:
```python
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=prompt
)

analysis_text = response.text
```

### 4.2 バックエンドAPIエンドポイント

#### 4.2.1 Algoスキャンデータ取得

```
GET /api/algo/daily/latest
```

**認証**: `ura` 権限必須

**レスポンス例**:
```json
{
  "scan_date": "2025-12-21",
  "scan_time": "08:30:00",
  "total_scanned": 150,
  "summary": {
    "momentum_97": [
      {
        "symbol": "NVDA",
        "volatility_regime": "contraction",
        "rs_rating": 99,
        "gamma_flip": 135.50,
        "expected_move_30d": 8.5,
        "screener_key": "momentum_97"
      }
    ],
    "explosive_eps": [...],
    "up_on_volume": [...],
    "top_2pct_rs": [...],
    "bullish_4pct": [...],
    "healthy_chart": [...]
  },
  "volatility_distribution": {
    "contraction": 45,
    "transition": 60,
    "expansion": 45
  },
  "updated_at": "2025-12-21T08:30:00+09:00"
}
```

#### 4.2.2 個別銘柄データ取得

```
GET /api/algo/symbols/{symbol}
```

**認証**: `ura` 権限必須

**レスポンス例**:
```json
{
  "symbol": "NVDA",
  "volatility_regime": "contraction",
  "analysis_data": {
    "gamma_plot": "/charts/algo/NVDA_gamma_analysis.png",
    "timeseries_plot": "/charts/algo/NVDA_timeseries_analysis.png",
    "ai_strategy": {
      "zero_gamma_flip": 135.50,
      "magnet_wall": 140.00,
      "acceleration_zone": 130.00,
      "hv_20d": 0.35,
      "expected_move_30d": 8.5,
      "downside_prob_10pct": 0.25,
      "upside_prob_10pct": 0.30,
      "current_regime": "Contraction",
      "strategy_triggers": {
        "entry_level": 136.00,
        "stop_loss": 132.00,
        "target": 142.00
      }
    }
  },
  "gemini_analysis": "【ガンマ分析に基づく戦略】\n\nNVDAは現在、ボラティリティ収縮期（Contraction）にあり、Zero Gamma Flip（$135.50）付近で推移しています。\n\n【トレーディング戦略】\n- エントリー: $136.00でロングポジション構築\n- ターゲット: Magnet/Wall（$140.00）、最終目標$142.00\n- ストップロス: $132.00（Acceleration Zone下）\n\n【リスク管理】\n- 30日間の期待移動率は8.5%と比較的穏やか\n- 上方リスク確率（30%）が下方リスク（25%）を上回り、ポジティブバイアス\n- ボラティリティ収縮期のため、大きなブレイクアウトに備える\n\nGamma Flipを上抜けた場合、ディーラーのヘッジフローがサポートとなり、$140付近のMagnetに引き寄せられる可能性が高い。",
  "screener_sources": ["momentum_97", "top_2pct_rs"],
  "metadata": {
    "rs_rating": 99,
    "eps_growth_pct": null,
    "volume_increase_pct": null,
    "price_change_yesterday": null
  },
  "last_updated": "2025-12-21T08:30:00+09:00"
}
```

#### 4.2.3 銘柄検索・オンデマンド分析

```
GET /api/algo/analyze_ticker?ticker={SYMBOL}&force={true|false}
```

**認証**: `ura` 権限必須

**パラメータ**:
- `ticker`: ティッカーシンボル（必須）
- `force`:
  - `false` (デフォルト): キャッシュデータを返す、なければ404
  - `true`: 強制的に新規分析を実行

**動作**:
1. `force=false` の場合:
   - `data/algo/symbols/{TICKER}.json` が存在すればそれを返す
   - 存在しなければ404エラー

2. `force=true` の場合:
   - StageAlgoの分析ツールを実行:
     - `gamma_plotter.py` でチャート生成
     - `quantlib_ai_analyzer.py` で分析JSON生成
     - `quantlib_timeseries_analyzer.py` でボラティリティ分類
   - スクリーナーに含まれていない場合:
     - Gemini解説は生成しない
     - `"gemini_analysis": null` を返す
     - `"screener_sources": []` を返す
   - スクリーナーに含まれている場合:
     - Gemini解説を生成
     - 完全なデータを返す

**レスポンス（スクリーナー該当なしの場合）**:
```json
{
  "symbol": "AAPL",
  "volatility_regime": "transition",
  "analysis_data": {
    "gamma_plot": "/charts/algo/AAPL_gamma_analysis.png",
    "timeseries_plot": "/charts/algo/AAPL_timeseries_analysis.png",
    "ai_strategy": { /* ... */ }
  },
  "gemini_analysis": null,
  "screener_sources": [],
  "metadata": {},
  "message": "この銘柄はスクリーナーに含まれていません。チャート分析のみ表示します。",
  "last_updated": "2025-12-21T09:15:00+09:00"
}
```

#### 4.2.4 手動スキャン実行 (管理者用)

```
POST /api/algo/scan
```

**認証**: `ura` 権限必須

**レスポンス**:
```json
{
  "success": true,
  "message": "スキャン完了: 150件のシグナル検出",
  "scan_date": "2025-12-21",
  "scan_time": "09:30:00",
  "summary": {
    "momentum_97": 25,
    "explosive_eps": 18,
    "up_on_volume": 30,
    "top_2pct_rs": 22,
    "bullish_4pct": 15,
    "healthy_chart": 40
  }
}
```

---

## 5. データ構造

### 5.1 ファイル配置

```
data/
├── algo/
│   ├── daily/
│   │   ├── latest.json                    # 最新のサマリー
│   │   └── algo_2025-12-21.json          # 日付別アーカイブ
│   └── symbols/
│       ├── NVDA.json                      # 個別銘柄データ
│       ├── AAPL.json
│       └── ...
frontend/
└── charts/
    └── algo/
        ├── NVDA_gamma_analysis.png        # gamma_plotter.py出力
        ├── NVDA_timeseries_analysis.png   # quantlib_timeseries_analyzer.py出力
        ├── AAPL_gamma_analysis.png
        └── ...
```

### 5.2 ボラティリティレジーム判定基準

StageAlgoの `quantlib_timeseries_analyzer.py` のサイクル分類に基づく:

```python
def classify_volatility_regime(hv_current, hv_history):
    """
    ボラティリティレジームを分類

    Args:
        hv_current: 現在の20日間HV
        hv_history: 過去1年間のHV系列

    Returns:
        regime: "contraction", "transition", "expansion"
    """
    hv_low = np.percentile(hv_history, 20)
    hv_high = np.percentile(hv_history, 80)

    if hv_current <= hv_low:
        return "contraction"  # 緑（凪）
    elif hv_current >= hv_high:
        return "expansion"    # 赤（嵐）
    else:
        return "transition"   # 黄（通常）
```

**可視化**:
- 🟢 **Contraction** (Low Vol): `background-color: #4CAF50` - HVが過去のパーセンタイル20以下
- 🟡 **Transition** (Normal): `background-color: #FFC107` - HVが中間域
- 🔴 **Expansion** (High Vol): `background-color: #F44336` - HVが過去のパーセンタイル80以上

### 5.3 MarketAlgoXデータフォーマット連携

MarketAlgoXの出力JSON (`YYYYMMDD.json`) から以下の情報を取得:

```json
{
  "date": "20251221",
  "screeners": {
    "momentum_97": [
      {
        "ticker": "NVDA",
        "rs_rating": 99,
        "composite_rating": 98,
        "eps_rating": 95,
        "industry": "Semiconductors"
      }
    ],
    "explosive_eps_growth": [
      {
        "ticker": "SMCI",
        "eps_growth_pct": 250.5,
        "rs_rating": 96
      }
    ],
    "up_on_volume": [
      {
        "ticker": "AMD",
        "volume_increase_pct": 150,
        "price_change_pct": 3.5,
        "rs_rating": 94
      }
    ],
    "top_2pct_rs": [...],
    "bullish_4pct_yesterday": [...],
    "healthy_chart_watch": [...]
  }
}
```

---

## 6. フロントエンド実装

### 6.1 HTML構造 (index.html追加部分)

```html
<!-- Algoタブボタン -->
<button class="tab-button" data-tab="algo">Algo</button>

<!-- Algoタブコンテンツ -->
<div id="algo-content" class="tab-pane">
  <!-- 検索バー -->
  <div class="algo-controls">
    <input type="text" id="algo-ticker-input" placeholder="ティッカー検索..." class="ticker-input">
    <button id="algo-analyze-btn" class="analyze-btn">検索</button>
  </div>

  <!-- ステータス表示 -->
  <div id="algo-status" class="algo-status-info"></div>

  <!-- スクリーナーボタン -->
  <div id="algo-screener-buttons" class="screener-buttons">
    <button class="screener-btn active" data-screener="momentum_97">Momentum 97</button>
    <button class="screener-btn" data-screener="explosive_eps">Explosive EPS</button>
    <button class="screener-btn" data-screener="up_on_volume">Up on Volume</button>
    <button class="screener-btn" data-screener="top_2pct_rs">Top 2% RS</button>
    <button class="screener-btn" data-screener="bullish_4pct">4% Bullish</button>
    <button class="screener-btn" data-screener="healthy_chart">Healthy Chart</button>
  </div>

  <!-- コンテンツエリア -->
  <div id="algo-content-area"></div>
</div>
```

### 6.2 JavaScript実装 (app.js追加部分)

```javascript
class AlgoManager {
  constructor() {
    this.summaryData = null;
    this.currentView = 'summary';
    this.activeScreener = 'momentum_97'; // デフォルト
    this.initEventListeners();
  }

  initEventListeners() {
    // スクリーナーボタンのイベント
    const screenerButtons = document.querySelectorAll('.screener-btn');
    screenerButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeScreener = btn.dataset.screener;
        this.switchScreener(btn.dataset.screener);
      });
    });

    // 検索ボタンのイベント
    const searchBtn = document.getElementById('algo-analyze-btn');
    if (searchBtn) {
      searchBtn.addEventListener('click', () => {
        if (searchBtn.dataset.state === 'reset') {
          this.resetToSummary();
        } else {
          this.searchTicker();
        }
      });
    }
  }

  async loadData() {
    this.showStatus('最新のAlgoデータを読み込み中...', 'info');

    try {
      const response = await fetchWithAuth('/api/algo/daily/latest');

      if (!response.ok) {
        if (response.status === 404) {
          this.showStatus('データがありません。スキャンを実行してください。', 'warning');
          return;
        }
        throw new Error(`サーバーエラー: ${response.status}`);
      }

      this.summaryData = await response.json();
      this.currentView = 'summary';
      this.render();

      const { updated_at, volatility_distribution } = this.summaryData;
      const displayDate = formatDateForDisplay(updated_at);

      this.showStatus(
        `最終更新: ${displayDate} | 緑: ${volatility_distribution.contraction} | 黄: ${volatility_distribution.transition} | 赤: ${volatility_distribution.expansion}`,
        'info'
      );

    } catch (error) {
      console.error('Algo data loading error:', error);
      this.showStatus(`❌ データ読み込みエラー: ${error.message}`, 'error');
    }
  }

  switchScreener(screenerKey) {
    // ボタンのアクティブ状態を更新
    document.querySelectorAll('.screener-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.screener === screenerKey);
    });

    this.activeScreener = screenerKey;
    this.render();
  }

  render() {
    if (!this.summaryData) return;

    const container = document.getElementById('algo-content-area');
    container.innerHTML = '';

    this.renderSummaryStats(container);
    this.renderSymbolList(container);
  }

  renderSummaryStats(container) {
    const { summary, volatility_distribution } = this.summaryData;
    const screenerData = summary[this.activeScreener] || [];

    const statsDiv = document.createElement('div');
    statsDiv.className = 'algo-summary-stats';
    statsDiv.innerHTML = `
      <h2>${this.getScreenerDisplayName(this.activeScreener)}</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">銘柄数</span>
          <span class="stat-value">${screenerData.length}</span>
        </div>
        <div class="stat-card green">
          <span class="stat-label">凪（緑）</span>
          <span class="stat-value">${screenerData.filter(s => s.volatility_regime === 'contraction').length}</span>
        </div>
        <div class="stat-card yellow">
          <span class="stat-label">通常（黄）</span>
          <span class="stat-value">${screenerData.filter(s => s.volatility_regime === 'transition').length}</span>
        </div>
        <div class="stat-card red">
          <span class="stat-label">嵐（赤）</span>
          <span class="stat-value">${screenerData.filter(s => s.volatility_regime === 'expansion').length}</span>
        </div>
      </div>
    `;

    container.appendChild(statsDiv);
  }

  renderSymbolList(container) {
    const { summary } = this.summaryData;
    const screenerData = summary[this.activeScreener] || [];

    if (screenerData.length === 0) {
      container.innerHTML += '<p class="no-data">このスクリーナーには該当銘柄がありません。</p>';
      return;
    }

    // ボラティリティレジーム順にソート
    const sortOrder = { 'contraction': 0, 'transition': 1, 'expansion': 2 };
    const sortedData = [...screenerData].sort((a, b) => {
      return sortOrder[a.volatility_regime] - sortOrder[b.volatility_regime];
    });

    const listDiv = document.createElement('div');
    listDiv.className = 'algo-symbol-list';

    sortedData.forEach(item => {
      const symbolItem = this.createSymbolItem(item);
      listDiv.appendChild(symbolItem);
    });

    container.appendChild(listDiv);
  }

  createSymbolItem(item) {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'algo-symbol-item';

    const regimeClass = `regime-${item.volatility_regime}`;
    const regimeLabel = this.getRegimeLabel(item.volatility_regime);

    const chartUrl = `/charts/algo/${item.symbol}_gamma_analysis.png?v=${new Date().getTime()}`;

    itemDiv.innerHTML = `
      <div class="symbol-header">
        <span class="symbol-name">${item.symbol}</span>
        <span class="regime-badge ${regimeClass}">${regimeLabel}</span>
      </div>
      <div class="symbol-meta">
        ${this.renderMetaInfo(item)}
      </div>
      <div class="symbol-chart">
        <img src="${chartUrl}" alt="${item.symbol} Gamma Analysis" class="algo-chart-img" loading="lazy" onerror="this.style.display='none'">
      </div>
    `;

    // ダブルタップリスナーを追加
    const img = itemDiv.querySelector('.algo-chart-img');
    if (img) {
      this.addDoubleTapListener(img, item.symbol);
    }

    return itemDiv;
  }

  renderMetaInfo(item) {
    let metaHtml = '';

    if (item.rs_rating !== undefined && item.rs_rating !== null) {
      const rsClass = this.getRSClass(item.rs_rating);
      metaHtml += `<span class="meta-badge ${rsClass}">RS ${item.rs_rating}</span>`;
    }

    if (item.eps_growth_pct !== undefined && item.eps_growth_pct !== null) {
      metaHtml += `<span class="meta-badge eps-badge">EPS +${item.eps_growth_pct}%</span>`;
    }

    if (item.volume_increase_pct !== undefined && item.volume_increase_pct !== null) {
      metaHtml += `<span class="meta-badge vol-badge">Vol +${item.volume_increase_pct}%</span>`;
    }

    if (item.expected_move_30d !== undefined && item.expected_move_30d !== null) {
      metaHtml += `<span class="meta-badge move-badge">30日予想 ±${item.expected_move_30d}%</span>`;
    }

    return metaHtml;
  }

  getScreenerDisplayName(screenerKey) {
    const names = {
      'momentum_97': 'Momentum 97 - 短期中期長期の最強銘柄',
      'explosive_eps': 'Explosive EPS Growth - 爆発的EPS成長銘柄',
      'up_on_volume': 'Up on Volume - 出来高急増上昇銘柄',
      'top_2pct_rs': 'Top 2% RS Rating - 相対強度トップ2%銘柄',
      'bullish_4pct': '4% Bullish Yesterday - 急騰直後銘柄',
      'healthy_chart': 'Healthy Chart Watch - 健全チャート銘柄'
    };
    return names[screenerKey] || screenerKey;
  }

  getRegimeLabel(regime) {
    const labels = {
      'contraction': '🟢 凪',
      'transition': '🟡 通常',
      'expansion': '🔴 嵐'
    };
    return labels[regime] || regime;
  }

  getRSClass(rsRating) {
    if (rsRating >= 90) return 'rs-excellent';
    if (rsRating >= 80) return 'rs-good';
    if (rsRating >= 70) return 'rs-average';
    return 'rs-weak';
  }

  addDoubleTapListener(element, symbol) {
    let lastTap = 0;

    element.addEventListener('touchend', (e) => {
      const currentTime = new Date().getTime();
      const tapLength = currentTime - lastTap;
      if (tapLength < 500 && tapLength > 0) {
        e.preventDefault();
        this.showImagePopup(symbol);
      }
      lastTap = currentTime;
    });

    // デスクトップ用
    element.addEventListener('dblclick', () => {
      this.showImagePopup(symbol);
    });
  }

  async showImagePopup(symbol) {
    try {
      // 個別銘柄データを取得
      const response = await fetchWithAuth(`/api/algo/symbols/${symbol}`);
      const data = await response.json();

      // オーバーレイ作成
      const overlay = document.createElement('div');
      overlay.className = 'algo-image-popup-overlay';

      // コンテンツコンテナ
      const contentDiv = document.createElement('div');
      contentDiv.className = 'algo-popup-content';

      // 画像
      const img = document.createElement('img');
      img.src = data.analysis_data.gamma_plot;
      img.className = 'algo-popup-image';

      // Gemini解説
      const analysisDiv = document.createElement('div');
      analysisDiv.className = 'algo-popup-analysis';

      if (data.gemini_analysis) {
        analysisDiv.innerHTML = `
          <h3>AI解説 (Gemini)</h3>
          <p>${data.gemini_analysis.replace(/\n/g, '<br>')}</p>
        `;
      } else {
        analysisDiv.innerHTML = `
          <p class="no-analysis">${data.message || 'この銘柄はスクリーナーに含まれていません。'}</p>
        `;
      }

      contentDiv.appendChild(img);
      contentDiv.appendChild(analysisDiv);
      overlay.appendChild(contentDiv);

      // クローズイベント
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          document.body.removeChild(overlay);
        }
      });

      document.body.appendChild(overlay);

    } catch (error) {
      console.error('Error loading symbol data:', error);
      alert('銘柄データの読み込みに失敗しました。');
    }
  }

  async searchTicker() {
    const input = document.getElementById('algo-ticker-input');
    const ticker = input.value.trim().toUpperCase();

    if (!ticker) {
      this.showStatus('ティッカーシンボルを入力してください', 'warning');
      return;
    }

    this.showStatus(`${ticker}のデータを検索中...`, 'info');

    try {
      // まずキャッシュを確認
      const response = await fetchWithAuth(`/api/algo/analyze_ticker?ticker=${ticker}&force=false`);

      if (!response.ok) {
        if (response.status === 404) {
          // キャッシュにない場合、ユーザーに確認
          const shouldAnalyze = confirm(`${ticker}はスクリーナーに含まれていません。\n新規に分析を実行しますか？（Gemini解説は含まれません）`);

          if (shouldAnalyze) {
            await this.forceAnalyzeTicker(ticker);
          } else {
            this.showStatus('検索をキャンセルしました', 'info');
          }
          return;
        }
        throw new Error(`検索に失敗しました: ${response.status}`);
      }

      const symbolData = await response.json();
      this.renderSearchResults(ticker, symbolData);

      const searchBtn = document.getElementById('algo-analyze-btn');
      if (searchBtn) {
        searchBtn.textContent = 'リセット';
        searchBtn.dataset.state = 'reset';
      }

      this.showStatus(`✅ ${ticker}の検索結果を表示中`, 'info');

    } catch (error) {
      console.error('Search error:', error);
      this.showStatus(`❌ エラー: ${error.message}`, 'error');
    }
  }

  async forceAnalyzeTicker(ticker) {
    this.showStatus(`${ticker}を分析中... (30秒程度かかります)`, 'info');

    try {
      const response = await fetchWithAuth(`/api/algo/analyze_ticker?ticker=${ticker}&force=true`);

      if (!response.ok) {
        throw new Error(`分析に失敗しました: ${response.status}`);
      }

      const symbolData = await response.json();
      this.renderSearchResults(ticker, symbolData);

      const searchBtn = document.getElementById('algo-analyze-btn');
      if (searchBtn) {
        searchBtn.textContent = 'リセット';
        searchBtn.dataset.state = 'reset';
      }

      this.showStatus(`✅ ${ticker}の分析が完了しました`, 'info');

    } catch (error) {
      console.error('Force analysis error:', error);
      this.showStatus(`❌ 分析エラー: ${error.message}`, 'error');
    }
  }

  renderSearchResults(ticker, symbolData) {
    const container = document.getElementById('algo-content-area');
    container.innerHTML = '';

    const resultDiv = document.createElement('div');
    resultDiv.className = 'algo-search-results';

    const regimeClass = `regime-${symbolData.volatility_regime}`;
    const regimeLabel = this.getRegimeLabel(symbolData.volatility_regime);

    resultDiv.innerHTML = `
      <div class="search-result-header">
        <h2>${ticker} の分析結果</h2>
        <span class="regime-badge ${regimeClass}">${regimeLabel}</span>
      </div>
    `;

    if (symbolData.screener_sources && symbolData.screener_sources.length > 0) {
      const screenerInfo = document.createElement('div');
      screenerInfo.className = 'screener-info';
      screenerInfo.innerHTML = `
        <p><strong>該当スクリーナー:</strong> ${symbolData.screener_sources.map(s => this.getScreenerDisplayName(s)).join(', ')}</p>
      `;
      resultDiv.appendChild(screenerInfo);
    }

    // チャート画像
    const chartDiv = document.createElement('div');
    chartDiv.className = 'search-result-chart';
    chartDiv.innerHTML = `
      <img src="${symbolData.analysis_data.gamma_plot}" alt="${ticker} Gamma Analysis" class="algo-chart-img-large">
    `;
    resultDiv.appendChild(chartDiv);

    // Gemini解説
    if (symbolData.gemini_analysis) {
      const analysisDiv = document.createElement('div');
      analysisDiv.className = 'search-result-analysis';
      analysisDiv.innerHTML = `
        <h3>AI解説 (Gemini)</h3>
        <p>${symbolData.gemini_analysis.replace(/\n/g, '<br>')}</p>
      `;
      resultDiv.appendChild(analysisDiv);
    } else if (symbolData.message) {
      const messageDiv = document.createElement('div');
      messageDiv.className = 'search-result-message';
      messageDiv.innerHTML = `<p>${symbolData.message}</p>`;
      resultDiv.appendChild(messageDiv);
    }

    container.appendChild(resultDiv);
  }

  resetToSummary() {
    this.currentView = 'summary';
    const input = document.getElementById('algo-ticker-input');
    if (input) input.value = '';

    const searchBtn = document.getElementById('algo-analyze-btn');
    if (searchBtn) {
      searchBtn.textContent = '検索';
      searchBtn.dataset.state = 'search';
    }

    this.render();

    const { updated_at, volatility_distribution } = this.summaryData;
    const displayDate = formatDateForDisplay(updated_at);

    this.showStatus(
      `最終更新: ${displayDate} | 緑: ${volatility_distribution.contraction} | 黄: ${volatility_distribution.transition} | 赤: ${volatility_distribution.expansion}`,
      'info'
    );
  }

  showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('algo-status');
    if (statusDiv) {
      statusDiv.textContent = message;
      statusDiv.className = `algo-status-info ${type}`;
    }
  }
}

// 初期化
function initAlgoTab() {
  window.algoManager = new AlgoManager();
  console.log('AlgoManager initialized');
}

// showDashboard内で呼び出し
if (document.getElementById('algo-content')) {
  initAlgoTab();
}

// タブ切り替え時にデータロード
if (targetTab === 'algo' && window.algoManager) {
  window.algoManager.loadData();
}
```

### 6.3 CSS追加

```css
/* ========================================
   Algoタブ - スクリーナーボタン
   ======================================== */
.screener-buttons {
  display: flex;
  gap: 8px;
  margin: 15px 0;
  flex-wrap: wrap;
}

.screener-btn {
  padding: 10px 15px;
  border: 2px solid #006B6B;
  background-color: white;
  color: #006B6B;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.screener-btn:hover {
  background-color: #E6F3F7;
}

.screener-btn.active {
  background-color: #006B6B;
  color: white;
}

/* ========================================
   Algoタブ - ボラティリティレジーム
   ======================================== */
.regime-contraction,
.regime-badge.regime-contraction {
  background-color: #4CAF50;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.regime-transition,
.regime-badge.regime-transition {
  background-color: #FFC107;
  color: #333;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.regime-expansion,
.regime-badge.regime-expansion {
  background-color: #F44336;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* ========================================
   Algoタブ - サマリー統計
   ======================================== */
.algo-summary-stats {
  margin: 20px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.stat-card {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  border: 2px solid transparent;
}

.stat-card.green {
  border-color: #4CAF50;
  background-color: #E8F5E9;
}

.stat-card.yellow {
  border-color: #FFC107;
  background-color: #FFF8E1;
}

.stat-card.red {
  border-color: #F44336;
  background-color: #FFEBEE;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

/* ========================================
   Algoタブ - 銘柄リスト
   ======================================== */
.algo-symbol-list {
  display: grid;
  gap: 20px;
  margin-top: 20px;
}

.algo-symbol-item {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s ease;
}

.algo-symbol-item:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.symbol-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.symbol-name {
  font-size: 18px;
  font-weight: 700;
  color: #006B6B;
}

.symbol-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.meta-badge {
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background-color: #e0e0e0;
  color: #333;
}

.meta-badge.rs-excellent {
  background-color: #4CAF50;
  color: white;
}

.meta-badge.rs-good {
  background-color: #2196F3;
  color: white;
}

.meta-badge.rs-average {
  background-color: #FFC107;
  color: #333;
}

.meta-badge.eps-badge {
  background-color: #9C27B0;
  color: white;
}

.meta-badge.vol-badge {
  background-color: #FF5722;
  color: white;
}

.meta-badge.move-badge {
  background-color: #607D8B;
  color: white;
}

.symbol-chart {
  width: 100%;
  margin-top: 10px;
}

.algo-chart-img {
  width: 100%;
  height: auto;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.algo-chart-img:hover {
  transform: scale(1.02);
}

/* ========================================
   Algoタブ - 画像ポップアップ
   ======================================== */
.algo-image-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.algo-popup-content {
  max-width: 1200px;
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  max-height: 90vh;
  overflow-y: auto;
}

.algo-popup-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  margin-bottom: 20px;
}

.algo-popup-analysis {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.algo-popup-analysis h3 {
  color: #006B6B;
  margin-bottom: 15px;
}

.algo-popup-analysis p {
  line-height: 1.8;
  color: #333;
}

.no-analysis {
  color: #999;
  font-style: italic;
}

/* ========================================
   Algoタブ - 検索結果
   ======================================== */
.algo-search-results {
  margin-top: 20px;
}

.search-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.screener-info {
  background-color: #E6F3F7;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.search-result-chart {
  margin: 20px 0;
}

.algo-chart-img-large {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.search-result-analysis {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.search-result-analysis h3 {
  color: #006B6B;
  margin-bottom: 15px;
}

.search-result-message {
  background-color: #FFF8E1;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #FFC107;
  margin-top: 15px;
}

/* ========================================
   Algoタブ - ステータスバー
   ======================================== */
.algo-status-info {
  padding: 10px 15px;
  border-radius: 6px;
  margin: 10px 0;
  font-size: 14px;
}

.algo-status-info.info {
  background-color: #E3F2FD;
  color: #1976D2;
  border-left: 4px solid #1976D2;
}

.algo-status-info.warning {
  background-color: #FFF8E1;
  color: #F57C00;
  border-left: 4px solid #F57C00;
}

.algo-status-info.error {
  background-color: #FFEBEE;
  color: #C62828;
  border-left: 4px solid #C62828;
}

/* ========================================
   Algoタブ - コントロール
   ======================================== */
.algo-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.ticker-input {
  flex: 1;
  padding: 10px 15px;
  border: 2px solid #006B6B;
  border-radius: 6px;
  font-size: 16px;
  text-transform: uppercase;
}

.analyze-btn {
  padding: 10px 20px;
  background-color: #006B6B;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.analyze-btn:hover {
  background-color: #005555;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-style: italic;
}
```

---

## 7. バックエンド実装

### 7.1 新規ファイル

#### 7.1.1 `backend/gemini_client.py`

Gemini APIの統一クライアント（すべてのAI解説生成をここで管理）:

```python
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
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        self.client = genai.Client(api_key=self.api_key)
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
```

#### 7.1.2 `backend/algo_data_manager.py`

Algoデータの読み書き管理:

```python
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
```

#### 7.1.3 `backend/algo_scanner.py`

MarketAlgoXのデータを取得し、StageAlgoで分析:

```python
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

from .gemini_client import gemini_client
from .algo_data_manager import AlgoDataManager

logger = logging.getLogger(__name__)

# StageAlgoリポジトリのパス（環境変数で設定）
STAGE_ALGO_PATH = os.getenv("STAGE_ALGO_PATH", "/app/StageAlgo")
# MarketAlgoXのデータディレクトリ
MARKET_ALGO_DATA_PATH = os.getenv("MARKET_ALGO_DATA_PATH", "/app/MarketAlgoX/data/screener_results")
# 画像保存先
CHARTS_ALGO_PATH = os.getenv("CHARTS_ALGO_PATH", "/app/frontend/charts/algo")

class AlgoScanner:
    def __init__(self):
        self.data_manager = AlgoDataManager()
        os.makedirs(CHARTS_ALGO_PATH, exist_ok=True)

    async def run_scan(self) -> Dict:
        """
        Algoスキャンを実行

        Returns:
            スキャン結果のサマリー
        """
        logger.info("Starting Algo scan...")

        # 1. MarketAlgoXのデータを取得
        market_data = self.load_market_algo_data()

        if not market_data:
            raise Exception("MarketAlgoX data not found")

        # 2. 各スクリーナーの銘柄を分析
        summary = {}
        volatility_distribution = {"contraction": 0, "transition": 0, "expansion": 0}

        for screener_key, symbols in market_data['screeners'].items():
            logger.info(f"Analyzing screener: {screener_key} ({len(symbols)} symbols)")

            analyzed_symbols = []

            for symbol_data in symbols:
                ticker = symbol_data['ticker']

                try:
                    # StageAlgoで分析
                    analysis_result = await self.analyze_symbol(ticker)

                    if analysis_result:
                        # スクリーナー情報をマージ
                        merged_data = {**symbol_data, **analysis_result}
                        analyzed_symbols.append(merged_data)

                        # ボラティリティ分布を集計
                        regime = analysis_result.get('volatility_regime', 'transition')
                        volatility_distribution[regime] += 1

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

                    # 個別銘柄データを保存
                    self.data_manager.save_symbol_data(ticker, {
                        **symbol_data,
                        'gemini_analysis': gemini_analysis,
                        'screener_sources': [screener_key],
                        'last_updated': datetime.now().isoformat()
                    })

            summary[screener_key] = analyzed_symbols

        # 3. サマリーを保存
        summary_data = {
            'scan_date': datetime.now().strftime('%Y-%m-%d'),
            'scan_time': datetime.now().strftime('%H:%M:%S'),
            'total_scanned': sum(len(symbols) for symbols in summary.values()),
            'summary': summary,
            'volatility_distribution': volatility_distribution,
            'updated_at': datetime.now().isoformat()
        }

        self.data_manager.save_daily_summary(summary_data)

        logger.info(f"Algo scan completed: {summary_data['total_scanned']} symbols analyzed")

        return summary_data

    def load_market_algo_data(self) -> Optional[Dict]:
        """MarketAlgoXの最新データを読み込み"""
        try:
            # 最新のJSONファイルを探す
            data_files = sorted(Path(MARKET_ALGO_DATA_PATH).glob('*.json'), reverse=True)

            if not data_files:
                logger.error("No MarketAlgoX data files found")
                return None

            latest_file = data_files[0]

            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"Loaded MarketAlgoX data from: {latest_file}")
            return data

        except Exception as e:
            logger.error(f"Error loading MarketAlgoX data: {e}")
            return None

    async def analyze_symbol(self, ticker: str) -> Optional[Dict]:
        """
        StageAlgoで銘柄を分析

        Args:
            ticker: ティッカーシンボル

        Returns:
            分析結果
        """
        try:
            # gamma_plotter.py を実行
            gamma_result = await self.run_gamma_plotter(ticker)

            # quantlib_ai_analyzer.py を実行
            ai_result = await self.run_quantlib_ai_analyzer(ticker)

            # quantlib_timeseries_analyzer.py を実行
            ts_result = await self.run_quantlib_timeseries_analyzer(ticker)

            # 結果をマージ
            return {
                'volatility_regime': ts_result.get('regime', 'transition'),
                'gamma_flip': gamma_result.get('zero_gamma_flip'),
                'expected_move_30d': ts_result.get('expected_move_30d'),
                'analysis_data': {
                    'gamma_plot': f'/charts/algo/{ticker}_gamma_analysis.png',
                    'timeseries_plot': f'/charts/algo/{ticker}_timeseries_analysis.png',
                    'ai_strategy': ai_result
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return None

    async def run_gamma_plotter(self, ticker: str) -> Dict:
        """gamma_plotter.pyを実行"""
        try:
            cmd = [
                'python',
                os.path.join(STAGE_ALGO_PATH, 'gamma_plotter.py'),
                ticker,
                '--output', CHARTS_ALGO_PATH
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # 結果をパース（スクリプトの出力形式に依存）
                # ここでは簡略化
                return {'zero_gamma_flip': 0.0}  # 実際はスクリプト出力から取得
            else:
                logger.error(f"gamma_plotter failed for {ticker}: {result.stderr}")
                return {}

        except Exception as e:
            logger.error(f"Error running gamma_plotter for {ticker}: {e}")
            return {}

    async def run_quantlib_ai_analyzer(self, ticker: str) -> Dict:
        """quantlib_ai_analyzer.pyを実行"""
        try:
            cmd = [
                'python',
                os.path.join(STAGE_ALGO_PATH, 'quantlib_ai_analyzer.py'),
                ticker,
                '--output', CHARTS_ALGO_PATH
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # JSONファイルから結果を読み込み
                json_path = os.path.join(CHARTS_ALGO_PATH, f'{ticker}_ai_analysis.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        return json.load(f)

            return {}

        except Exception as e:
            logger.error(f"Error running quantlib_ai_analyzer for {ticker}: {e}")
            return {}

    async def run_quantlib_timeseries_analyzer(self, ticker: str) -> Dict:
        """quantlib_timeseries_analyzer.pyを実行"""
        try:
            cmd = [
                'python',
                os.path.join(STAGE_ALGO_PATH, 'quantlib_timeseries_analyzer.py'),
                ticker,
                '--output', CHARTS_ALGO_PATH
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # 結果をパース
                return {'regime': 'transition', 'expected_move_30d': 0.0}  # 実際は出力から取得

            return {}

        except Exception as e:
            logger.error(f"Error running quantlib_timeseries_analyzer for {ticker}: {e}")
            return {}

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

# グローバルインスタンス
algo_scanner = AlgoScanner()

async def run_algo_scan() -> Dict:
    """Algoスキャンを実行（エントリーポイント）"""
    return await algo_scanner.run_scan()

async def analyze_single_ticker_algo(ticker: str) -> Optional[Dict]:
    """単一銘柄を分析（検索機能用）"""
    return await algo_scanner.analyze_symbol(ticker)
```

#### 7.1.4 `backend/cron_job_algo.sh`

Cronから実行されるシェルスクリプト:

```bash
#!/bin/bash

# Algoスキャンを実行するCronジョブ

set -e

echo "=========================================="
echo "Algo Scanner Starting: $(date)"
echo "=========================================="

# Pythonパスを設定
export PYTHONPATH=/app:$PYTHONPATH

# Algoスキャンを実行
python -c "
import asyncio
from backend.algo_scanner import run_algo_scan
from backend.data_fetcher import send_push_notifications_to_permission

async def main():
    try:
        result = await run_algo_scan()

        # ura権限ユーザーに通知
        total_signals = result['total_scanned']
        await send_push_notifications_to_permission(
            'ura',
            'Algoスキャン完了',
            f'新規シグナル: {total_signals}件'
        )

        print(f'✅ Algo scan completed: {total_signals} signals')

    except Exception as e:
        print(f'❌ Algo scan failed: {e}')
        raise

asyncio.run(main())
"

echo "=========================================="
echo "Algo Scanner Finished: $(date)"
echo "=========================================="
```

### 7.2 main.pyへの追加

既存の`backend/main.py`に以下のエンドポイントを追加:

```python
# Algoスキャン関連のインポート
from .algo_scanner import run_algo_scan, analyze_single_ticker_algo
from .algo_data_manager import AlgoDataManager

@app.post("/api/algo/scan")
async def trigger_algo_scan(payload: dict = Depends(get_current_user_payload)):
    """Algoスキャンを手動実行（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden: ura permission required")

    try:
        result = await run_algo_scan()

        # ura権限ユーザーに通知
        await _send_notifications_to_permission_level(
            "ura",
            "Algoスキャン完了",
            f"新規シグナル: {result['total_scanned']}件"
        )

        return {
            "success": True,
            "message": f"スキャン完了: {result['total_scanned']}件のシグナル検出",
            "scan_date": result['scan_date'],
            "scan_time": result['scan_time']
        }

    except Exception as e:
        logger.error(f"Algo scan error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"スキャンエラー: {str(e)}")


@app.get("/api/algo/daily/latest")
def get_algo_latest_summary(payload: dict = Depends(get_current_user_payload)):
    """Algoサマリー取得（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden: ura permission required")

    try:
        data_manager = AlgoDataManager()
        summary = data_manager.load_latest_summary()

        if not summary:
            raise HTTPException(status_code=404, detail="Latest summary not found")

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading Algo summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve Algo summary")


@app.get("/api/algo/symbols/{symbol}")
def get_algo_symbol_data(symbol: str, payload: dict = Depends(get_current_user_payload)):
    """個別銘柄データ取得（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden: ura permission required")

    try:
        # Basic validation
        if not re.match(r'^[A-Z0-9\-\.]+$', symbol.upper()):
            raise HTTPException(status_code=400, detail="Invalid symbol format")

        data_manager = AlgoDataManager()
        symbol_data = data_manager.load_symbol_data(symbol.upper())

        if not symbol_data:
            raise HTTPException(status_code=404, detail=f"Data for symbol '{symbol}' not found")

        return symbol_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading symbol data for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Could not retrieve data for symbol '{symbol}'")


@app.get("/api/algo/analyze_ticker")
async def analyze_ticker_algo(ticker: str, force: bool = False, payload: dict = Depends(get_current_user_payload)):
    """銘柄分析（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden: ura permission required")

    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required")

    try:
        symbol = ticker.strip().upper()
        data_manager = AlgoDataManager()

        if not force:
            # キャッシュデータを返す
            logger.info(f"Attempting to load cached data for {symbol}...")
            existing_data = data_manager.load_symbol_data(symbol)

            if existing_data:
                logger.info(f"Returning cached data for {symbol}")
                return existing_data
            else:
                logger.info(f"No cached data found for {symbol}")
                raise HTTPException(
                    status_code=404,
                    detail=f"分析データが見つかりません。新規に分析しますか？"
                )

        # force=true の場合、新規分析を実行
        logger.info(f"Force analyzing {symbol}...")
        analysis_result = await analyze_single_ticker_algo(symbol)

        if not analysis_result:
            raise HTTPException(
                status_code=404,
                detail=f"{symbol}の分析に失敗しました"
            )

        # スクリーナーに含まれていないため、Gemini解説なし
        symbol_data = {
            'symbol': symbol,
            **analysis_result,
            'gemini_analysis': None,
            'screener_sources': [],
            'metadata': {},
            'message': 'この銘柄はスクリーナーに含まれていません。チャート分析のみ表示します。',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

        # キャッシュに保存
        data_manager.save_symbol_data(symbol, symbol_data)

        return symbol_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing ticker {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析中に予期せぬエラーが発生しました")
```

### 7.3 app.jsの権限制御追加

既存の`applyTabPermissions()`関数に追加:

```javascript
function applyTabPermissions() {
    const permission = AuthManager.getPermission();
    const hwb200Tab = document.querySelector('.tab-button[data-tab="hwb200"]');
    const algoTab = document.querySelector('.tab-button[data-tab="algo"]');

    console.log(`Applying permissions for level: ${permission}`);

    if (hwb200Tab) hwb200Tab.style.display = '';
    if (algoTab) algoTab.style.display = '';

    if (permission === 'standard') {
        console.log("Standard permission: Hiding 200MA and Algo tabs.");
        if (hwb200Tab) hwb200Tab.style.display = 'none';
        if (algoTab) algoTab.style.display = 'none';
    } else if (permission === 'secret') {
        console.log("Secret permission: Hiding Algo tab.");
        if (algoTab) algoTab.style.display = 'none';
    } else if (permission === 'ura') {
        console.log("Ura permission: All tabs visible.");
    }
}
```

---

## 8. Gemini API統一対応

### 8.1 既存のOpenAI呼び出しの置き換え

**影響範囲**:
- `backend/data_fetcher.py`: AI解説生成部分（Fear & Greed、ニュースサマリー、経済指標解説など）

**変更内容**:
```python
# backend/data_fetcher.pyの冒頭に追加
from .gemini_client import gemini_client

# すべてのOpenAI呼び出しを以下のように置き換え

# Before (OpenAI)
import openai
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)
ai_commentary = response.choices[0].message.content

# After (Gemini)
ai_commentary = gemini_client.generate_content(prompt)
```

### 8.2 環境変数の追加

`.env`ファイルに追加:
```
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# StageAlgo & MarketAlgoX paths
STAGE_ALGO_PATH=/app/StageAlgo
MARKET_ALGO_DATA_PATH=/app/MarketAlgoX/data/screener_results
CHARTS_ALGO_PATH=/app/frontend/charts/algo
```

---

## 9. 依存ライブラリ

### 9.1 新規追加ライブラリ（requirements.txtに追加済み）

```
google-genai>=0.8.3             # Gemini API（google-generativeaiは非推奨）
QuantLib>=1.40                  # QuantLib for financial analysis
scipy>=1.17.0                   # Scientific computing
pandas-ta>=0.3.14b              # Technical analysis (StageAlgo依存)
```

### 9.2 StageAlgo依存関係

StageAlgoは以下のライブラリを使用（requirements.txtに含める）:
- yfinance
- curl-cffi
- pandas
- numpy
- pandas-ta
- scipy
- tqdm
- pytz
- python-dotenv
- Pillow

これらはすでにrequirements.txtに含まれているため、追加不要。

---

## 10. Docker & Git統合

### 10.1 Dockerfileの更新

```dockerfile
# StageAlgoとMarketAlgoXをクローン
RUN cd /app && \
    git clone https://github.com/turnDeep/StageAlgo.git && \
    git clone https://github.com/turnDeep/MarketAlgoX.git

# StageAlgoの依存関係をインストール
RUN pip install --no-cache-dir -r /app/StageAlgo/requirements.txt

# cron_job_algo.shを実行可能にする
RUN chmod +x /app/backend/cron_job_algo.sh

# Cronジョブに追加
RUN ( \
    echo "SHELL=/bin/bash" ; \
    echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" ; \
    echo "TZ=Asia/Tokyo" ; \
    echo "" ; \
    echo "15 6 * * 1-5 . /app/backend/cron-env.sh && /app/backend/run_job.sh fetch >> /app/logs/cron_error.log 2>&1" ; \
    echo "28 6 * * 1-5 . /app/backend/cron-env.sh && /app/backend/run_job.sh generate >> /app/logs/cron_error.log 2>&1" ; \
    echo "35 6 * * 1-5 . /app/backend/cron-env.sh && /app/backend/cron_job_hwb.sh >> /app/logs/cron_error.log 2>&1" ; \
    echo "0 8 * * 1-5 . /app/backend/cron-env.sh && /app/backend/cron_job_algo.sh >> /app/logs/cron_error.log 2>&1" \
) | crontab -

# chartsディレクトリ作成
RUN mkdir -p /app/frontend/charts/algo
```

---

## 11. テストケース

### 11.1 認証テスト

- [ ] standardユーザーはAlgoタブが見えない
- [ ] secretユーザーはAlgoタブが見えない
- [ ] uraユーザーのみAlgoタブが見える
- [ ] Algoタブへのダイレクトアクセス（URL直打ち）も権限チェック

### 11.2 スクリーナー切り替えテスト

- [ ] 6つのボタンがすべて表示される
- [ ] 各ボタンクリックで対応するリストが表示される
- [ ] アクティブボタンのハイライト表示
- [ ] 銘柄数が正しく表示される

### 11.3 ボラティリティソート順テスト

- [ ] 緑（Contraction）が最上位
- [ ] 黄（Transition）が中間
- [ ] 赤（Expansion）が最下位
- [ ] ボラティリティバッジの色分けが正しい

### 11.4 画像拡大テスト

- [ ] ダブルタップで拡大表示
- [ ] Gemini解説が表示される（スクリーナー該当銘柄のみ）
- [ ] オーバーレイクリックで閉じる
- [ ] 画像が正しく表示される（gamma_analysis.png）

### 11.5 検索機能テスト

- [ ] スクリーナー該当銘柄を検索できる
- [ ] 該当銘柄の詳細とGemini解説が表示される
- [ ] 該当なしの場合、確認ダイアログが表示される
- [ ] force=trueで画像が生成される
- [ ] 該当なしの場合、Gemini解説は表示されない
- [ ] リセットボタンで元の画面に戻る

### 11.6 Cronジョブテスト

- [ ] 月〜金の8時に実行される
- [ ] MarketAlgoXデータが正しく読み込まれる
- [ ] StageAlgo分析ツールが正常に実行される
- [ ] 画像ファイルが生成される
- [ ] Gemini解説が生成される
- [ ] JSONファイルが保存される
- [ ] ura権限ユーザーに通知が届く

### 11.7 Gemini API統一テスト

- [ ] 既存のAI解説（Fear & Greed、ニュースなど）がGeminiに置き換わっている
- [ ] Algoタブの解説がGeminiで生成される
- [ ] エラーハンドリングが機能する
- [ ] レート制限に対応している

### 11.8 パフォーマンステスト

- [ ] 100銘柄の分析が30分以内に完了する
- [ ] 画像ファイルサイズが適切（1MB以下）
- [ ] JSONファイルサイズが適切
- [ ] フロントエンドのロード時間が3秒以内

---

## 12. マイルストーン

### Phase 1: 環境準備（完了）
- [x] MarketAlgoXリポジトリの6スクリーナー仕様確認
- [x] StageAlgoリポジトリの分析ツール仕様確認
- [x] 依存ライブラリのバージョン調査
- [x] requirements.txt更新

### Phase 2: Gemini API統一
- [ ] gemini_client.py実装
- [ ] 既存OpenAI呼び出しのGemini置き換え（data_fetcher.py）
- [ ] 動作確認
- [ ] エラーハンドリング強化

### Phase 3: バックエンド実装
- [ ] algo_data_manager.py実装
- [ ] algo_scanner.py実装
  - [ ] MarketAlgoXデータ読み込み
  - [ ] StageAlgo分析ツール実行
  - [ ] ボラティリティレジーム分類
  - [ ] Gemini解説生成
- [ ] main.pyへのエンドポイント追加
- [ ] cron_job_algo.sh作成
- [ ] 単体テスト

### Phase 4: フロントエンド実装
- [ ] HTML追加（index.html）
- [ ] CSS追加（styles.css）
- [ ] AlgoManager JavaScript実装（app.js）
  - [ ] データロード機能
  - [ ] スクリーナー切り替え
  - [ ] ボラティリティソート
  - [ ] 画像ポップアップ
  - [ ] 検索機能
- [ ] 権限制御の追加（applyTabPermissions）

### Phase 5: Docker & Git統合
- [ ] Dockerfile更新（StageAlgo & MarketAlgoXクローン）
- [ ] docker-compose.yml確認
- [ ] Cronジョブ設定
- [ ] 環境変数設定（.env）

### Phase 6: 統合テスト
- [ ] 全機能の動作確認
- [ ] 認証・権限テスト
- [ ] Cronジョブテスト（手動実行）
- [ ] Push通知テスト
- [ ] パフォーマンステスト

### Phase 7: デプロイ
- [ ] 本番環境デプロイ
- [ ] モニタリング設定
- [ ] ログ確認
- [ ] 初回Cronジョブ実行確認

---

## 13. リスク・注意事項

### 13.1 外部リポジトリ依存

- **リスク**: MarketAlgoXとStageAlgoのコードが変更された場合、互換性が失われる可能性
- **対策**:
  - 特定のコミットハッシュまたはタグを指定してクローン
  - 定期的な動作確認
  - バージョン管理

### 13.2 Gemini API制限

- **リスク**: レート制限、コスト増大
- **対策**:
  - リトライ機構の実装（gemini_client.py）
  - 1日の分析銘柄数を制限（最大150銘柄程度）
  - エラー時のフォールバック（解説なしで画像のみ表示）

### 13.3 パフォーマンス

- **リスク**: 150銘柄 × 3ツール = 450回の分析実行で時間がかかる
- **対策**:
  - 並列処理の導入（asyncio、multiprocessing）
  - キャッシュ戦略（既存分析の再利用）
  - タイムアウト設定（各分析60秒）

### 13.4 データ保存容量

- **リスク**: 画像ファイルの蓄積（1日150枚 × 365日 = 54,750枚/年）
- **対策**:
  - 画像圧縮（PNG → WebP）
  - 古いデータの定期削除（30日以上前）
  - アーカイブ戦略

### 13.5 MarketAlgoX実行タイミング

- **リスク**: MarketAlgoXが6時に実行されるが、完了時刻が不明
- **対策**:
  - Algoスキャンを8時に実行し、2時間のバッファを確保
  - MarketAlgoXデータが見つからない場合はリトライ
  - 最大3回リトライ（10分間隔）

---

## 14. 今後の拡張性

- **スクリーナーのカスタマイズ**: ユーザー独自のフィルター条件設定
- **アラート機能**: 特定の条件でPush通知
- **バックテスト**: 過去のスクリーナー結果と実際のパフォーマンス比較
- **ポートフォリオ管理**: スクリーナー銘柄をウォッチリストに追加
- **詳細分析レポート**: PDFエクスポート機能

---

**作成日**: 2025-12-21
**最終更新**: 2025-12-21
**バージョン**: 2.0 (MarketAlgoX & StageAlgo調査完了版)
**作成者**: Claude (Anthropic)
