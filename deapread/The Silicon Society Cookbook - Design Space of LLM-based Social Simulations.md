# 🧠 詳細閱讀報告｜The Silicon Society Cookbook

> [!info] Paper Info
> **完整標題**：The Silicon Society Cookbook: Design Space of LLM-based Social Simulations  
> **作者**：Aurélien Bück-Kaeffer, Sneheel Sarangi, Maximilian Puelma Touzel, Reihaneh Rabbany, Zachary Yang, Jean-François Godbout  
> **來源**：arXiv:2605.00197v1  
> **日期**：2026-04-30  
> **論文類型**：empirical study / benchmark-like design-space analysis  
> **報告語言**：繁體中文

**Tags**：#SiliconSociety #LLMSocialSimulation #AgentBasedModeling #SimulationValidation #DesignSpace #BluePrint

> [!summary] 一句話總結
> 這篇 paper 關注的是 LLM-based social simulation，也就是作者稱為 **Silicon Societies** 的研究方向：用大型語言模型模擬人類社會互動、社群網路與意見動態。作者想解決的不是「再做一個更大型或更像真的社會模擬器」，而是系統性地問：當我們設計一個 LLM 社會模擬時，base model、agent 數量、網路結構、homophily、survey context、news agent、persona/LoRA 比例這些設計選擇，到底會如何改變模擬結果？
>
> 這篇的核心貢獻是把 Silicon Society 當成一個 design space 來掃描：作者跑了 **595 個 simulation roll-outs**，分析 7 類設計參數對 stylistic realism 與 opinion dynamics 的影響。最重要的發現是：**base model 是最關鍵的變因**，在 BERT AI-detectability 上 η² = 0.266，在 net consensus change 上 η² = 0.090；而社群媒體資料 fine-tuning 會讓文字更難被 BERT 偵測為 AI，也會加強意見動態。相反地，單一 biased news agent 在作者設定下沒有可測量效果。

## 1. 研究定位：這篇 paper 放在哪條研究線？

這篇 paper 放在 **LLM social simulation / generative agent-based modeling / Silicon Society validation** 這條研究線上。它回應的是最近大量 LLM 社會模擬研究共同面臨的問題：大家不斷做出更複雜、更大規模的模擬器，但對「這些模擬到底有多像人類社會」、「哪些設計選擇會改變結果」、「不同 simulator 的結果能不能互相比較」還缺乏穩定標準。

- **研究線**：LLM-based social simulation、Agent-Based Modeling、Silicon Societies、simulation validation
- **論文類型**：empirical design-space analysis；它比較像方法論與實驗設計研究，不是提出單一新的 SOTA simulator
- **它想補上的缺口**：不是直接追求「最 realistic」的 simulator，而是先量化設計參數如何影響模擬軌跡，讓後續研究能做更有根據的 simulator design decision

這篇 paper 的定位很像是給 LLM 社會模擬研究者的一本 cookbook：如果你要煮出一個 Silicon Society，哪些材料最影響味道？哪些材料單獨看起來有效，但混在一起會出現交互作用？哪些設計選擇其實沒有預期中的效果？

作者明確指出，他們只討論 **Silicon Societies**：也就是以 human-likeness / human interaction simulation 為目標的 LLM 社會互動模擬。這跟 coding agents、task-solving multi-agent systems 不同，後者的目標是完成任務，不是模擬人類社會。

## 2. 研究問題與動機

LLM-based social simulation 的吸引力在於，它看起來可以同時捕捉 micro-level 與 macro-level 現象：個體如何發文、回覆、改變看法，以及整體社群是否產生 echo chamber、herding effect、information cascade 等。但問題是，這個領域的 simulator 變得越來越複雜，validation 卻沒有跟上。

作者引用 Larooij & Törnberg (2025)、Li et al. (2025)、Li & Tao (2026)、Seshadri et al. (2026) 等工作指出，目前 LLM 社會模擬的驗證標準仍然不足。很多研究依賴 subjective believability 或 application-specific human baselines，而缺乏能讓研究互相累積的標準化方法。

因此，這篇 paper 沒有試圖回答「哪個 simulator 最像人類社會」。作者改問一個比較可操作的問題：

