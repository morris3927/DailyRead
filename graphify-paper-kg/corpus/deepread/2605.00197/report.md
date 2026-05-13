# 🧠 詳細閱讀報告｜The Silicon Society Cookbook

> [!info] Paper Info
> **完整標題**：The *Silicon Society* Cookbook: Design Space of LLM-based Social Simulations  
> **作者**：Aurélien Bück-Kaeffer, Sneheel Sarangi, Maximilian Puelma Touzel, Reihaneh Rabbany, Zachary Yang, Jean-François Godbout  
> **來源**：arXiv:2605.00197v1；comments 標示為 under review at COLM 2026  
> **日期**：2026-04-30 submitted；arXiv v1  
> **論文類型**：empirical / system analysis / benchmark-style design-space study  
> **報告語言**：繁體中文

**Tags**：#LLM #SocialSimulation #MultiAgentSystems #AgentBasedModeling #Evaluation #SiliconSociety

> [!summary] 一句話總結
> 這篇 paper 關注的是以 LLM 模擬人類社會互動的 **Silicon Societies**，核心問題是：當研究者建立 LLM-based social simulator 時，base model、網路拓樸、homophily、survey context、新聞代理與 persona/LoRA 比例等設計選擇，究竟會如何改變模擬結果？作者的貢獻不是提出一個「最真實」的社會模擬器，而是用 595 次 simulation roll-outs 系統性掃描設計空間。最重要的發現是 base LLM 是最具影響力的因素，對 BERT AI-detectability 的單因子解釋量為 η²=0.266，對 net consensus change 為 η²=0.090；BluePrint 社群媒體 LoRA fine-tuning 會降低 AI 可偵測性並強化 opinion dynamics，而單一 biased news agent 在 paper 的設定中沒有可測得效果。

## 1. 研究定位：這篇 paper 放在哪條研究線？

這篇 paper 位在 **LLM-based social simulation / generative agent-based modeling / multi-agent social networks evaluation** 這條研究線上。它回應的是近年大量「用 LLM 代理人模擬人類社會互動」工作的共同問題：系統越做越複雜，但驗證標準與設計選擇的影響仍然不清楚。作者明確指出，他們不是要涵蓋所有 multi-agent frameworks，也不是討論為了完成 coding 等任務的 agent systems；他們把範圍限縮在「以 human-likeness 為目標、模擬人類互動」的 Silicon Societies。

- **研究線**：LLM social simulators、Agent-Based Models with LLM agents、Silicon Societies validation、social network simulation。
- **論文類型**：主要是 empirical design-space analysis；同時包含自建 simulator 與 fine-tuning ablation。
- **它想補上的缺口**：既有 LLM social simulation 常展示 macro phenomena，例如 echo chambers、herding 或 information propagation，但缺乏對設計參數如何影響結果的系統性理解。作者認為，如果不知道 base model、網路結構、persona 配置、context 設計等因素各自與交互作用的影響，後續研究很難比較、累積或驗證模擬器的 realism。

這篇 paper 在 literature review 裡可被引用為：一篇針對 LLM social simulations 設計空間的 empirical mapping 工作，特別是用多參數 roll-out 分析 base model、fine-tuning、population size、survey context、homophily 等變因對 opinion dynamics 與 stylistic realism proxy 的影響。

## 2. 研究問題與動機

作者的核心問題可以拆成三層：

第一，**Silicon Society 要怎麼驗證？** 傳統 ABM 已經很難驗證，LLM-based social simulation 更麻煩，因為它同時涉及 micro-level 的個體訊息生成、互動行為，以及 macro-level 的共識、分化、資訊擴散等現象。paper 指出，目前領域尚未形成標準 validation metric，人類 baseline 也通常昂貴且任務特定。

第二，**如果暫時不主張哪個 simulator 最真實，那至少要知道設計選擇會造成什麼後果。** 作者選擇把問題從「打造最 realistic 的 simulator」轉成「mapping design space」：當我們改變 base model、agent 數量、網路拓樸、homophily、survey context、news agent、persona/LoRA proportions 時，simulation trajectories 和 metrics 會怎麼變？

