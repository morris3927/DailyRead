# 🧠 詳細閱讀報告｜AHE: Observability-Driven Harness Evolution

> [!info] Paper Info
> **完整標題**：Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses
> **作者**：Jiahang Lin, Shichun Liu, Chengjun Pan, Lizhi Lin, Shihan Dou, Xuanjing Huang, Hang Yan, Zhenhua Han, Tao Gui
> **來源**：arXiv:2604.25850v3 (cs.CL, cs.SE)
> **日期**：2026-04-30 (v3)
> **論文類型**：方法創新 + 系統建置
> **報告語言**：繁體中文

**Tags**：#coding-agent #harness-engineering #self-evolution #observability #agent-optimization

![](../assets/2026-05-12/ahe-harness-evolution.png)

> [!summary] 一句話總結
> 這篇 paper 關注的是 coding agent 的 harness 工程自動化問題。作者想解決的是：目前 coding agent 的 harness（系統提示、工具、中介層、記憶等）調校全靠人工，且自動化面臨異質動作空間、海量軌跡難以提煉信號、編輯效果難以歸因三大瓶頸。它的核心貢獻不是單純調 prompt 或強化學習，而是提出 AHE 三層可觀測性架構（component observability、experience observability、decision observability），讓每一次 harness 編輯都成為可證偽的合約。最重要的結果是：在 Terminal-Bench 2 上 10 輪迭代將 pass@1 從 69.7% 提升至 77.0%，超越人工設計的 Codex-CLI（71.9%）及其他自演化基線。

## 1. 研究定位：這篇 paper 放在哪條研究線？

這篇 paper 位於 **coding agent harness 工程 + agent 自動優化** 的交匯處。它回應的是一個越來越迫切的實務問題：coding agent 的表現不僅取決於底層 LLM，也取決於圍繞模型的 harness（system prompt、tools、middleware、memory 等），但 harness 的調校目前完全依賴人工，隨著模型快速迭代已跟不上腳步。

- **研究線**：coding agent harness engineering + automated agent optimization
- **論文類型**：方法創新 + 系統建置 — 提出 AHE 閉環方法，並在 NexAU 框架上完整實現
- **它想取代或補上的缺口**：既有自動化方法（ACE、TF-GRPO 等）只優化單一組件（通常是 prompt 或 playbook），無法聯合演化 harness 的所有可編輯組件。兩個結構性障礙是：①原始軌跡 token 量大且結構鬆散，提煉不出可操作信號；②組件耦合緊密，改 prompt 以外的東西容易出錯。AHE 識別出真正的瓶頸在於「可觀測性（observability）」而非 agent 能力。

## 2. 研究問題與動機

作者的核心問題：**如何讓一個 evolution agent 穩定地聯合演化 coding agent harness 的所有可編輯組件？**

這個問題為什麼重要：
- Harness 設計實質上影響 coding agent 在長時序任務上的表現，即使 base model 固定也不變。
- 最佳 harness 是 model-specific 的——為一個 base model 調校的 harness 換到另一個模型往往表現下降，必須重新適配。
- 目前完全靠人工：開發者看軌跡、找失敗模式、手動改 prompt / tools / middleware / skills。
- Base model 進展飛快，人工迴圈跟不上，模型能力和所需 harness 之間的差距越來越大。

既有自動化方法的局限：
- ACE 蒸餾自然語言 playbook，讓 agent 在 context 中讀取——但只改 prompt 層。
- TF-GRPO 用 trajectory-feedback 強化成功的工具序列——但只改行為策略，不碰 harness 結構。
- 其他方法或改 skills、或搜尋 graph-structured workflows——都只觸及單一面向。

## 3. 作者的方法到底在做什麼？

AHE 的核心設計原則：**閉環中每一階段的產物都必須是可觀測的**——以結構化、分層的形式呈現，讓另一個 agent 可以讀取並據此行動。Base model 固定不動，只改 harness。

整體 pipeline 分為六個 phase，每輪迭代依序執行：
1. **Rollout**：用目前 harness 跑 k 個 rollouts
2. **Clean**：清理軌跡（去 base64、去重 tool output）
3. **Attribute & Rollback**：歸因上一輪 manifest，回退未通過的編輯
4. **Agent Debugger**：分層蒸餾軌跡為結構化 evidence corpus
5. **Evolve**：Evolve Agent 讀取 evidence，決定編輯，寫入 manifest
6. **Commit**：git commit 打標籤