> 當我們設計 Silicon Society 時，不同設計參數會如何影響模擬結果？這些參數的效果是可加的，還是會產生複雜交互作用？

作者提出兩個主要假設：

1. Silicon Society 的 design space 不會是單純 additive。也就是說，不能只看參數 A 和參數 B 各自對某個 metric 的邊際效果，就預測 A+B 會如何表現。
2. 用 social media data fine-tune LLM 會讓模型在風格上更接近人類，也會改變 simulation 中的行為。

這個問題重要的地方在於：如果 design parameters 的效果高度交互，那麼研究者就不能把 simulator settings 當成獨立可替換的零件。不同 base model、network topology、agent population size、persona construction 之間可能會互相改變結果。

## 3. 作者的方法到底在做什麼？

作者自己建了一個 social network simulator，而不是直接使用現有 simulator。原因是他們想完整控制所有假設與設計參數，避免被既有系統的架構限制。

整體流程可以理解成：

1. 建立一群 LLM agents。
2. 用特定 network topology 把 agents 接成 follower graph。
3. 讓 agents 在模擬中觀察 thread、回覆 thread 或開新 thread。
4. 每隔固定步數對 agents 做 survey，追蹤 opinion dynamics。
5. 對 595 次 roll-outs 的結果做統計分析，檢查各設計參數與交互作用。

作者的 simulator 每次 simulation 共跑 2500 steps，每 250 steps survey 一次，所以每個 simulation 有 11 次 survey。每一步會選 10 個 agents：前 9 個觀察近期 thread，最後 1 個有 1/3 機率開新 thread、2/3 機率回覆既有 thread。作者估計 2500 messages / 1024 agents 大約相當於 75 小時的 simulated time。每個 simulation 在 A100 GPU 上跑 2 到 11 小時，依設定而異。

### 3.1 資料集 / 任務設定

這篇 paper 使用 **BluePrint** social media dataset 來 fine-tune agents。根據 paper 的描述，BluePrint 會用 user histories 計算 user embeddings，接著把相似使用者 cluster 成 persona archetypes。作者進一步修改 BluePrint 的做法：不只用使用者自己發的 messages，也納入使用者正向互動過的 posts，例如 likes、reposts，讓 user embedding 能反映更多行為。

作者對四個 base models 做 LoRA fine-tuning：

- Llama-3.1-Minitaur-8B
- Llama-3.1-8B
- Qwen2.5-7B-Instruct
- gemma-3-4b-pt

每個 base model fine-tune 出 25 個 LoRA adapters，對應 25 個 persona clusters。在模擬時，agent population 會依不同 proportions 設定分配這些 LoRAs。

實驗總共跑 **595 個 simulation roll-outs**。參數涵蓋：

- **agent 數量**：64、256、1024、4096
- **base model**：四種 base models，以及 Qwen non-finetuned ablation
- **network topology**：Erdős–Rényi random graph 或 directed scale-free graph
- **homophily initialization**：是否讓初始意見相近的 agents 在 network 中更接近
- **survey answers in context**：agent 是否知道自己先前的 survey answers
- **biased news agent**：是否放入一個偏向某個 survey option 的 news agent
- **LoRA proportions**：BluePrint、Uniform、Distribution、Average 等分配方式

Survey questions 則選擇能造成意見分裂的題目。作者先用 42 個 divisive multiple-choice questions，根據 entropy 挑出能讓 population 最接近 50/50 分裂的題目。最後選用的問題包含：

- 是否應允許使用 copyrighted material 訓練 AI models？
- 是否可接受用 genetic engineering 增強人類智力？
- 在 economic growth 與 environmental protection 之間，會投給哪類候選人？

這個設計的好處是：如果問題本身高度一面倒，就很難觀察 opinion dynamics；選擇高 entropy 題目可以讓 simulation 中的差異更容易浮現。不過，這也代表結果特別依賴這些 divisive questions，不能直接推論到所有社會議題。

### 3.2 模型 / 系統 / 演算法設計

作者的 simulator 是一個 social media-like environment。Agents 有 followership network，會觀察自己 follow 的人參與過的近期 thread，並發文或回覆。Agent activation 採 Zipfian distribution，讓少數高度活躍的「power users」推動大部分互動，這是為了模擬社群媒體常見的參與不均現象。

