# DailyRead Automation Prompt

每天 06:00 執行一次 DailyRead。

## 目的

這不是正式文獻回顧，也不是特別對應 Morris 當前研究。這是一份研究新聞播報式 paper digest，用來追蹤以下領域最近 paper / research content 怎麼發展、內容在做什麼：

1. Silicon Sampling / Social Simulation
2. Harness Engineering
3. Agent Memory

Morris 看到有興趣的內容後會自己深讀。

## 搜尋入口

優先使用 Lab SearXNG：

- Base URL: `http://192.168.1.18:8888`
- Search endpoint: `http://192.168.1.18:8888/search?q={query}&format=json`

可搭配 arXiv / Semantic Scholar / web_fetch 取得 metadata、abstract 與可讀內容。

## 寫作方式

不要做卡片式摘要。每篇 paper 要像「かに讀完後講給 Morris 聽」。DailyRead 的 domain notes 必須保留 2026-05-08 到 2026-05-12 silicon sampling 筆記那種固定講解骨架，而不是只寫一段簡短心得。

每篇 paper / article 的標準格式：

```markdown
## N. Paper / Article Title

- **arXiv / Venue / 類型**: ...
- **Link**: ...

### 這篇在說什麼
用自己的話重講 abstract / 主旨：研究問題是什麼、作者為什麼要做、這篇在領域脈絡中想補哪個洞。

### 主要貢獻
條列或短段落說清楚 2–4 個貢獻。不要只寫「提出新方法」；要說新在哪裡、解決什麼限制。

### 方法 / pipeline
說明方法、架構、prompt / simulator / benchmark / harness pipeline。若是系統或 framework，要說資料流、控制流、agent loop、memory / tool / environment 如何互動。

### 實驗設計
說明 dataset、benchmark、baseline、metric、main result、ablation / sensitivity analysis。若資訊不足，明確寫「目前只從 abstract / landing page 能確認到 X，還看不到 Y」，不要編造。

### かに讀後判斷
具體說明這篇的位置、和前幾天 / 既有 paper 的關係、是否值得 Morris 點開，以及深讀時優先看哪些 section / figure / table。
```

Harness Engineering 可納入 blog、docs、GitHub repo、framework。若不是 paper，也要保留同樣標題，但調整內容：

- `這篇在說什麼` → 這篇文章 / repo 在解決什麼工程問題
- `主要貢獻` → 對 harness / eval / workflow 的新貢獻
- `方法 / pipeline` → 工程設計、架構、agent loop、工具介面、observability、evaluation workflow
- `實驗設計` → 若無正式實驗，寫 benchmark / demo / case study / hidden tests / 評估方法；若都沒有，明確說缺少什麼證據
- `かに讀後判斷` → 是否值得收藏或細看、適合拿來改進哪類 agent workflow


## 深度最低標準

DailyRead 的品質重點是「講解深度」，不是 paper 數量。即使今天每個 domain 只有 1–2 篇，也不能寫成短摘要或卡片。

### 讀取全文規則

DailyRead 不是 deepread，但不能只依 abstract 假裝已讀完。每篇被納入 domain note 前，必須先盡力取得可讀全文：

1. arXiv paper：優先抓 arXiv PDF / e-print 並抽文字；其次用 ar5iv / HTML；最後才用 abstract。
2. ACM / blog / repo：優先讀可公開取得的完整 HTML / README / docs；若被 paywall、登入或格式阻擋，才退回 abstract / landing page。
3. 今日推薦點開：必須讀到 PDF / full HTML / repo README 等「全文級材料」後才可列為推薦；若只讀到 abstract，不可列為今日推薦，只能放候選或略過。
4. 一般收錄篇：若只能讀到 abstract，必須明確標示為「僅 abstract 層級快速掃描」，並降低判斷強度；不要寫成像已完整檢查方法與實驗。
5. 不要反覆使用「目前從 abstract 和 HTML 前段能確認...需要看全文」這種模板句。應具體說明：已讀來源是什麼、缺少哪個 section / table / figure / artifact、為什麼缺少會影響判斷。

