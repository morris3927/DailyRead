# 🧠 詳細閱讀報告｜Stop Overvaluing Multi-Agent Debate

> [!info] Paper Info
> **完整標題**：Stop Overvaluing Multi-Agent Debate—We Must Rethink Evaluation and Embrace Model Heterogeneity  
> **arXiv ID**：2502.08788  
> **作者**：Hangfan Zhang, Zhiyao Cui, Jianhao Chen, Xinrun Wang, Qiaosheng Zhang, Zhen Wang, Dinghao Wu, Shuyue Hu  
> **來源**：arXiv:2502.08788 [cs.CL, cs.LG]  
> **日期**：Submitted on 12 Feb 2025；last revised 21 Jun 2025, v3  
> **論文類型**：position paper + empirical evaluation  
> **報告語言**：繁體中文

**Tags**：#LLM #MultiAgentSystems #MultiAgentDebate #Evaluation #InferenceTimeCompute #SelfConsistency

> [!summary] 一句話總結
> 這篇 paper 關注的是 LLM multi-agent debate（MAD）到底有沒有真的比簡單的 single-agent inference 更有效。作者指出，目前 MAD 研究常因 benchmark 狹窄、baseline 太弱、設定不一致而被高估；他們系統性評估 5 種 MAD 方法、9 個 benchmark、4 個 foundation models 後發現，現有 MAD 通常無法穩定超越 CoT，且在可比較 inference budget 下常輸給 Self-Consistency。比較正面的訊息是：若把 debate 中的 agents 改成 heterogeneous models，MAD 的平均表現會穩定改善，顯示 MAS/MAD 的價值可能不在「多個同質 agent 互講」，而在能否引入真正互補的知識與推理差異。

---

## 1. 研究定位：這篇 paper 放在哪條研究線？

這篇 paper 位在 **LLM inference-time scaling / multi-agent collaboration / multi-agent debate evaluation** 的交界。它不是提出一個複雜的新 MAD 架構，而是對「MAD 是否真的有效」做系統性再評估，並提出一個立場：目前社群過度高估 MAD，真正需要的是更嚴格的 evaluation，以及更重視 model heterogeneity。

- **研究線**：LLM multi-agent debate、agent collaboration、inference-time computation、LLM evaluation。
- **論文類型**：position paper + empirical study；帶有方法觀點，但主要貢獻是評估與研究議程重塑。
- **它想補上的缺口**：過去 MAD paper 常只跟 direct prompting 比，或只在少數/新提出的資料集上驗證，缺少與 CoT、Self-Consistency 這類 strong single-agent baselines 的穩定比較，也很少同時看 performance、efficiency、robustness。

作者把問題說得很直接：MAD 的概念很吸引人，因為「two heads are better than one」看似合理；但如果那些 heads 只是同一模型的多次角色扮演，且沒有比 CoT-SC 更有效率，那 MAD 的研究敘事就需要被重新檢查。

---

## 2. 研究問題與動機

這篇 paper 的核心動機是：MAD 研究已經有不少正面結果與頂會發表，但這些結果是否真的能支持「multi-agent debate 能提升 LLM reasoning/factual accuracy」這個一般性主張？

作者認為目前 MAD 評估有三個主要問題：

1. **benchmark coverage 很窄且彼此重疊少**  
   不同 MAD 方法常在不同任務上測，包含數學、翻譯、程式、對話評估等，但缺少共同 benchmark，因此很難判斷哪個方法真的比較好。

2. **baseline comparison 偏弱**  
   很多方法只跟 direct answer / direct prompting 比，沒有充分比較 CoT 或 Self-Consistency。這會讓 MAD 看起來有進步，但其實可能只是比一個弱 baseline 好。

3. **成本與效率沒有被公平處理**  
   MAD 通常需要更多 LLM calls 或更多 tokens。如果多花很多 inference-time compute 才換來一點點或不穩定的提升，那應該跟 SC 這種簡單的 inference-time scaling 方法比較，而不是只看 accuracy。

作者提出的主問題可以重建為：