Fine-tuning 是這篇方法裡很重要的一環。作者認為 instruction-tuned commercial models 常常過度禮貌、過度同意、不願表達爭議性個人意見，這與真實社群媒體互動不太一致。因此，他們用 BluePrint 的社群媒體資料訓練 LoRAs，希望 agents 的發文風格與意見分布更接近人類。

作者也設計了幾種 LoRA population proportions：

- **Uniform**：每個 LoRA 負責 1/25 population
- **BluePrint**：依 BluePrint dataset 中各 cluster 的比例分配
- **Distribution**：用一組 models 作為 opinion basis，讓整體 population opinion distribution 接近人類分布
- **Average**：只對齊最常見的人類答案，而不是完整分布

這裡最有趣的是 Distribution vs Average。作者用 SimBench 的概念，把 human opinion matrix 記成 H，把每個 model 的 opinion matrix 記成 Mℓ，然後最佳化 convex weights wℓ，讓加權後的 model population opinion distribution 接近 human distribution。這是在問一個很重要的 simulation 問題：要模擬人群時，只抓「平均人」夠不夠？還是必須保留人類意見分布的多樣性？

### 3.3 評估方式

作者把 metrics 分成兩類。

第一類是接近 realism 的 proxy：**BERT human-vs-LLM classifier accuracy**。作者訓練一個 BERT classifier，分辨真實人類社群媒體 thread 和 LLM-generated simulation thread。若 classifier 比較難分辨，也就是 accuracy 比較低，作者將其解讀為 stylistically more realistic 的訊號。

這個 metric 很重要，但也要小心。作者自己也承認，這只是唯一的 realism metric，而且只是 stylistic realism，不代表社會動態就更真實。BERT detectability 低，最多說明文字風格比較不容易被辨識為 AI，不等於 opinion dynamics 或 network dynamics 和人類一致。

第二類 metrics 來自 survey responses，用來衡量 opinion dynamics。這些 metrics 沒有人類 baseline，因此作者明確說不能拿來宣稱某個 setting 更 realistic；它們只能用來比較不同設計參數如何影響 simulation outcomes。這點我覺得是這篇 paper 比較謹慎的地方。

主要結果分析包括：

- Social media fine-tuning ablation
- 不同 base models 對 consensus trajectories 的影響
- survey answers 放入 context 的影響
- design parameters 是否 additive 或 non-additive
- 各參數對 metrics 的 variance explained（η²）

作者設定比較嚴格的顯著性門檻：只有 p ≤ 0.001 才視為 statistically significant，避免因為大量 metrics / variables 導致 p-hacking。

## 4. 主要結果

### 4.1 Fine-tuning on social media data 的效果

作者先用 SimBench 檢查 fine-tuning 前後模型是否更貼近人類 opinion distribution。Table 1 顯示，除了 Minitaur 原本已經較強、fine-tuning 後略降之外，其他 models 的 SimBench score 都有提升：

- gemma-3-4b-pt：從 -3.42 到 1.78 ± 4.72，平均 +5.20
- Llama-3.1-8B：從 -0.06 到 1.14 ± 4.51，平均 +1.20
- Qwen-2.5-7B-Instruct：從 -34.87 到 -26.87 ± 11.90，平均 +8.00
- Llama-3.1-Minitaur-8B：從 13.23 到 12.46 ± 1.56，平均 -0.77

作者也提醒，SimBench 是 proxy，而且 benchmarks 可被 game；後面結果並不支持 SimBench score 和 stylistic similarity 或 opinion dynamics metrics 有明確相關。因此 SimBench 在這篇裡比較像 fine-tuning 合理性的前置檢查，不是最終 validity 證據。

在 Qwen ablation 中，fine-tuning 的效果更清楚。未 fine-tuned 的 Qwen 幾乎總是被 BERT classifier 識別為 AI：accuracy = 0.9999 ± 0.0008。加入 BluePrint LoRA 後，Qwen 的 BERT detectability 降到 0.9531 ± 0.0351。這仍然很高，但相較於近乎 100% 可偵測，已經有明顯改善。

更重要的是 Table 3 的 opinion dynamics：

