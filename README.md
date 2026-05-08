# DailyRead

DailyRead 是一個 Obsidian-readable 的領域動態筆記庫，用來每天追蹤指定 AI / agent 研究方向的 paper、technical report、benchmark、framework 與高品質技術文章。

定位不是完整文獻回顧，而是「paper / research news briefing」：用 5–10 分鐘快速掌握這些領域最近在談什麼、有哪些值得點開的內容。

## Current Domains

- `silicon-sampling-social-simulation/` — Silicon Sampling、LLM persona、social simulation、synthetic population、generative agents
- `harness-engineering/` — LLM / agent evaluation harness、benchmark infrastructure、eval pipeline、reproducibility、technical engineering posts
- `agent-memory/` — LLM agent memory、long-term memory、episodic / semantic memory、memory retrieval、agent cognition

## Daily Structure

- `daily/YYYY-MM-DD.md` — 每日總覽，類似晨報首頁
- `<domain>/YYYY-MM-DD.md` — 各領域當日筆記
- `<domain>/README.md` — 領域介紹、關鍵字、篩選標準
- `logs/` — 執行紀錄
- `raw/` — 搜尋結果與中間資料

## Style

- 像研究新聞播報，但不是卡片式摘要。
- 每篇 paper 以「小龍蝦讀完後講給 Morris 聽」的方式重述：先用白話說明 abstract / 主旨，再整理主要貢獻、方法、實驗設計與閱讀判斷。
- 每則內容都標明來源與類型：paper / survey / benchmark / framework / blog / technical report。
- Paper 需要盡量說明 contribution、method、experiment design；blog / docs 則改說工程設計、實作重點與可學到什麼。
- 不硬湊數量；找不到高品質內容時，明確寫「今日無高品質候選」。
- 保留原始 URL，方便後續自行深讀。