- MAD 是否真的比 simple single-agent baselines 更好？
- MAD 的優勢是否跨模型、跨 benchmark、跨設定穩定？
- MAD 多花的 LLM calls / tokens 是否有效轉換成 performance gain？
- 如果目前同質模型的 MAD 不夠好，真正有希望的 MAS 設計因素是什麼？

---

## 3. 作者的方法到底在做什麼？

整體 pipeline 是：作者選 5 個代表性 MAD frameworks，放到 9 個標準 benchmark、4 個 foundation models 上，跟 3 種 single-agent baselines 比較，並額外分析 hyperparameters、token efficiency、錯誤修正/錯誤引入，以及 heterogeneous-model MAD 的效果。

### 3.1 資料集 / 任務設定

作者使用 9 個 widely adopted benchmarks，涵蓋三類 LLM 能力：

- **General knowledge**
  - MMLU
  - MMLU-Pro
  - CommonsenseQA（paper 文字中有拼成 CommensenseQA）
  - ARC-Challenge
  - AGIEval
- **Mathematical reasoning**
  - GSM8K
  - MATH
- **Programming**
  - HumanEval
  - MBPP

評估 metric：

- MMLU / MMLU-Pro / CommonsenseQA / ARC-Challenge / AGIEval / GSM8K / MATH：accuracy, 0-shot。
- HumanEval / MBPP：Pass@1, 0-shot。

使用的 foundation models：

- gpt-4o-mini-2024-07-18
- claude-3-5-haiku-2024-1022
- Llama3.1:8b-instruct
- Llama3.1:70b-instruct

作者說明除非另有註明，temperature 設為 1、top-p 設為 1，以平衡生成品質與多樣性。

### 3.2 模型 / 系統 / 演算法設計

比較的 single-agent baselines 有三種：

- **SA / single-agent**：只給必要題目描述，直接產生答案。
- **CoT / Chain-of-Thought**：加入 “Let’s think step by step” 來誘導逐步推理。
- **SC / Self-Consistency**：重複從 CoT agent sample，多次產生答案後用 majority voting 決定最終答案。作者依照 Wang et al. (2023) 的假設，只在能以單一正確答案投票的任務使用 SC；因此 programming tasks 不納入 SC。

比較的 MAD frameworks 有五種：

- **SoM / Society-of-Minds**：早期代表性 MAD 方法；多個 agents debate，最後 majority voting。
- **MP / Multi-Persona**：固定角色，例如 affirmative agent / negative agent，再由 judge agent 判斷。
- **EoT / Exchange-of-Thoughts**：指定不同 persona / reasoning tendencies，並加入 confidence evaluation。
- **ChatEval**：使用不同 agent roles，採 round-by-round debate / majority voting 等策略。
- **AgentVerse**：較動態的 multi-agent framework，可由 verifier / judger 決定後續流程；在 programming 任務中有額外 execution-evaluation stage。

作者為了公平比較，盡量把不同 MAD 方法調到相近 inference budget；除非另有說明，預設使用 **6 次 LLM calls**。這點很重要，因為 MAD 的優勢如果只是來自「多叫模型幾次」，就必須和同樣會多叫模型的 SC 比。

### 3.3 評估方式

作者的評估分成幾個層次：

1. **MAD vs SA / CoT / SC**  
   主要看 MAD 是否比 direct single-agent、CoT、Self-Consistency 更好。

2. **跨模型、跨 benchmark 的統計彙整**  
   作者把 4 個 models × 9 個 benchmarks 形成 36 個 experimental configurations，對每個 MAD 與 CoT 的比較做 ANOVA test，significance level = 0.05。若 p-value > 0.05，視為 tie；否則依結果分成 win / tie / lose。

3. **hyperparameter ablation**  
   改變 debate rounds 與 number of agents，檢查 MAD 輸給 CoT 是否只是因為設定不好。

4. **efficiency / token consumption 分析**  
   看 MAD 是否能有效利用更多 tokens；並跟增加 samples 的 SC 比。

5. **question-level error analysis**  
   比較 MAD 相對於 SA 修正了多少原本錯的答案，又錯改了多少原本對的答案。