第三，**這些設計因素是否可以加總式理解？** 作者假設 design space 不會完全 additive。也就是說，不能只看 A 參數單獨增加某 metric、B 參數單獨增加某 metric，就推論 A+B 一定更強。paper 的結果最後也支持一個比較細緻的說法：有些因素近似 additive，有些則受到 base model 或 population scale gating。

我覺得這個動機有價值，因為它把 LLM social simulation 從「展示有趣現象」推向「做可比較、可診斷的實驗設計」。對社會科學或資管研究來說，這比單純宣稱 agent 看起來像人更重要。

## 3. 作者的方法到底在做什麼？

整體 pipeline 是：作者自建一個 social network simulator，讓 LLM agents 在 follower graph 中觀察 thread、發文或回覆；每隔固定步數用 survey question 測量 agent opinions；再用多組 simulation parameters 跑 595 次 roll-outs，分析哪些設計選擇影響文字風格的 AI 可偵測性與 opinion dynamics。除了主實驗，作者也做 Qwen2.5-7B-Instruct 有無 BluePrint LoRA fine-tuning 的 ablation，用來檢查社群媒體 fine-tuning 是否真的改變 simulation 行為。

### 3.1 資料集 / 任務設定

**社群媒體資料與 persona 來源**：作者使用 BluePrint dataset。BluePrint 原本以 user histories 建立 user embeddings 並 cluster 成 persona archetypes；這篇 paper 延伸 BluePrint 的做法，不只用使用者自己發的 messages，也加入使用者正向互動過的 posts，例如 likes、reposts，讓不常發文但會互動的使用者也能進入 persona clustering。

**LoRA 與 population proportions**：每個 base model fine-tune 25 個 LoRA adapters，對應 25 個 persona clusters。因為 simulation 中 agent 數量大於 25，所以每個 LoRA 會負責 population 的一部分。作者測四種 proportions：

- **Uniform**：每個 LoRA 負責 1/25 population。
- **BluePrint**：依 BluePrint dataset 中各 cluster 的實際比例分配。
- **Distribution**：用一組 LoRA models 的加權組合去 match SimBench human opinion distribution。
- **Average**：不是 match 完整分布，而是 match 每題最常見的人類答案。

Distribution 和 Average 的設計是這篇方法中比較有趣的地方。作者把一群 models 看成 opinion space 的 basis，用 convex weighted sum 去逼近人類 survey response distribution。paper 報告在 Minitaur 上，Distribution 與 Average 的 SimBench scores 分別為 17.08 與 17.05，高於最佳單一 model 的 14.60，但兩者的 weight distributions 很不同。

**survey questions**：作者先用 42 個可能具爭議性的 multiple-choice questions，根據 fine-tuned LoRA population 的 answer distribution entropy 選題。主要使用 3 個 survey questions：

- Q25：是否應合法使用 copyrighted material 來訓練 AI models？Yes/No；entropy 0.9993。
- Q28：政府是否應提供免費 healthcare？Yes/No；在 appendix 表 11 entropy 0.9173。
- Q29：recreational marijuana 是否應合法化？Yes/No；在 appendix 表 11 entropy 0.9145。

paper 也指出，選項順序會大幅影響 LLM 回答分布，例如「Donald Trump or Kamala Harris」和「Kamala Harris or Donald Trump」排名差異很大。這呼應 human survey 與 LLM response bias 的已知問題。

### 3.2 模型 / 系統 / 演算法設計

**simulator 設定**：作者為了不被既有 simulator 的 assumptions 限制，自建 social network simulator。每次 simulation 建立一群 agents，並建立 followership network。agents 有固定的 action probability；每個 simulation step 選 10 個 agents：前 9 個觀察其 follow 的人參與過的近期 thread，最後 1 個 agent 有 1/3 機率開新 thread、2/3 機率回覆既有 thread。

**時間與規模**：每次 simulation 跑 2500 steps，每 250 steps survey 一次，因此包含 step 0 到 step 2500 共 11 次 surveys。作者用 BluePrint 中平均每人每月 24.3 messages 估算，1024 agents 的 2500 messages 約相當於 75 小時 simulated time。每次 simulation 在 A100 GPU 上約需 2 到 11 小時，依參數而異。