- Opinion Shift Rate：BluePrint Qwen 0.210 ± 0.108；原始 Qwen 0.057 ± 0.097
- Majority Follow Rate：BluePrint Qwen 0.505 ± 0.064；原始 Qwen 0.275 ± 0.236
- NASR：BluePrint Qwen 0.078 ± 0.039；原始 Qwen 0.021 ± 0.036
- Net Consensus Change：BluePrint Qwen -0.055 ± 0.161；原始 Qwen 0.004 ± 0.048

作者的解讀是：沒有 persona LoRAs 時，agents 的 opinion dynamics 幾乎被壓扁。原始 Qwen 在一些問題上從一開始就接近 perfect consensus，因此很難產生 disagreement、persuasion 或 consensus change。BluePrint LoRAs 引入了 population heterogeneity，讓模擬更有社會動態。

這裡要小心的是，作者沒有說 fine-tuned 一定更真實；他們只說 fine-tuned models 產生更 believable threads 與更強的 opinion dynamics。是否更接近人類社會，仍缺少 ground-truth comparison。

### 4.2 Base model 是最重要的變因

Table 4 顯示，不同 base model 造成不同 consensus trajectory：

- Llama-3.1-Minitaur-8B-BluePrint：Initial Consensus 0.86，ΔConsensus -0.095 ± 0.112，83% runs with decreased consensus
- Qwen2.5-7B-Instruct-BluePrint：Initial Consensus 0.85，ΔConsensus -0.055 ± 0.161，70% runs with decreased consensus
- Llama-3.1-8B-BluePrint：Initial Consensus 0.79，ΔConsensus -0.027 ± 0.179，50% runs with decreased consensus
- gemma-3-4b-pt-BluePrint：Initial Consensus 0.73，ΔConsensus +0.025 ± 0.122，36% runs with decreased consensus

Minitaur 造成最強、最穩定的 consensus erosion；Gemma 則是唯一平均往 consensus gain 方向漂移的模型，但作者也指出這個差異在 variance 下不一定顯著。

我覺得這裡最值得注意的是：這個排序不是單純由 model size 或 architecture family 決定。Minitaur 和 Llama-3.1-8B 共享 Llama-3.1-8B base，但行為差很多，作者推測可能是 Minitaur 的 human cognition / social media persona fine-tuning 讓它具有更強的 individual opinionation。

在 variance explained 分析中，base model 是多個核心 metrics 的 dominant factor：

- Net Consensus Change：model η² = 0.090，secondary factor 是 ctx = 0.028
- BERT accuracy：model η² = 0.266，ctx = 0.264

這支持作者的主張：設計 Silicon Society 時，選哪個 base model 不是小細節，而是會主導模擬文字風格與 opinion dynamics 的核心選擇。

### 4.3 Survey answers 放進 context 會改變行為，而且效果 model-dependent

作者測試 agent 是否知道自己先前 survey answers。結果顯示，當 survey answers 被放進 context 時，BERT AI detectability 明顯升高：

- ctx=True：0.984 ± 0.023
- ctx=False：0.943 ± 0.043
- t = 14.2, p < 10^-15, d = 1.20

作者解釋是，模型知道 survey topic 後會 hyper-focus，導致每個 message 都圍繞 survey 主題，反而更像 AI-generated simulation thread，而不像自然社群媒體對話。

但 survey context 對 consensus change 的影響不是均一的。Table 5 顯示：

- Minitaur：ctx=True -0.095；ctx=False -0.095；p = 0.99，沒有影響
- Llama：ctx=True +0.015；ctx=False -0.067；p = 0.014，未達作者嚴格門檻
- Qwen：ctx=True -0.004；ctx=False -0.107；p < 0.001，有顯著影響
- Gemma：ctx=True +0.042；ctx=False +0.002；p = 0.11，沒有顯著影響

也就是說，讓 agents 記得自己的 survey answer 對 Qwen 影響很大，會降低 consensus erosion，使整體更穩定或往 consensus 方向移動；但對 Minitaur 和 Gemma 幾乎沒有可測量效果。

這是作者所謂 design space non-additive 的一個例子：同一個設計選擇，在不同 base model 上效果不同。

### 4.4 Design space 不是完全 additive，也不是完全混亂