6. **Heter-MAD 分析**  
   將 agents 從同一模型改為從多個模型中隨機抽取，測試 model heterogeneity 是否改善 MAD。

---

## 4. 主要結果

### 4.1 最重要的發現：MAD 通常沒有贏過 CoT，更常輸給 SC

**Paper evidence：** 作者在 abstract 和 Section 3 都明確指出，5 種代表性 MAD 方法在 9 個 benchmark、4 個 foundation models 的系統性評估中，通常無法超越簡單的 single-agent baselines，例如 CoT 和 SC。

更具體地：

- 在 GPT-4o-mini 的 Table 3 中：
  - **SoM 在 9 個 datasets 全部低於或不高於 CoT**；例如 MMLU 上 CoT 是 80.73±0.34，SoM 是 74.73±0.52。
  - **ChatEval 和 AgentVerse 各只在 9 個 datasets 中 1 個超過 CoT**。
  - **SC 在可用任務中通常最高**；例如 GPT-4o-mini 上，SC 在 MMLU 是 82.13±0.66，高於 CoT 的 80.73±0.34，也高於各 MAD；GSM8K 上 SC 是 95.67±0.19，高於 CoT 的 93.60±0.82。

- 跨 36 個 configurations 的 win/tie/lose 統計中：
  - SoM、EoT、ChatEval、AgentVerse 對 CoT 的 win rate 約只有 15%。
  - MP 沒有展現對 CoT 的顯著改善。
  - paper 在 introduction 中也強調：沒有任何 MAD 方法在 36 個 scenarios 中對 CoT 達到超過 20% 的 win rate。

**解讀：** 這對 Morris 特別關心的問題很關鍵：如果目標是「用 inference-time compute 提升單題答案正確率」，那 **single agent + CoT-SC 很可能比目前常見的同質 MAD/MAS 更穩、更便宜、更容易評估**。MAD 並不是自然就比 single-agent 好；它至少要通過 CoT 和 SC 這兩個門檻。

### 4.2 MAD 可以贏 SA，但這不代表它贏過 strong single-agent baselines

**Paper evidence：** 作者也承認，大多數 MAD frameworks 通常能贏過直接作答的 SA。在 GPT-4o-mini 條件下，MAD frameworks 在 45 個 conditions 中有 34 個 outperform SA，這與過去 MAD 研究的正面發現一致。

**解讀：** 這裡的重點不是「MAD 完全沒用」，而是「MAD 的常見 claim 可能建立在太弱的 baseline 上」。如果只跟 direct prompting 比，很多方法都會看起來有效；但一旦換成 CoT 或 SC，MAD 的相對價值就急速下降。

### 4.3 調 debate rounds 或 agent 數量通常救不了 MAD

**Paper evidence：** 作者用 GSM8K、MMLU、HumanEval 代表三類能力，調整 debate rounds 和 number of agents。結果顯示，多數情境中增加 agents 或 rounds 不會顯著改變結論，甚至可能停滯或下降。

例外是：

- SoM 在 GSM8K 上隨 debate rounds 變動時持續超過 CoT。
- EoT 在 GSM8K 上，agents 從 3 增加到 9 時 performance 持續提升，最後超過 CoT。

但作者認為這些例外不足以推翻整體結論：MAD 無法靠簡單調 hyperparameters 就穩定超越 CoT。

**解讀：** 這警告 MAS 研究不能只說「我們再加更多 agents / rounds 就會更好」。如果沒有更好的 interaction / aggregation mechanism，規模增加不一定等於推理品質增加。

### 4.4 從 token efficiency 看，SC 比 MAD 更有效利用 inference budget

**Paper evidence：** 作者比較 token consumption 的 scaling。結果是：

- SC 能有效利用增加的 inference budget。
- MAD frameworks 要嘛沒有穩定正向趨勢，例如 SoM 在 MMLU 上不會因消耗更多 tokens 而穩定變好；要嘛即使有正向趨勢，仍在 comparable token budget 下輸給 SC，例如 EoT 在 MMLU 和 GSM8K 上隨 tokens 增加而改善，但仍明顯低於 SC 或其他 MAD。