**七個 design variables**：

- agent 數量：64、256、1024、4096。
- base model：Llama-3.1-Minitaur-8B、Llama-3.1-8B、Qwen2.5-7B-Instruct、gemma-3-4b-pt。
- network topology：ER random graph 或 directed scale-free graph。
- homophily initialization：是否讓初始意見相近的 agents 在網路中更靠近。
- survey context：agent 是否知道自己的 survey answers；若是，survey questions 與 agent answers 會加入 context。
- biased news agent：是否放入一個偏向某 survey option 的 news agent；若是，news agent 會放在最高 degree node，產生由 Gemini 3.1 預先生成、偏向某選項的 news posts。
- proportions：BluePrint、Uniform、Distribution、Average；若是未 fine-tuned Qwen ablation，則有 None。

**homophily 的實作**：appendix 說明 homophily initialization 是 spatial-opinion alignment。先用 NetworkX spring layout 將 graph 放到 2D 空間，再依 x-coordinate 排序 nodes；同時計算 agents / LoRA profiles 的 expected opinion scores 並排序，最後把 opinion-sorted agents 指派到 spatially ordered nodes。因為 spring layout 會讓 connected nodes 比較接近，這樣會讓鄰居更可能有相似初始意見。

**fine-tuning 設計**：作者用 LoRA 在 BluePrint social media data 上 fine-tune 四個 base models。Qwen 是四者中唯一 instruction-tuned model；作者提到選擇包含非 instruction-tuned model，是因為已有有限證據指出 instruction tuning 可能壓縮 answer diversity，而模擬社會互動時 diversity 可能重要。

### 3.3 評估方式

作者很小心地區分 **realism proxy** 與 **opinion dynamics metrics**。

**唯一 realism proxy** 是 BERT human-vs-LLM classifier accuracy。作者訓練一個以 Zhang et al. (2022) 為基礎的 BERT classifier，區分 BluePrint 中真實人類 thread 與 simulation 產生的 LLM thread。訓練資料總計 200,000 samples，並避免 data leakage。每個 simulation 約用 150 threads 作 test set。若 classifier 越難判斷 thread 是 AI 產生，作者就解讀為文字風格更接近人類社群媒體文本。

> [!warning] 這裡不能過度解讀
> paper 自己也強調，BERT detectability 只是 stylistic realism proxy，不等於整個 social simulator 在社會科學上 validated。其他 survey-based metrics 沒有人類 baseline，因此不能用來主張某設定「比較真實」。

**opinion dynamics metrics** 主要包括：

- **Consensus**：最大意見陣營占 population 的比例。
- **Net Consensus Change, NCC**：final consensus 減 initial consensus。
- **Opinion Shift Rate, OSR**：兩次 survey snapshot 間改變意見的人口比例。
- **Majority Follow Rate, MFR**：改變意見者中，轉向當前 majority opinion 的比例。
- **Neighbor Alignment Shift Rate, NASR**：轉向直接鄰居 majority opinion 的人口比例。
- **Assortativity**：同意見 agents 是否傾向彼此連結的 network assortativity coefficient。

統計上，作者為了避免 p-hacking，設定 p≤0.001 才視為 statistically significant。limitation 中也說明多重比較沒有調整，因此 p<0.05 的 marginal results 要謹慎看待。

## 4. 主要結果

### 4.1 最重要的發現

**發現一：BluePrint social media fine-tuning 讓 Qwen 文字較不容易被 BERT 判為 AI，也讓 opinion dynamics 變強。**

在 Qwen2.5-7B-Instruct 的 ablation 中，未 fine-tuned Qwen 生成的 threads 幾乎總是被 BERT classifier 判為 AI，accuracy 為 0.9999±0.0008，n=72。BluePrint LoRA 版本則為 0.9531±0.0351，n=151，差異達 d=1.62, p<0.001。這表示 fine-tuning 讓文字風格更不容易被 BERT 偵測為 AI，但 accuracy 仍高達約 95%，所以不能說它已經完全像人。

