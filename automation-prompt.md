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

## 產出位置

在 repo `/Users/morris/Desktop/Repo/DailyRead` 中更新：

- `daily/YYYY-MM-DD.md`：今日總覽與推薦點開
- `silicon-sampling-social-simulation/YYYY-MM-DD.md`
- `harness-engineering/YYYY-MM-DD.md`
- `agent-memory/YYYY-MM-DD.md`
- `logs/YYYY-MM-DD.log`
- `raw/search-YYYY-MM-DD.json`

## 數量原則

每天不硬湊數量。預設：

- 每個 domain 1–3 則高品質內容
- 若某 domain 沒有高品質候選，明確寫今日無高品質候選
- 優先挑能說清楚方法與實驗設計的 paper

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