如果全文抓取失敗，必須在 `logs/YYYY-MM-DD.log` 記錄嘗試過的來源與失敗原因。

每一篇被納入 domain note 的內容，至少要用明確小標題包含：

1. `### 這篇在說什麼`：這篇到底在補哪個缺口？為什麼這個問題重要？
2. `### 主要貢獻`：它的新貢獻是什麼，和既有研究相比新在哪。
3. `### 方法 / pipeline`：作者怎麼做；若是 benchmark，要說 task construction、evaluation protocol、scoring；若是 harness/blog/repo，要說工程架構與 workflow。
4. `### 實驗設計`：dataset、benchmark、baseline、metric、main result；如果只讀到 abstract / landing page，就明確寫「目前能確認到的證據只有哪些」，不要用一句話帶過。
5. `### かに讀後判斷`：具體說明值得/不值得 Morris 點開的理由、和前幾天/既有 paper 的關係，以及如果要深讀應優先看哪些 section / figure / table。

不可把以上內容壓成單段敘述；若缺任何一個小標題，該 domain note 視為未完成，必須補齊後才能 commit。

篇幅原則：

- 今日推薦點開：每篇至少 500–800 中文字，必須有完整方法與實驗解釋。
- 一般收錄篇：每篇至少 300–500 中文字；若資料不足，也要解釋資訊不足在哪裡、還需要查什麼。
- 每個 domain note 不應只列 bullet；需要有連貫段落，把 paper 的主旨講清楚。
- `daily/YYYY-MM-DD.md` 可以維持短總覽，但 domain notes 必須是可讀的研究講解。

## 產出位置

在 repo `/Users/morris/Desktop/Repo/DailyRead` 中更新：

- `daily/YYYY-MM-DD.md`：今日總覽與推薦點開
- `silicon-sampling-social-simulation/YYYY-MM-DD.md`
- `harness-engineering/YYYY-MM-DD.md`
- `agent-memory/YYYY-MM-DD.md`
- `logs/YYYY-MM-DD.log`
- `raw/search-YYYY-MM-DD.json`
- `assets/YYYY-MM-DD/*.png`：只替「今日推薦點開」的 1–3 篇產生筆記圖，不替所有候選產圖

## 數量原則

每天不硬湊數量。預設：

- 每個 domain 1–3 則高品質內容
- 若某 domain 沒有高品質候選，明確寫今日無高品質候選
- 優先挑能說清楚方法與實驗設計的 paper

## 本地 Paper Memory / 查重

DailyRead 使用 Mac mini 本地的 Graphify + NetworkX paper memory 作為查重與跨 paper/domain knowledge 記憶層。這個 graph 是本地資料，不進 DailyRead git。

本地位置：

- `/Users/morris/.graphify/dailyread-paper-kg/graphify-out/graph.json`
- `/Users/morris/.graphify/dailyread-paper-kg/graphify-out/paper_index.json`
- `/Users/morris/.graphify/dailyread-paper-kg/graphify-out/GRAPH_REPORT.md`
- `/Users/morris/.graphify/dailyread-paper-kg/graphify-out/graph.html`

在挑選今日推薦或 domain note 候選前，必須先查重：

```bash
/Users/morris/.graphify/dailyread-paper-kg/check_paper_seen.py <arxiv-id-or-title-or-url>
```

規則：

- arXiv ID 優先；若沒有 arXiv ID，用 normalized title 查。
- 若結果是 `SEEN`，不要把它當成新的今日推薦；除非它是重要更新，且必須明確標成「更新 / follow-up」，不可寫成新 paper。
- 若結果是 `NOT_SEEN`，才可作為新候選。
- DailyRead 完成後，重建本地 graph，讓今日讀過 / 推薦過 / 提到過的 paper 進入後續查重：