opinion dynamics 上，fine-tuned Qwen 的 OSR 為 0.210±0.108，未 fine-tuned Qwen 為 0.057±0.097；MFR 分別為 0.505±0.064 與 0.275±0.236；NASR 分別為 0.078±0.039 與 0.021±0.036；NCC 分別為 -0.055±0.161 與 0.004±0.048。作者解讀為：沒有 persona LoRAs 時，agents 幾乎給出相同 default opinions，起始 consensus 接近滿分，因此 disagreement、persuasion、consensus change 都被壓低。

這個結果支持作者的 fine-tuning 選擇，但也有一個重要 caveat：沒有 ground-truth human simulation baseline，所以不能說 fine-tuned 版本「比較真實」，只能說它更像 social media text 且在 paper 的 metrics 中有更強動態。

**發現二：base model 是最重要的設計選擇。**

四個 BluePrint LoRA models 的 consensus trajectories 不同。Minitaur 造成最強、最一致的 consensus erosion；Gemma 平均上反而略往 consensus gain 方向移動，但差異相對 variance 不顯著。paper 報告：

- Llama-3.1-Minitaur-8B-BluePrint：n=169，initial consensus 0.86，ΔConsensus -0.095±0.112，83% runs consensus 下降。
- Qwen2.5-7B-Instruct-BluePrint：n=151，initial consensus 0.85，ΔConsensus -0.055±0.161，70% runs consensus 下降。
- Llama-3.1-8B-BluePrint：n=111，initial consensus 0.79，ΔConsensus -0.027±0.179，50% runs consensus 下降。
- gemma-3-4b-pt-BluePrint：n=92，initial consensus 0.73，ΔConsensus +0.025±0.122，36% runs consensus 下降。

ANOVA-style 單因子解釋量也支持 base model 的重要性：對 BERT accuracy，model η²=0.266；對 net consensus change，model η²=0.090。這是 paper 最核心的 design-space takeaway：LLM social simulator 的結果不能只看網路拓樸或 agent 數量，base model 本身會主導很多結果。

**發現三：survey context 會改變文字與 opinion dynamics，但效果依 model 與 population size 而變。**

如果讓 agents 在 context 中看到自己的 survey answers，BERT AI detectability 會升高：ctx=True 為 0.984±0.023，ctx=False 為 0.943±0.043，t=14.2, p<10^-15, d=1.20。作者的解釋是，agents 會過度聚焦 survey topic，導致每個 message 都像在談 survey，讓 AI thread 更容易被 classifier 抓出來。

但 survey context 對 consensus change 的效果不是一致的：Minitaur 幾乎沒有差異；Qwen 在 ctx=True 時 consensus erosion 明顯減弱，ctx=True -0.004 vs ctx=False -0.107，p<0.001；Llama 有 p=0.014 的差異但未達作者主要顯著門檻；Gemma 無顯著效果。對 MFR 的影響也跟 population size 有 synergy：64 與 256 agents 時不顯著，1024 agents 時 +0.075, p<0.001，4096 agents 時 +0.064, p=0.001。

這支持 paper 對 design-space geometry 的結論：有些參數效果會被 base model 或 scale gate 住，不能只看 marginal effect。

**發現四：biased news agent 在本設定中沒有可測得效果。**

作者放入一個 biased news agent，放在最高 degree node 並生成偏向某 survey option 的 news posts，但在 paper 報告的指標中沒有 measurable effect：對 consensus change p=0.62、opinion shift rate p=0.23、BERT detectability p=0.34。作者提出兩個可能原因：單一 news agent 訊號太弱，或 network topology 限制了擴散。目前從 paper 可見內容無法確認是哪一個原因。

**發現五：design space 是 hybrid geometry，不是完全 additive，也不是全都混亂。**

作者指出有些因素相對穩定，例如 homophily 對 assortativity shift 的效果方向一致；survey context 與 news agent 對 BERT detectability 的 interaction contrast 為 -0.006，近似 additive。另一方面，survey context 對 consensus change 的影響高度 model-dependent，對 MFR 的影響又與 population size 有 synergy。這讓作者總結 Silicon Society 設計空間是「部分 additive、部分 non-linear interactions」。