### 3.1 資料集 / 任務設定

- **演化環境**：Terminal-Bench 2，89 個任務（4 easy / 55 medium / 30 hard），每個任務 timeout 1 小時。
- **跨 benchmark 轉移測試**：SWE-bench-verified，500 個任務，涵蓋 7 個 repository。
- **Base model**：GPT-5.4 high（演化時使用），跨模型測試另用 deepseek-v4-flash、qwen-3.6-plus、gemini-3.1-flash-lite-preview、GPT-5.4 medium / xhigh。
- **每個任務跑 k=2 rollouts**，以穩定 pass@1 信號。
- **評估指標**：pass@1（二元成功率均值）和 tokens/trial（每次試驗的 prompt+completion token 數，以千為單位）。超時或基礎設施中止的 trial 計為失敗。

### 3.2 模型 / 系統 / 演算法設計

AHE 的方法建立在三個可觀測性支柱上：

**❶ Component Observability — NexAU 解耦式 harness 基板**

NexAU 框架將 harness 拆成七種正交組件，每種以獨立檔案掛載在工作空間的固定路徑：
- system prompt、tool description、tool implementation、middleware、skill、sub-agent configuration、long-term memory

組件之間鬆耦合——加 middleware 不需要改 system prompt，加 skill 不需要碰 tool。這意味每個失敗模式可以對應到單一組件類別，每次 pass-rate 變化可以歸因到一個檔案。每次邏輯編輯就是一次 git commit，自然擁有 diff 和 rollback 能力。

種子 harness H₀ 刻意極簡：只有一個 shell 執行工具，沒有 middleware、skills、sub-agents。這確保後續每個新增組件都必須在實測 rollouts 中證明自己的價值，避免歸因污染。

**❷ Experience Observability — Agent Debugger 分層軌跡蒸餾**

原始軌跡動輒數百萬 token，直接丟給 agent 無法消化。Agent Debugger 將軌跡框架化為一個可導航的檔案環境——每條軌跡訊息在獨立檔案中，可用 shell 和腳本工具存取。同一 query 的 traces 放在同一環境中，debugger agent 分析失敗根因或成功模式，產出 per-task 分析報告。最後彙整成 benchmark-level overview 作為每輪迭代的入口。

此外也提供原始 traces（raw 和輕量處理版本），讓 agent 可以驗證報告中的宣稱。所有內容以檔案形式提供，支援 progressive disclosure——節省 token，讓 agent 決策更精準。

**❸ Decision Observability — Change Manifest 可證偽編輯合約**

Evolve Agent 在每輪中讀取分層 evidence corpus，決定要新增、修改或移除哪些 harness 組件，並記錄每次編輯的理由。兩個約束實現 decision observability：

1. **可控性**：Evolve Agent 只能寫 harness workspace 內；runs 目錄、tracer、verifier、LLM 配置為 read-only；種子 system prompt 標記為不可刪除。這防止了自我修改的捷徑（如關掉 verifier、換模型、提高 reasoning budget）。

2. **可證偽性**：每次編輯附帶一個 manifest entry，記錄失敗證據、推斷根因、修復方案，以及預測影響（包括預期修復的任務和可能 regression 的任務）。下一輪用實際 task-level delta 驗證預測，產出 per-edit verdict。通過的留下，未通過的在檔案粒度回退。每次編輯因此成為一個可證偽的合約。

### 3.3 評估方式

- **主實驗**：Terminal-Bench 2 上跑 10 輪 AHE 迭代，對比三個人工 harness（opencode、terminus-2、Codex-CLI）和兩個自演化基線（ACE、TF-GRPO，從同一 NexAU₀ 種子出發）。
- **跨 benchmark 轉移**：凍結的 AHE harness 不再演化，直接拿到 SWE-bench-verified 上評估。
- **跨模型轉移**：凍結的 AHE workspace 在 5 個 alternate base models 上重新評估。
- **消融實驗**：逐一套入 AHE 單一組件到 NexAU₀ 種子，定位增益來源。
- **自歸因分析**：對 evolve model 的 self-prediction 計算 precision/recall，分別看 fix 預測和 regression 預測的可靠性。

## 4. 主要結果

### 4.1 最重要的發現