```bash
/Users/morris/.local/share/uv/tools/graphifyy/bin/python3 /Users/morris/.graphify/dailyread-paper-kg/build_paper_graph.py
graphify global add /Users/morris/.graphify/dailyread-paper-kg/graphify-out/graph.json --as DailyRead-paper-kg
```

若 graph build 失敗，不要阻塞 DailyRead commit；但必須在 `logs/YYYY-MM-DD.log` 記錄錯誤，並在 Discord 短回報中說明 graph update 失敗。

## DailyRead 筆記圖（推薦篇限定）

每天只替 `daily/YYYY-MM-DD.md` 中「今日推薦點開」的 1–3 篇產圖，不替所有候選 paper / article 產圖，避免任務太久、圖片品質不穩、repo 變太肥。

### 產圖策略

- 產圖預設固定使用 `openai/gpt-image-2`；除非該模型不可用，才可明確記錄原因後 fallback。
- 圖片可以使用英文文字，不必強制繁體中文；以清楚、穩定、可讀為優先。
- 每張圖只表達該 paper / article 的核心 takeaway，不嘗試塞完整摘要。
- 依內容類型選圖：
  - 抽象 / 理論 paper：產「concept map / method flow diagram」。
  - 系統 / framework / infrastructure paper：產「pipeline note diagram」。
  - survey / taxonomy paper：產「classification tree note diagram」。
  - blog / repo / engineering article：產「architecture / workflow note diagram」。
- 風格：research notebook / clean handwritten study note；可用 highlight、arrows、small icons，但不要做商業海報。

### 非同步產圖

產圖流程應非同步，不要阻塞閱讀下一篇 paper：

1. 每讀完並決定一篇「今日推薦點開」後，先根據該篇內容寫出 image prompt。
2. 立即開 sub-agent 讓 Codex / ChatGPT image 以 `openai/gpt-image-2` 產圖；主 DailyRead 流程繼續讀下一篇。
3. 圖片輸出到 `assets/YYYY-MM-DD/<slug>.png`。
4. sub-agent 完成後，主流程檢查圖片是否存在、基本可讀、無明顯錯字或嚴重跑題。
5. 在對應 domain markdown 與 `daily/YYYY-MM-DD.md` 的推薦篇段落插入 Markdown 圖片連結：
   - GitHub Markdown：`![](../assets/YYYY-MM-DD/<slug>.png)`（視檔案相對路徑調整）
   - Obsidian 可讀時也可使用一般 Markdown 圖片語法。

### Image prompt template

針對每篇推薦內容產生英文 prompt，包含：

- Title / short topic.
- Problem: 原始問題或研究動機。
- Method: 方法、pipeline、framework 或 taxonomy。
- Evidence: dataset / benchmark / main experiment / evaluation setup（若有）。
- Takeaway: 一句核心判斷。
- Diagram type: concept map / pipeline note diagram / classification tree / architecture workflow.
- Style: clean research notebook, readable English labels, paper texture, arrows, highlight markers, minimal icons.

不要把未確認的實驗數字或結論畫進圖片；若資訊不足，只畫 problem–method–takeaway。

## Git

完成後：

1. `git add` 今日新增 / 修改檔案
2. `git commit -m "DailyRead: YYYY-MM-DD"`
3. `git push origin main`

若沒有有效新內容，不要空 commit；在 log 寫明原因。

Commit 前必須由 main model 自審三個 domain notes：

- 每篇條目是否保留 `這篇在說什麼 / 主要貢獻 / 方法 / pipeline / 實驗設計 / かに讀後判斷` 五個小標題。
- 內容是否真的有講清楚研究問題、方法、證據與閱讀判斷，而不是只補標題。
- 若有 paper / article 資訊不足，是否明確說明目前能確認與不能確認的部分。

自審不通過就先補齊，不要直接 commit。

## Discord 回報

不要把完整晨報丟到 paper 晨報頻道。完成後只回覆一段短摘要即可：

- 今日 DailyRead 已更新
- 三個 domain 各一句 headline
- 今日推薦點開 1–3 篇
- Git commit hash

不要貼全文。
