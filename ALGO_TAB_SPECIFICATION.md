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

MarketAlgoXリポジトリ (https://github.com/turnDeep/MarketAlgoX) から以下の6つのスクリーナーを利用:

1. **スクリーナー1** - 名称はMarketAlgoXリポジトリから確認
2. **スクリーナー2** - 名称はMarketAlgoXリポジトリから確認
3. **スクリーナー3** - 名称はMarketAlgoXリポジトリから確認
4. **スクリーナー4** - 名称はMarketAlgoXリポジトリから確認
5. **スクリーナー5** - 名称はMarketAlgoXリポジトリから確認
6. **スクリーナー6** - 名称はMarketAlgoXリポジトリから確認

### 1.3 分析ツール

StageAlgoリポジトリ (https://github.com/turnDeep/StageAlgo) から以下のツールを利用:

1. **gamma_plotter.py** - ガンマプロット画像生成
2. **quantlib_ai_analyzer.py** - QuantLibベースのAI分析
3. **quantlib_timeseries_analyzer.py** - QuantLibベースの時系列分析

### 1.4 UI/UX設計

#### 1.4.1 スクリーナー切り替えボタン

- **配置**: 200MAタブの「当日ブレイクアウト」「直近5営業日」「監視銘柄」ボタンと同じ位置
- **構成**: 6つのボタンを横並びで配置
- **動作**:
  - 各ボタンをクリックすると、対応するスクリーナーの結果リストを表示
  - アクティブなボタンはハイライト表示

#### 1.4.2 銘柄リスト表示

**リストアイテム構成**:
- 銘柄名 (ティッカーシンボル)
- 分析画像 (gamma_plotter.py等で生成)
- ボラティリティステータスインジケーター

**ソート順** (上から順に):
1. 🟢 **緑色 (Low Vol)**: 「凪（なぎ）」の状態
2. 🟡 **黄色 (Normal)**: 通常運転の状態
3. 🔴 **赤色 (High Vol)**: 「嵐（パニック）」の状態

**画像の操作**:
- **ダブルタップ**: 画像を拡大表示 + Gemini APIによる解説テキストを表示
- 拡大表示時は背景オーバーレイで他のコンテンツを隠す
- オーバーレイクリックで元の画面に戻る

#### 1.4.3 検索機能

**動作仕様**:
1. 検索ボックスにティッカーシンボルを入力
2. 全6スクリーナーのリストから該当銘柄を検索
3. **該当あり**: その銘柄のリストを表示
4. **該当なし**:
   - その場でStageAlgoのツールを実行し、画像を生成
   - 生成した画像を表示
   - **重要**: スクリーナーにない銘柄はGemini解説を出力しない（画像のみ表示）

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

### 2.2 Push通知

- **対象者**: `ura` 権限保持者のみ
- **通知内容**: Algoスキャン完了時に新規シグナル数を通知

---

## 3. Cronジョブ設定

### 3.1 実行スケジュール

```
月曜日〜金曜日の朝8時 (JST)
```

### 3.2 実行内容

1. MarketAlgoXの6つのスクリーナーを実行
2. 抽出された銘柄に対してStageAlgoの分析を実行
3. 画像生成 (gamma_plotter.py, quantlib_ai_analyzer.py, quantlib_timeseries_analyzer.py)
4. Gemini APIで解説生成
5. データをJSONファイルに保存
6. ura権限ユーザーにPush通知を送信

### 3.3 Cronエントリ例

```bash
0 8 * * 1-5 . /app/backend/cron-env.sh && /app/backend/cron_job_algo.sh >> /app/logs/cron_error.log 2>&1
```

---

## 4. API設計

### 4.1 Gemini API統一

**重要**: OpenAI APIからGemini APIに全面移行

- **使用モデル**: `gemini-3-flash-preview`
- **API呼び出し**: `google-generativeai` ライブラリを使用
- **既存のOpenAI API呼び出しをすべてGemini APIに置き換える**

### 4.2 バックエンドAPIエンドポイント

#### 4.2.1 Algoスキャンデータ取得

```
GET /api/algo/daily/latest
```

**レスポンス例**:
```json
{
  "scan_date": "2025-12-21",
  "scan_time": "08:00:00",
  "total_scanned": 150,
  "summary": {
    "screener_1": [...],
    "screener_2": [...],
    "screener_3": [...],
    "screener_4": [...],
    "screener_5": [...],
    "screener_6": [...]
  },
  "updated_at": "2025-12-21T08:30:00Z"
}
```

#### 4.2.2 個別銘柄データ取得

```
GET /api/algo/symbols/{symbol}
```

**レスポンス例**:
```json
{
  "symbol": "AAPL",
  "volatility_status": "low",  // low, normal, high
  "analysis_data": {
    "gamma_plot": "/charts/algo/AAPL_gamma.png",
    "quantlib_ai": "/charts/algo/AAPL_quantlib_ai.png",
    "quantlib_ts": "/charts/algo/AAPL_quantlib_ts.png"
  },
  "gemini_analysis": "Geminiによる解説テキスト...",
  "screener_sources": ["screener_1", "screener_3"]
}
```

#### 4.2.3 銘柄検索・オンデマンド分析

```
GET /api/algo/analyze_ticker?ticker={SYMBOL}&force={true|false}
```

**動作**:
- `force=false` (デフォルト): キャッシュデータを返す、なければ404
- `force=true`: 強制的に新規分析を実行

**レスポンス**:
- スクリーナーにある場合: 完全な分析データ + Gemini解説
- スクリーナーにない場合: 画像のみ、Gemini解説なし

#### 4.2.4 手動スキャン実行 (管理者用)

```
POST /api/algo/scan
```

**権限**: `ura` のみ

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
│       ├── AAPL.json                      # 個別銘柄データ
│       ├── TSLA.json
│       └── ...
frontend/
└── charts/
    └── algo/
        ├── AAPL_gamma.png                 # ガンマプロット
        ├── AAPL_quantlib_ai.png           # QuantLib AI分析
        ├── AAPL_quantlib_ts.png           # QuantLib時系列分析
        └── ...
```

### 5.2 ボラティリティ判定基準

```python
# 仮の基準（実際の基準はStageAlgoリポジトリから取得）
def classify_volatility(volatility_value):
    if volatility_value < 0.15:
        return "low"    # 緑色
    elif volatility_value < 0.30:
        return "normal" # 黄色
    else:
        return "high"   # 赤色
```

---

## 6. フロントエンド実装

### 6.1 HTML構造 (index.html追加部分)

```html
<!-- Algoタブボタン -->
<button class="tab-button" data-tab="algo">Algo</button>

<!-- Algoタブコンテンツ -->
<div id="algo-content" class="tab-pane">
  <div class="hwb-controls">
    <input type="text" id="algo-ticker-input" placeholder="ティッカー検索...">
    <button id="algo-analyze-btn">検索</button>
  </div>
  <div id="algo-status" class="hwb-status-info"></div>
  <div id="algo-content-area"></div>
</div>
```

### 6.2 JavaScript実装 (app.js追加部分)

```javascript
class AlgoManager {
  constructor() {
    this.summaryData = null;
    this.currentView = 'summary';
    this.activeScreener = 'screener_1'; // デフォルト
    this.initEventListeners();
  }

  async loadData() {
    // /api/algo/daily/latest からデータ取得
  }

  renderScreenerButtons(container) {
    // 6つのスクリーナーボタンを描画
  }

  renderSymbolList(container, items) {
    // ボラティリティ順にソートして表示
    // 緑 -> 黄 -> 赤
  }

  addDoubleTapListener(element, symbol) {
    // ダブルタップで画像拡大 + Gemini解説表示
  }

  async searchTicker(ticker) {
    // 検索機能の実装
    // スクリーナーにあれば表示
    // なければforce=trueで分析実行（解説なし）
  }
}
```

### 6.3 CSS追加

```css
/* ボラティリティステータスの色分け */
.volatility-low {
  background-color: #4CAF50; /* 緑 */
}

.volatility-normal {
  background-color: #FFC107; /* 黄 */
}

.volatility-high {
  background-color: #F44336; /* 赤 */
}

/* Algoタブの画像ポップアップ */
.algo-image-popup-overlay {
  /* 200MAと同じスタイル */
}

.algo-image-popup-content {
  /* 拡大画像 + Gemini解説エリア */
}
```

---

## 7. バックエンド実装

### 7.1 新規ファイル

#### 7.1.1 `backend/algo_scanner.py`

- MarketAlgoXのスクリーナーを実行
- StageAlgoの分析ツールを呼び出し
- Gemini APIで解説生成
- データを保存

#### 7.1.2 `backend/algo_data_manager.py`

- Algoデータの読み書き管理
- latest.jsonの更新
- 個別銘柄データの管理

#### 7.1.3 `backend/gemini_client.py`

- Gemini API呼び出しの統一インターフェース
- エラーハンドリング
- レート制限対応

#### 7.1.4 `backend/cron_job_algo.sh`

- Cronから実行されるシェルスクリプト
- algo_scanner.pyを実行
- ログ出力

### 7.2 main.pyへの追加

```python
from .algo_scanner import run_algo_scan, analyze_single_ticker_algo
from .algo_data_manager import AlgoDataManager

@app.post("/api/algo/scan")
async def trigger_algo_scan(payload: dict = Depends(get_current_user_payload)):
    """Algoスキャンを手動実行（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden")

    result = await run_algo_scan()

    # ura権限ユーザーに通知
    await _send_notifications_to_permission_level(
        "ura",
        "Algoスキャン完了",
        f"新規シグナル: {result['summary']['total_signals']}件"
    )

    return {
        "success": True,
        "message": f"スキャン完了: {result['summary']['total_signals']}件のシグナル検出",
        "scan_date": result['scan_date'],
        "scan_time": result['scan_time']
    }

@app.get("/api/algo/daily/latest")
def get_algo_latest_summary(payload: dict = Depends(get_current_user_payload)):
    """Algoサマリー取得（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # データ取得処理...

@app.get("/api/algo/symbols/{symbol}")
def get_algo_symbol_data(symbol: str, payload: dict = Depends(get_current_user_payload)):
    """個別銘柄データ取得（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # データ取得処理...

@app.get("/api/algo/analyze_ticker")
async def analyze_ticker_algo(ticker: str, force: bool = False, payload: dict = Depends(get_current_user_payload)):
    """銘柄分析（ura権限のみ）"""
    if payload.get("permission") != "ura":
        raise HTTPException(status_code=403, detail="Access forbidden")

    # 分析処理...
```

---

## 8. Gemini API統一対応

### 8.1 既存のOpenAI呼び出しの置き換え

**影響範囲**:
- `backend/data_fetcher.py`: AI解説生成部分
- その他OpenAI APIを使用している箇所

**変更内容**:
```python
# Before (OpenAI)
import openai
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...]
)

# After (Gemini)
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview')
response = model.generate_content(prompt)
```

### 8.2 環境変数の追加

`.env`ファイルに追加:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 9. 依存ライブラリ

### 9.1 新規追加ライブラリ

```
google-generativeai>=0.8.3      # Gemini API
QuantLib>=1.35                  # QuantLib (quantlib_*_analyzer.py用)
QuantLib-Python>=1.35           # QuantLib Python bindings
scipy>=1.14.1                   # 科学計算
```

### 9.2 既存ライブラリの更新

すべてのライブラリを最新版に更新:
- fastapi
- uvicorn
- pandas
- numpy
- matplotlib
- plotly
- yfinance
- beautifulsoup4
- その他

---

## 10. テストケース

### 10.1 認証テスト

- [ ] standardユーザーはAlgoタブが見えない
- [ ] secretユーザーはAlgoタブが見えない
- [ ] uraユーザーのみAlgoタブが見える

### 10.2 スクリーナー切り替えテスト

- [ ] 6つのボタンがすべて表示される
- [ ] 各ボタンクリックで対応するリストが表示される
- [ ] アクティブボタンのハイライト表示

### 10.3 ソート順テスト

- [ ] 緑（Low Vol）が最上位
- [ ] 黄（Normal）が中間
- [ ] 赤（High Vol）が最下位

### 10.4 画像拡大テスト

- [ ] ダブルタップで拡大表示
- [ ] Gemini解説が表示される（スクリーナー該当銘柄のみ）
- [ ] オーバーレイクリックで閉じる

### 10.5 検索機能テスト

- [ ] スクリーナー該当銘柄を検索できる
- [ ] 該当なしの場合、画像が生成される
- [ ] 該当なしの場合、Gemini解説は表示されない

### 10.6 Cronジョブテスト

- [ ] 月〜金の8時に実行される
- [ ] スキャンが正常に完了する
- [ ] ura権限ユーザーに通知が届く

### 10.7 Gemini API統一テスト

- [ ] 既存のAI解説がGeminiに置き換わっている
- [ ] エラーハンドリングが機能する
- [ ] レート制限に対応している

---

## 11. マイルストーン

### Phase 1: 調査・準備
- [ ] MarketAlgoXリポジトリの6スクリーナー仕様確認
- [ ] StageAlgoリポジトリの分析ツール仕様確認
- [ ] 依存ライブラリのバージョン調査
- [ ] requirements.txt更新

### Phase 2: Gemini API統一
- [ ] gemini_client.py実装
- [ ] 既存OpenAI呼び出しのGemini置き換え
- [ ] 動作確認

### Phase 3: バックエンド実装
- [ ] algo_data_manager.py実装
- [ ] algo_scanner.py実装
- [ ] main.pyへのエンドポイント追加
- [ ] cron_job_algo.sh作成

### Phase 4: フロントエンド実装
- [ ] HTML追加（タブ、コンテンツエリア）
- [ ] CSS追加（ボラティリティ色分け、ポップアップ）
- [ ] AlgoManager JavaScript実装
- [ ] 権限制御の追加

### Phase 5: 統合テスト
- [ ] 全機能の動作確認
- [ ] 認証・権限テスト
- [ ] Cronジョブテスト
- [ ] Push通知テスト

### Phase 6: デプロイ
- [ ] Dockerfile更新
- [ ] docker-compose.yml更新
- [ ] 本番環境デプロイ
- [ ] モニタリング設定

---

## 12. リスク・注意事項

### 12.1 外部リポジトリ依存

- MarketAlgoXとStageAlgoのコードが変更された場合の対応
- サブモジュールまたはパッケージとしての管理を検討

### 12.2 Gemini API制限

- レート制限への対応
- コスト管理
- フォールバック機構の検討

### 12.3 パフォーマンス

- 6つのスクリーナー × 多数の銘柄の処理時間
- 画像生成の並列化
- キャッシュ戦略

### 12.4 データ保存容量

- 画像ファイルの蓄積による容量増加
- 古いデータの定期的なアーカイブ・削除

---

## 13. 今後の拡張性

- スクリーナーのカスタマイズ機能
- アラート条件の設定
- バックテスト機能
- ポートフォリオ管理との連携

---

**作成日**: 2025-12-21
**バージョン**: 1.0
**作成者**: Claude (Anthropic)