### 4.2 消融實驗或細部分析

**fine-tuning ablation 是這篇最重要的 ablation。** 未 fine-tuned Qwen 使用短 prompt 加上從 Li et al. (2025) 隨機抽樣的 meta-personality，例如 age、sex、race、state。結果顯示，單靠 prompt/persona metadata 並沒有產生足夠的 starting opinion heterogeneity；Qwen 對 Q25 與 Q28 的 initial consensus 為 1.000，對 Q29 為 0.907。這解釋了為什麼未 fine-tuned 版本的 opinion shift 被壓低。

**SimBench fine-tuning 結果需要保守解讀。** Table 1 顯示 fine-tuning 後多數模型 SimBench scores 平均提高：Gemma 從 -3.42 到 1.78±4.72，Llama 從 -0.06 到 1.14±4.51，Qwen 從 -34.87 到 -26.87±11.90；Minitaur 則從 13.23 到 12.46±1.56，略降。作者也明確說 SimBench benchmark 是 proxy，後續結果不顯示 SimBench score 與 human stylistic similarity 或 opinion dynamics metrics 有相關。因此，SimBench 在這裡是 fine-tuning 合理性的輔助證據，不是最終 validation。

**agent 數量對 OSR 的效果可能是測量 artifact。** Table 7 顯示 number of agents 對 Opinion Shift Rate 的 η²=0.230，是 OSR 的 dominant factor，secondary 是 model η²=0.200。但 appendix A.4 說這很可能是 survey frequency artifact：每 250 steps survey 一次，agent 越多，在 interval 中有機會 act/observe 的比例越小，因此觀察到的 opinion change 會下降。這是一個作者主動揭露的限制，讀結果時要非常小心。

## 5. 這篇 paper 的貢獻

- **把 LLM-based social simulation 的設計選擇變成可比較的 empirical design-space 問題。** 它不是只展示一個 simulator，而是系統性測 595 次 roll-outs，量化七個參數對多個 metrics 的影響。

- **指出 base model choice 是 Silicon Society 結果的主導因素之一。** 對 BERT detectability 與 net consensus change，base model 都是最重要或最具代表性的解釋因素，提醒後續研究不能把「LLM agent」當成可互換元件。

- **提供 social media LoRA fine-tuning 對 stylistic realism proxy 與 opinion dynamics 的 evidence。** Qwen ablation 顯示 BluePrint LoRA 讓 generated threads 較不容易被 BERT classifier 判為 AI，也讓 opinion shifts、majority following、neighbor alignment 等動態變強。

- **清楚區分 realism proxy 與 dynamics metrics。** paper 沒有過度宣稱 survey-based metrics 代表 human realism，而是把它們當成設計因素如何改變 simulation outcomes 的診斷工具。這點在方法論上值得肯定。

- **提出 design space 的 hybrid geometry 觀點。** 有些效果近似 additive，有些 interaction 依賴 model 或 population scale；這比「所有參數都很重要」的籠統說法更有研究價值。

## 6. 限制與需要小心的地方

> [!warning] 不要過度推論
> 這一節只根據 paper 內容與可見證據評論。若 paper 沒提供足夠資訊，我會直接標示「目前從 paper 可見內容無法確認」。

- **沒有真正的人類社會動態 baseline。** BERT classifier 只能當文字風格 proxy；survey dynamics metrics 沒有 human baseline，因此不能說某個設定的 opinion dynamics 更真實。

- **參數空間仍非常有限。** 作者測了七個 variables，但每個 variable 的 options 都有限；例如 network topology 只有 ER 與 directed scale-free，news agent 只有 0 或 1。這篇是 narrow mapping，不是完整 design-space coverage。

- **base model 與 question-specific initial consensus 有 confounding。** paper 自己指出，例如 Qwen 在 Q28 起始 consensus 0.993、Gemma 在 Q29 起始 consensus 0.562，這會影響 within-question comparisons。