**RQ1：AHE 在 Terminal-Bench 2 上超越所有基線**

- AHE 10 輪迭代：pass@1 從 69.7% → 77.0%
- 超越人工 harness Codex-CLI（71.9%）、terminus-2（62.9%）、opencode（47.2%）
- 超越自演化基線 TF-GRPO（72.3%）和 ACE（68.9%）
- 唯一例外：Hard 難度上略低於 Codex-CLI（53.3% vs 56.7%），作者將此歸因於 AHE 組件在長時序任務上的交互干擾，而非缺少能力——單獨將 AHE 的 long-term memory 換入 NexAU₀ 已超越 Codex-CLI 的 Hard 表現。

**RQ2：凍結 harness 可跨任務與跨模型轉移**

SWE-bench-verified 上：
- AHE 達到最高 aggregate success rate（75.6%），比 NexAU₀（75.2%）、ACE（74.6%）、TF-GRPO（74.2%）都高
- 同時削減 token 消耗：比 NexAU₀ 少 12%、比 TF-GRPO 少 21%、比 ACE 少 32%
- 增益集中在最大且最耗 token 的 repo（django、sphinx-doc），因為其多步 edit-and-verify 迴圈匹配 AHE tools/middleware/memory 壓縮的結構
- 三個最小 repo 有微幅 regression，符合小樣本下 pass@1 變異超過增益的預期

跨模型轉移（Terminal-Bench 2）：
- deepseek-v4-flash：+10.1 pp（51.7% → 61.8%）
- qwen-3.6-plus：+6.3 pp（56.2% → 62.5%）
- gemini-3.1-flash-lite-preview：+5.1 pp（36.5% → 41.6%）
- 跨模型家族增益大於同家族內增益，越未飽和的模型越依賴 AHE 固化在 tools/middleware/memory 中的協調模式

### 4.2 消融實驗或細部分析

**RQ3a：增益來自哪個組件？**

單一套入 AHE 組件到 NexAU₀ 的效果：
- +long-term memory only：75.3%（+5.6 pp）— 12 條 boundary-case 教訓，Hard 上超越 full AHE
- +tool only：73.0%（+3.3 pp）— 1364 行 shell，自動從附近檔案提取 contract hints
- +middleware only：71.9%（+2.2 pp）— finish-hook 強制 closure check
- +system_prompt only：67.4%（-2.3 pp）— 單獨放入反而衰退

結論：**增益來自 tools、middleware、long-term memory，而非 system prompt**。事實性的 harness 結構可跨任務和模型轉移，散文式的策略性 prompt 則不行。

**RQ3b：自歸因的可靠性**

- Fix 預測：precision 33.7%，recall 51.4%，約為隨機基線的 5 倍——evolve model 的修復目標確實有據可循
- Regression 預測：precision 11.8%，recall 11.1%，僅約隨機基線的 2 倍——**agent 能說明為什麼編輯有幫助，但無法可靠預測同一編輯會破壞哪些任務**

這就是演化曲線非單調上升的原因，也是作者指出的最清晰未來方向：**regression foresight**。

## 5. 這篇 paper 的貢獻

- **提出 AHE 方法**：首度將 agent-driven harness 演化形式化，識別出 observability 為設計樞紐，並以三層可觀測性支柱（解耦組件基板、分層軌跡蒸餾、可證偽 change manifest）實現穩定的閉環演化。
- **實證驗證**：Terminal-Bench 2 上 pass@1 從 69.7% → 77.0%，超越所有人工和自演化基線；凍結 harness 可跨 benchmark 和跨模型家族轉移。
- **分析性貢獻**：揭示 agent-driven evolution 的兩個限制——①harness 組件非加性交互，堆疊有效編輯會封頂增益；②自歸因對 fix 可靠但對 regression 幾乎盲，指向 regression foresight 作為未來方向。

## 6. 限制與需要小心的地方

> [!warning] 不要過度推論
> 這一節只根據 paper 內容與可見證據評論。若 paper 沒提供足夠資訊，直接寫「目前從 paper 可見內容無法確認」。

