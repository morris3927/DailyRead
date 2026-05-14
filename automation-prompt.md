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

不要做卡片式摘要。每篇 paper 要像「かに讀完後講給 Morris 聽」：

- 用自己的話重講 abstract / 主旨
- 說明主要貢獻
- 說明方法 / pipeline / 架構
- 說明實驗設計：dataset、benchmark、baseline、metric、main result；若資訊不足，明確說目前只從 abstract/landing page 能看到什麼，不要編造
- 最後給閱讀判斷：這篇在領域裡的位置，以及是否值得 Morris 點開

Harness Engineering 可納入 blog、docs、GitHub repo、framework。若不是 paper，不硬套實驗設計，改寫：

- 這篇文章 / repo 在解決什麼工程問題
- 工程設計或架構重點
- 對 agent harness / eval / workflow 的意義
- 是否值得收藏或細看


## 深度最低標準

DailyRead 的品質重點是「講解深度」，不是 paper 數量。即使今天每個 domain 只有 1–2 篇，也不能寫成短摘要或卡片。

每一篇被納入 domain note 的內容，至少要包含：

1. **研究問題 / 動機**：這篇到底在補哪個缺口？為什麼這個問題重要？
2. **方法 / 架構 / pipeline**：作者怎麼做；若是 benchmark，要說 task construction、evaluation protocol、scoring；若是 harness/blog/repo，要說工程架構與 workflow。
3. **實驗設計 / 證據**：dataset、benchmark、baseline、metric、main result；如果只讀到 abstract / landing page，就明確寫「目前能確認到的證據只有哪些」，不要用一句話帶過。
4. **和同領域既有內容的關係**：它延續、反駁、補足或修正了前幾天/既有 paper 的哪個問題？
5. **かに讀後判斷**：具體說明值得/不值得 Morris 點開的理由，以及如果要深讀應優先看哪些 section / figure / table。

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
2. 立即開 sub-agent 讓 Codex / ChatGPT image 產圖；主 DailyRead 流程繼續讀下一篇。
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

## Discord 回報

不要把完整晨報丟到 paper 晨報頻道。完成後只回覆一段短摘要即可：

- 今日 DailyRead 已更新
- 三個 domain 各一句 headline
- 今日推薦點開 1–3 篇
- Git commit hash

不要貼全文。