- **多重比較未調整。** 作者做了 30+ tests，雖然設定 p≤0.001 作主要顯著門檻，但 nominal p<0.05 的結果可能是假陽性；paper 也提醒讀者要謹慎。

- **只考慮二階 interaction，沒有分析三個以上參數的交互作用。** 這是可理解的，因為 combinations 會爆炸，但也代表 design geometry 仍可能有未被看見的 higher-order effects。

- **simulation time horizon 短。** 1024 agents 的 2500 messages 被估算為約 75 小時 simulated time。作者也提到，與既有 literature 中未 fine-tuned simulator 仍可出現 opinion dynamics 的差異，可能來自他們較短的 time horizons。長期穩定性目前從 paper 可見內容無法確認。

- **BERT classifier 的訓練資料與泛化仍需小心。** paper 說使用 200,000 samples 並避免 data leakage，但 classifier 是否對不同 topic、不同語域、不同平台仍穩健，目前從 paper 可見內容無法確認。

- **biased news agent 無效不代表 misinformation/news agents 一般無效。** 這只是在「一個 news agent、最高 degree node、特定預生成 biased posts、特定 simulation setup」下無顯著效果。若增加 news agents、改變 posting frequency、改變 network diffusion mechanics，結果可能不同；paper 沒有測。

## 7. 跟 Morris 研究/學習的關聯

這篇跟 Morris 的資管背景有幾個連結。

第一，它是很好的 **AI agents / social simulation evaluation** 案例。資管研究常關心數位平台、社群媒體、資訊擴散、輿論與組織/市場行為。這篇提醒我們：若用 LLM agents 模擬使用者或社群，不應只看生成內容是否「像人」，還要問 design choices 如何塑造結論。

第二，它提供一個可學的 **multi-factor experimental design**。作者沒有只比較一兩個模型，而是把 simulator design variables 明確列出，搭配 randomized roll-outs、effect size、η²、interaction analysis。這種寫法可借鑑到 MIS 或 HCI 研究中的 simulation-based evaluation。

第三，它對 **persona-based user simulation** 很有警示。未 fine-tuned Qwen 加上 meta-persona 仍然產生高度一致的 default opinions，表示 demographic persona prompt 未必足以產生有效 heterogeneity。若 Morris 未來做 user simulation、AI customer agents、educational agents 或 social platform experiment，這點很重要。

第四，它也呼應 **LLM evaluation 的 proxy 問題**。BERT AI-detectability、SimBench、survey dynamics 都只是 proxy。paper 的好處是作者沒有把 proxy 說成真實世界 ground truth；這種證據邊界意識值得學。

## 8. かに讀後判斷

我覺得這篇值得 Morris 深讀，尤其如果你關心 AI agents、社群模擬、LLM evaluation 或資管中的 digital platform simulation。它不是一篇「提出新模型架構」的 paper，而是方法論上很有用的 design-space 實證研究。

建議閱讀順序：

1. 先讀 Introduction，看作者如何把 Silicon Society validation gap 定位出來。
2. 再讀 3.2 Variables 和 3.3 Metrics，掌握七個 design variables 與 metrics 邊界。
3. 重點讀 5.1 fine-tuning ablation、5.2 base models、5.4 geometry、5.5 ANOVA。
4. 最後讀 limitations，因為這篇的價值很大一部分在於它知道自己不能證明什麼。

可以帶走的核心觀念是：**LLM social simulation 的結果不是 simulator 自然流出的客觀社會現象，而是 base model、fine-tuning、context 設計、survey 設計、network setup 與 measurement protocol 共同產生的結果。** 如果後續研究沒有把這些設計選擇打開來檢查，就很容易把 artifact 當成 social insight。

## 附：結果 / 方法重點圖

![[assets/design-space-summary.svg]]

- Mermaid spec：`assets/design-space-summary.mmd`
- SVG 圖檔：`assets/design-space-summary.svg`

這張圖把 paper 的流程與主要發現整理成四段：設計空間 → simulator roll-outs → metrics → empirical findings。適合放在 Obsidian note 或 DailyRead 的 assets 中一起看。