- **Benchmark 範圍有限**：演化只在 Terminal-Bench 2 上驅動，轉移測試只測了 SWE-bench-verified 一個跨 benchmark。更廣泛的程式語言、repo 規模部署、人類在迴路工作流均未測試。
- **Evolution operating point 耦合**：AHE 的 step budget 和 per-task timeout 是為 GPT-5.4 high 設定的，跨模型轉移數字混雜了 harness 可攜性與 operating point 耦合——同一家族內增益隨 reasoning tier 非單調。目前從 paper 可見內容無法確認解耦後的結果。
- **Regression blindness**：自歸因機制對 fix 預測尚可（~5x random），對 regression 幾乎盲（~2x random），這意味演化曲線必然非單調，且目前沒有解決方案。
- **自修改治理不完整**：AHE 限制了編輯範圍並用 versioned manifest 歸因，但未提供完整的 guardrail stack。長時序 harness 清理和更強的誤用防護仍未解決，作者自己定位為「受控研究原型」而非成熟系統。
- **種子 harness 的選擇影響深遠**：極簡種子（只有一個 shell tool）雖然保證歸因乾淨，但意味 AHE 必須從零發明所有組件。一個更好的種子是否會讓 AHE 更快收斂？目前從 paper 可見內容無法確認。
- **非加性交互**：組件間存在非加性交互，堆疊個別有效的編輯未必得到同等總增益。full AHE（77.0%）低於 memory-only（Hard 上 63.3%）和 tool-only（Medium 上 87.3%）的某些單項表現，說明組合後存在干擾。

## 7. 跟 Morris 研究/學習的關聯

這篇 paper 和 Morris 的研究/學習有多處直接相關：

- **Harness Engineering 作為研究主題**：AHE 直接回應了 Morris 使用 OpenClaw 等工具時面臨的實務問題——agent 的 harness（system prompt、tools、middleware、memory）如何調校？AHE 提供了一個系統化的自動化框架，這在 MIS 領域中屬於 AI agent 系統設計與優化的前沿。
- **Observability-driven design 的思維**：三層可觀測性的設計原則（component / experience / decision observability）不僅適用於 harness，也可推廣到任何 agent 系統的可控演化。這種「讓每個決策可證偽」的工程思維值得在 MIS 系統設計中借鑒。
- **Self-evolution 與 agent safety**：AHE 的自修改治理（controllability constraints、rollback 機制）觸及了 Morris 可能關心的 AI safety 議題——如何讓 agent 在自動改進時不失控。
- **跨模型轉移**：AHE 凍結 harness 可跨模型家族轉移的發現，對 Morris 在多模型環境下（如 OpenClaw 支援多種 model）的實踐有參考價值——harness 中哪些是通用工程經驗，哪些是 model-specific 的？
- **Limitations 值得追蹤**：regression blindness 和非加性交互是兩個開放問題，若 Morris 未來做相關研究，這些都是很好的切入點。

## 8. かに讀後判斷

**值得深讀。** 這篇 paper 做了一件很實在的事：把「如何自動演化 coding agent harness」這個模糊的想法，拆解成三個可操作的可觀測性支柱，並用實驗證明它有效。特別值得讀的 sections：

- **§3 Method**：三層可觀測性的設計邏輯很清楚，尤其是 decision observability 的 change manifest 機制，是這篇最有原創性的設計。
- **§4.4 RQ3 Analysis**：消融實驗和自歸因分析是這篇最精彩的部分——它不只告訴你方法有效，還告訴你哪裡有效、哪裡失效、為什麼。system prompt 單獨回歸的發現尤其重要。
- **Limitations**：作者誠實面對 regression blindness 和非加性交互的限制，沒有過度宣稱。

可以帶走的研究設計觀念：
1. **可證偽合約模式**：每次 edit 附帶 self-declared prediction + 下一輪驗證 + rollback，這個 pattern 可以遷移到任何 iterative optimization 場景。
2. **極簡種子 + 強制歸因**：用最簡單的種子確保每個後續改動都有 clean attribution，這個實驗設計原則很實用。
3. **分層 evidence corpus**：從 raw traces → per-task report → benchmark overview 的 drill-down 結構，解決了「海量軌跡無法消化」的通用問題。

Caveat：這篇的 base model 是 GPT-5.4 系列——一個非常強的模型。AHE 的效果在更弱的模型上是否同樣成立，目前從 paper 可見內容無法完全確認（跨模型轉移測試顯示正面但增益大小與模型飽和度相關）。另外，演化只在 89 個任務上跑 10 輪，規模不算大。