作者把 design space 的 geometry 描述成 hybrid：有些參數效果相對獨立，有些則高度依賴 model identity 或 population scale。

相對 additive 的例子：

- homophily 對 assortativity shift 的方向穩定，且不太受 base model 或 population size 改變
- survey context 和 news agent 對 BERT detectability 的影響大致獨立，interaction contrast IC = -0.006

Non-additive / synergistic 的例子：

- survey context 對 consensus change 高度 model-dependent：對 Qwen / Llama 有效果，對 Minitaur / Gemma 沒有
- survey context 對 Majority Follow Rate 的影響和 population size 有 synergy：N ≤ 256 時不明顯，但 N = 1024 或 4096 時變得 robust

Table 6 顯示 survey context 對 MFR 的效果：

- 64 agents：-0.020，p = 0.36，不顯著
- 256 agents：+0.024，p = 0.25，不顯著
- 1024 agents：+0.075，p < 0.001，顯著
- 4096 agents：+0.064，p = 0.001，顯著

這對社會模擬研究很重要，因為它提醒我們：小規模 simulation 的結果不一定能外推到大規模 population；某些機制可能只有在規模放大後才出現。

### 4.5 Biased news agent 沒有可測量效果

作者設計了一個 biased news agent，放在 followership network 中 degree 最高的 node，並讓它發偏向某個 survey option 的 news posts。直覺上，這應該會影響 opinions。

但結果是：單一 biased news agent 沒有顯著影響 consensus change、opinion shift rate 或 BERT detectability：

- consensus change：p = 0.62
- opinion shift rate：p = 0.23
- BERT detectability：p = 0.34

作者提出兩個可能原因：一個 news agent 的 signal 太弱；或 network topology 限制了資訊擴散。這裡作者沒有進一步證明是哪一個原因，所以只能說「在本文設定下，單一 biased news agent 沒有可測量效果」。

## 5. 這篇 paper 的貢獻

- **把 Silicon Society 從單一 simulator 問題轉成 design-space 問題。** 作者不是提出另一個更複雜的 simulator，而是系統性分析設計參數如何影響 simulation outcomes。

- **用 595 個 roll-outs 量化多個設計參數的重要性與交互作用。** 這讓研究者能看到 base model、agent 數量、homophily、survey context、news agent、proportions 等設計選擇的相對影響。

- **證明 base model 是非常關鍵的設計選擇。** 在 BERT detectability 與 consensus change 上，base model 都是主要 variance explained factor。

- **提供 social media fine-tuning 的實驗證據。** BluePrint LoRA fine-tuning 讓 threads 比較不容易被 BERT classifier 偵測為 AI，也讓 opinion dynamics 更強。

- **指出 design space 的 hybrid geometry。** 有些參數接近 additive，有些參數則出現 model-dependent 或 scale-dependent interaction，不能只靠 marginal effects 推論。

- **對 validation gap 提供一個方法論方向。** 雖然它還不是完整 validation framework，但它示範如何從「設計參數如何影響結果」開始，建立更可累積的 simulator science。

## 6. 限制與需要小心的地方

> [!warning] 不要過度推論
> 這篇 paper 很適合拿來理解 Silicon Society 的設計敏感性，但它沒有證明哪個設定「最像真實社會」。作者的 metrics 多數沒有 human baseline，因此不能把 opinion dynamics metrics 直接解讀成 realism。

- **參數空間仍然很有限。** 作者自己承認，Silicon Society 的 parameter space 很大；他們只涵蓋一部分參數，每個參數也只測了一些 options。現有 7 類參數已經有 1024 種可能組合，但他們實際跑 595 roll-outs，仍不是完整 factorial coverage。

- **base model 和初始 consensus 可能 confounded。** 作者在 limitations 中明確提到，base model variable 與 question-specific initial consensus values 混在一起，例如 Qwen 在 Q28 一開始 consensus = 0.993，Gemma 在 Q29 是 0.562，這可能影響 within-question comparisons。

- **多重比較問題。** 作者做了 30+ statistical tests，但 p-values 沒有做 multiple comparison adjustment。作者因此設定 p < 0.001 作為顯著門檻，並提醒 p < 0.05 的邊際結果要小心。