**解讀：** 這是整篇 paper 對 MAD/MAS 評估最有殺傷力的一點。MAD 不只要看 accuracy，還要看「每一單位 token / call 換來多少提升」。如果同樣多花 tokens，SC 更穩，那 MAD 就不能只用「多 agent collaboration」的概念吸引力來合理化成本。

### 4.5 MAD underperform 的原因：會修錯，也會把對的改錯

**Paper evidence：** 作者做 question-level analysis，看每個 MAD 方法相對 SA 修正了多少錯誤，以及引入了多少新錯誤。結果指出：

- MP、ChatEval、AgentVerse 能修正很多錯誤，但也常把原本正確的答案改錯，因此不穩定。
- SoM、EoT 較保守，比較少引入錯誤，但也較少成功修正錯誤。

**解讀：** 這揭示 MAD 設計中的核心 trade-off：

- 太 aggressive 的 debate / judge 容易 over-correction。
- 太 conservative 的 debate 又無法充分利用「多 agent」的潛力。

這也表示 MAD 的問題不只是 prompt 工程，而是 aggregation / verification / disagreement resolution 的方法論問題。

### 4.6 Heter-MAD：model heterogeneity 是比較有希望的方向

作者提出一個很簡單的變體：**Heter-MAD**。每次 agent 要生成輸出時，不固定使用同一 foundation model，而是從候選模型池中依機率抽樣。實驗中使用 GPT-4o-mini 和 Llama3.1-70b，兩者被選到的機率都設為 0.5。

**Paper evidence：** 作者把 Heter-MAD 套到 SoM、EoT、ChatEval、AgentVerse；MP 被排除，理由是前人指出角色不平衡，且相對 CoT win rate 為 0%。結果顯示：

- Heter-SoM 相對 SoM-average 平均提升 **+6.4%**。
- Heter-EoT 相對 EoT-average 平均提升 **+8.2%**。
- Heter-ChatEval 相對 CE-average 平均提升 **+4.0%**。
- Heter-AgentVerse 相對 AGV-average 平均提升 **+2.7%**。
- 所有 considered MAD methods 加入 heterogeneity 後，都 outperform CoT-Average，最高到 **+5.8%**。
- Heter-SoM 反而達到最高平均表現，超過較新的複雜 MAD 方法。

作者進一步分析 Heter-MAD 為什麼有效：他們把題目分成 CC、CW、WC、WW：

- CC：GPT-4o-mini 和 Llama3.1-70b 都答對。
- WW：兩者都答錯。
- CW：只有 GPT-4o-mini 答對。
- WC：只有 Llama3.1-70b 答對。

Heter-MAD 的主要提升來自 CW/WC，也就是某一個模型會、另一個模型不會的題目。這支持作者的說法：heterogeneous models 能提供真正的知識/推理互補。

**解讀：** 這裡對 MAS 的啟示很明確：如果 agents 本質上是同一模型的多個 prompt 角色，那它們的錯誤可能高度相關；這不是真正的 collective intelligence。MAS 的價值更可能來自 **能力互補、錯誤不相關、知識多樣性、推理路徑異質性**，而不是 agent 數量本身。

---

## 5. 這篇 paper 的貢獻

- **系統性挑戰 MAD 的主流樂觀敘事**：作者不是只做單一 negative example，而是用 5 個 MAD frameworks、9 個 benchmarks、4 個 foundation models 來說明現有 MAD 常被高估。

- **把 strong single-agent baselines 放回評估中心**：paper 清楚指出，MAD 不能只跟 SA / direct prompting 比，必須跟 CoT 和 Self-Consistency 比，尤其要考慮相近 LLM calls / token budget。

- **提出 performance + efficiency + robustness 的 MAD 評估框架**：作者不只報 accuracy，也看 token consumption、hyperparameter robustness、question-level error behavior。

- **指出 model heterogeneity 可能是 MAD 真正有效的核心機制之一**：Heter-MAD 的簡單改動能穩定改善所有 considered MAD frameworks，顯示 debate 的價值可能來自 epistemic diversity，而不是多個同質 agent 的形式。