- **BERT detectability 只是 stylistic realism proxy。** BERT classifier 分不出 AI，不代表社會互動邏輯、意見變化或網路動態就像人類。這一點作者有意識到，但仍然是研究設計的重要限制。

- **survey questions 很少且刻意挑 divisive questions。** 作者只選了少數 survey questions，而且是根據 entropy 挑出容易分裂 population 的題目。這有利於觀察 dynamics，但不一定代表一般政治、社會或消費議題。

- **simulated time horizon 很短。** 作者估計 2500 messages / 1024 agents 約等於 75 小時，這可能不足以觀察長期 social dynamics。作者也提到與既有研究差異可能和 shorter time horizons 有關。

- **news agent 結果不能泛化成「媒體不影響意見」。** 本文只能說在單一 biased news agent、特定 network placement、特定 simulation setup 下沒有可測量效果。不能推出 biased media 在 LLM societies 或真實社會中沒有影響。

- **三階以上交互作用沒有分析。** 作者只考慮最多兩個參數的 interaction，因為更高階交互作用數量爆炸。因此 design space 的複雜性可能仍被低估。

## 7. 跟 Morris 研究/學習的關聯

這篇跟 Morris 關心的 **silicon sampling / social simulation / harness engineering** 很直接相關，而且比單純「LLM 能不能模擬人」的 paper 更值得讀，因為它在問更底層的方法論問題：模擬系統的設計選擇如何影響結果？

第一，它提供了一個很好的 **harness engineering 範例**。作者沒有只展示 simulator demo，而是設計了 roll-out matrix、metrics、ablation、variance explained、interaction analysis。這種做法可以借到 Morris 之後做 LLM social simulation 或 silicon sampling 實驗：不是只問模型輸出像不像，而是系統性掃描 prompt、persona、memory、network、model、sampling 等參數。

第二，它提醒我們 **base model 不是可忽略的背景變因**。如果 Morris 之後想用不同 open-weight models 做 silicon-sampling 研究，這篇的結果暗示不能把模型當成同質 agent，只換 prompt 或 persona。不同 base model 可能在 opinion dynamics、consensus formation、style realism 上產生完全不同軌跡。

第三，它對 **persona / fine-tuning / distribution matching** 很有啟發。作者用 BluePrint LoRAs 製造 population heterogeneity，並比較 Uniform、BluePrint、Distribution、Average proportions。這對「如何建構一群 silicon agents」非常重要：我們要模擬的是平均人，還是整個人群分布？如果只用一個平均 persona，可能會壓扁社會動態。

第四，它也提醒 **validation 不應該只靠單一 realism metric**。BERT detectability、SimBench、survey opinion dynamics 都只是 proxy。若 Morris 未來做這方向，應該把 validation 拆成多層：文字風格、人類意見分布、短期互動、長期 network dynamics、對外部事件的反應等。

## 8. かに讀後判斷

我會把這篇列為 **值得深讀**，尤其如果 Morris 接下來真的要做 silicon sampling / social simulation 方向。它不是那種提供單一模型技巧的 paper，而是提供一個設計實驗的框架：如何把 LLM society 的設計參數拆開、掃描、量化、檢查交互作用。

建議優先讀：

1. **Introduction**：理解 validation gap 與 Silicon Society 定義
2. **Section 3.2 Variables**：看作者怎麼拆 design space
3. **Section 4 Fine-tuning on Social Media Data**：看 BluePrint LoRA 與 persona population 的設計
4. **Section 5 Results**：尤其 Table 3、Table 4、Table 5、Table 7
5. **Limitations**：這篇的限制寫得很重要，尤其 base model confounding 與 multiple comparisons

這篇最值得帶走的觀念是：LLM social simulation 的問題不只是「prompt 寫得像不像人」，而是整個 simulation stack 的設計都會改變結果。base model、fine-tuning、人口比例、survey context、agent 數量、network homophily 不是單純設定值，而是會互相作用的實驗變因。

如果要接到 Morris 的研究，我覺得這篇可以當作一個核心參考：未來在設計 silicon-sampling experiment 時，可以學它把參數空間明確化，並用 variance explained / interaction analysis 來回答「到底是哪個設計選擇在影響結果」。