- **提出未來 MAD 研究問題**：包含如何利用 heterogeneity、如何結合更強 single-agent inference、如何做 fine-grained interaction、以及什麼場景才能真正反映 MAD utility。

---

## 6. 限制與需要小心的地方

> [!warning] 不要過度推論
> 以下分成 paper evidence 與かに解讀。若 paper 沒明確支持，我不把它當作作者結論。

### 6.1 Paper evidence：作者自己承認或內容可見的限制

- **Heter-MAD 不是最佳化過的技術方案**  
  作者明確說他們無意提出一個專為 heterogeneity 最佳化的 MAD design；Heter-MAD 只是簡單地從候選模型池抽樣 foundation model。因此它證明「heterogeneity 有潛力」，不代表已經解決 heterogeneous collaboration。

- **目前 benchmark 可能不適合展現 MAD 真正價值**  
  作者指出，許多現有 benchmark 主要是單一知識點或單題答案，可能本來就適合強 single-agent 解決，不一定能反映多 agent 協作的價值。

- **SC 不適用於所有任務**  
  作者依照原始 SC 設定，只在能 majority voting 單一正確答案的任務使用 SC，因此 programming tasks 被排除。這代表「SC 輾壓 MAD」這個說法要限縮在 SC 可合理使用的任務類型。

- **AgentVerse 在 programming task 的優勢含額外 execution-evaluation stage**  
  作者提醒，AgentVerse 在 HumanEval 上能顯著勝過 CoT，但它使用了生成程式的執行結果，這通常不是其他 MAD frameworks 的設計範圍，因此比較時要小心。

- **模型範圍仍有限**  
  主評估使用 4 個 foundation models，Heter-MAD 實驗使用 GPT-4o-mini 與 Llama3.1-70b。這已比許多 MAD paper 更廣，但仍不能代表所有 frontier/reasoning models 或 domain-specific models。

### 6.2 かに解讀：讀這篇時要額外小心的地方

- **這篇不是在宣告 MAS 無效，而是在宣告「現有 MAD 評估不足」**  
  它批判的是目前常見 MAD 設計與評估習慣，而不是所有 multi-agent collaboration。

- **Heterogeneity 的因果機制仍需要更細的研究**  
  paper 的 CW/WC 分析很有說服力，但目前仍偏 outcome-level。未來若要做方法創新，需要知道不同模型何時互補、何時互相干擾、judge 如何辨識哪個模型可信。

- **benchmark 任務型態會強烈影響結論**  
  如果任務是單題 closed-form QA，CoT-SC 很可能已經很強；但若任務是長流程 research、multi-document synthesis、software engineering、human organization simulation，MAD/MAS 的價值可能會不同。這篇 paper 自己也把這列為 future question。

---

## 7. 跟 Morris 研究/學習的關聯

Morris 特別關心的問題是：**single agent + CoT-SC 是否會比 MAS / multi-agent debate 更好，以及這對 MAS 評估有什麼警訊。**

這篇 paper 給的答案很清楚：

1. **在這篇 paper 的設定下，single-agent CoT/SC 通常比現有 MAD 更值得先試**  
   CoT 是非常強的最低門檻；SC 則是 inference-time compute 的強 baseline。任何 MAS/MAD 方法如果不能在相近 token/call budget 下贏過 CoT-SC，就不能說自己因「協作」而有效。

2. **MAS evaluation 不能只放 direct prompting baseline**  
   如果一篇 MAS paper 只跟 SA 或 naive prompting 比，Morris 應該立刻提高警覺。至少要問：有沒有 CoT？有沒有 SC？有沒有控制 LLM calls/tokens？有沒有跨 benchmark？有沒有跨 model？

3. **要區分「多 agent 外觀」與「真正互補的 agent 能力」**  
   多個角色 prompt 不一定帶來真正 diversity。同一模型生成的多個 agents 可能共享盲點，甚至在 debate 中把對的答案帶偏。這對 MAS 研究非常重要：agent role diversity 不等於 model/knowledge/reasoning diversity。

4. **未來 MAS 的合理評估應該包含成本與錯誤行為**  
   不只看 accuracy，還要看：
   - 每次提升花了多少 tokens？
   - agent debate 是否會 over-correct？
   - 哪些題目從錯變對？哪些從對變錯？
   - MAS 是否只是在重複同一模型的錯誤？

5. **對 MIS / 管理與協作研究的啟示**  
   這篇 paper 其實呼應組織與團隊研究的一個老問題：團隊績效不是人數函數，而是成員異質性、協調成本、決策規則、資訊整合能力的函數。對 AI agents 也是如此。若要研究 MAS，應該把「協作機制如何轉換異質知識」當成核心，而不是只把多 agent 當成 prompt pattern。

---

## 8. 對 multi-agent debate / collaboration 的啟示

### 8.1 Paper evidence

作者的明確主張是：

- 現有 MAD 方法在 systematic evaluation 下常無法 reliable outperform CoT 和 SC。
- 當比較相近 inference budget 時，MAD 的 token efficiency 通常不如 SC。
- 同質模型的 MAD 可能被過度高估。
- 引入 model heterogeneity 可以穩定改善 MAD。
- 未來 MAD 應該重新思考 evaluation paradigm，並把 heterogeneity 作為核心設計原則之一。

### 8.2 かに解讀

我覺得這篇對 MAS 評估最大的警訊是：**「多 agent」本身不是貢獻；能否在公平成本下產生超越 strong single-agent inference 的穩定增益，才是貢獻。**

如果要評估一個 MAS / MAD 系統，我會建議 Morris 用以下 checklist：

- 是否跟 CoT 和 SC 比，而不是只跟 direct prompting 比？
- 是否控制 LLM calls、tokens、latency、成本？
- 是否跨任務、跨模型、跨設定測試？
- 是否分析 win/tie/lose，而不是只報平均分？
- 是否分析錯誤修正與錯誤引入？
- agents 是否真的異質，還是只是同一模型不同 persona？
- judge / aggregator 是否有能力辨識哪個 agent 的 reasoning 更可信？
- 任務是否真的需要 multi-agent collaboration，還是 single-agent CoT-SC 已足夠？

這篇 paper 也讓我更傾向一個判斷：**MAS 的研究價值不該建立在「模擬人類開會」這個比喻上，而該建立在可驗證的互補性與資訊整合機制上。**

---

## 9. かに讀後判斷

這篇值得 Morris 深讀，尤其如果你正在看 MAS、multi-agent collaboration、debate、agent evaluation。它不是最炫的方法 paper，但很適合當作 MAS 評估的「校準器」。

我的讀後判斷：

- **如果你要做 MAS/MAD 方法**：這篇要求你一定要放 CoT、SC、token budget、cross-benchmark robustness。否則很容易被質疑只是贏過弱 baseline。
- **如果你要讀別人的 MAS paper**：這篇提供一個很好的審稿視角。看到只跟 direct prompting 比、只測一兩個資料集、沒有成本分析的 MAD paper，要非常小心。
- **如果你關心 single-agent + CoT-SC vs MAS**：在標準 QA/math/programming benchmark 上，這篇證據支持「先用 CoT-SC 作為強基準」。MAS 必須證明它在同等成本下有額外價值。
- **如果你想找 MAS 的未來方向**：model heterogeneity、fine-grained reasoning interaction、能展現多知識整合的任務場景，是比單純增加 agents/rounds 更有前途的方向。

最精簡的 take-away 是：

> **MAD 不是不能做，而是不能再用弱 baseline 與 selective benchmark 來證明。真正值得研究的不是「多幾個 agent」，而是「不同能力如何被有效整合」。**

---

## 10. 本次保存檔案

依照目前 DeepRead 保存規則，repo 只保留必要交付物：

- PDF：`/Users/morris/Desktop/Repo/DailyRead/deepread/2502.08788/paper.pdf`
- 本報告：`/Users/morris/Desktop/Repo/DailyRead/deepread/2502.08788/report.md`
