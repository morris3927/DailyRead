# LangChain / LangGraph：Multi-Agent Architectures 概念導覽

- **影片標題**：Conceptual Guide: Multi Agent Architectures
- **URL**：https://www.youtube.com/watch?v=4nZl32FwU-o
- **發布日期**：2024-10-16

## 1. 影片在講什麼

這支影片是 LangChain 對 **multi-agent systems / multi-agent architectures** 的概念導覽。它不是教你怎麼寫 LangGraph 程式碼，而是在說：當一個 single-agent system 開始變複雜時，為什麼需要拆成多個 agents，以及拆開之後該怎麼設計 agent 之間的控制流與溝通方式。

影片一開始先定義 agentic system：一個系統越 agentic，代表越多 application control flow 是由 LLM 決定。為了讓討論簡化，影片採用常見入門定義：**agent 是一個會呼叫 tools 的 LLM**。從這個定義出發，single-agent system 就是一個 LLM 搭配多個 tools；multi-agent system 則是把過度複雜的單一 agent 拆成多個比較專門的 agents，並設計它們如何協作。

影片的核心觀點不是「agent 越多越好」，而是：**multi-agent architecture 的價值取決於 control flow、specialization、context management 和 communication pattern 是否設計得好。**

## 2. 為什麼 single-agent system 會不夠用

影片提出三個常見原因。

第一是 **too many tools**。當一個 agent 同時擁有太多 tools，它會更容易選錯工具。影片提到一個經驗值：大約 5–10 個 tools 常是單一 agent 可管理工具數量的甜蜜點。超過這個範圍後，不是工具越多越強，而是 decision space 變得太大，模型可能不知道下一步該叫哪個 tool。

第二是 **context too complex**。隨著工具呼叫、人類互動、任務歷史越來越多，single agent 的 context 會變得很長、很雜。這不只是 context window 長度問題，也是模型能不能在複雜上下文中維持正確控制流的問題。影片把這視為 single-agent system 擴張時很常見的失效點。

第三是 **need for specialization**。複雜任務常需要不同能力，例如 planner、researcher、math expert、coder。把所有專長塞進同一個 prompt，未必比拆成不同專門 agents 更好。multi-agent systems 的一個主要用途，就是讓不同 agents 專注在不同 domain 或子任務上。

## 3. Multi-agent systems 的好處

影片把 multi-agent systems 的好處整理成三個方向。

第一是 **modularity**。拆成多個 agents 後，每個 agent 可以獨立開發、測試與維護。這對 production system 很重要，因為問題不會全部混在一個巨大 prompt 或巨大 agent 裡。

第二是 **specialization**。每個 agent 可以被設計成特定 domain 的 expert，例如專門做研究、專門寫程式、專門做數學推理。這種專門化不只是角色命名，而是可以反映在 tool access、prompt、state、輸入輸出格式上。

第三是 **control**。LangGraph 這類框架的定位是提供較低階的控制能力，讓開發者能明確指定 agent 之間的 communication pattern。影片反覆強調，multi-agent system 的重點不是把多個 LLM 接起來，而是控制它們什麼時候溝通、共享什麼資訊、誰決定下一步。

## 4. 影片介紹的幾種 multi-agent architecture

### 4.1 Single-agent baseline

baseline 是一個 LLM 搭配多個 tools。這是最常見的起點，也通常是最簡單可行的設計。影片的意思不是 single-agent 不好，而是當任務、工具數量、context、專門化需求擴張後，single-agent 會遇到上述限制。

### 4.2 Network of agents

network of agents 是多個 agents 各自擁有 tools，並彼此溝通、決定誰下一個接手。影片提到 Swarm 和 CrewAI 常被視為這類架構。

但影片對這種架構很保留。原因是 communication pattern 太鬆散：如果任一 agent 在任一時間都能 route 到任一其他 agent，系統就很難控制。這種架構可能很彈性，但在 production 中容易變得不可靠、耗時、昂貴，因為它會產生大量 LLM calls。影片因此不太建議直接把這類 fully flexible network 用在 production。

這一點對理解 MAS 很重要：影片不是反對 agent network，而是反對沒有明確控制流的 agent network。

### 4.3 Supervisor-agent approach

supervisor 架構中，有一個 central supervisor agent 負責 route 到其他 sub-agents。sub-agents 專注完成自己的任務，不需要自己決定下一個該叫誰。

這比 network of agents 更可控。network 架構把 routing decision 分散在所有 agents 身上；supervisor 架構則把「下一步誰做」集中到 supervisor。這會降低 sub-agents 的負擔，也讓整體流程比較容易觀察與管理。

### 4.4 Supervisor with tools

supervisor with tools 是 supervisor 架構的簡化版本：把 sub-agents 包裝成 central LLM 可以呼叫的 tools。也就是說，sub-agent 在系統裡變成一種 tool interface。

這種設計的優點是簡單，容易用現有 tool-calling 機制實作。缺點是資訊傳遞比較窄：central LLM 呼叫 sub-agent 時，主要傳過去的是 tool call parameters。sub-agent 並不一定看到完整 shared state，而是只看到被包進 tool call 的輸入。影片後面用這點對比 shared-state communication。

### 4.5 Hierarchical approach

hierarchical 架構是把 supervisor 層層堆疊。一個 supervisor 可以呼叫某個 sub-agent，而那個 sub-agent 本身也可能是另一個 supervisor，下面再管理更多 agents。

這適合 sub-agents 很多、而且可以依照專業領域或任務結構分群的情境。它比單層 supervisor 更能處理大規模 agent 組織，但也更依賴好的分層與 routing 設計。

### 4.6 Custom cognitive architecture

影片最強調的是：production 中最常見、也最實際的架構，往往不是 off-the-shelf supervisor 或 hierarchical pattern，而是 **custom cognitive architecture**。

也就是說，開發者可以借用 supervisor、hierarchical、tool-calling、shared state 等常見技巧，但最後要根據 domain 自己設計控制流程。影片把這視為 LangGraph 的核心價值：提供足夠低階的控制能力，讓開發者能建立符合任務需求的 agent architecture，而不是只能套固定模板。

## 5. Agent 之間怎麼溝通

影片後半部真正重要的內容，是 agent communication。

第一種方式是 **shared state**。兩個 agents 可以共享一個 overall state object，裡面可能有 messages、artifacts 或其他 keys。不同 agents 可以讀寫這個 state。即使兩個 agents 的 internal state 不同，只要有共享 keys，它們就能透過這些 keys 交換資訊。例如 agent 1 產生 `foo`，agent 2 讀取 `foo` 後產生 `foobar`，讓 agent 1 後續可以使用。

第二種方式是 **tool-call parameters**。agent 1 呼叫 agent 2 時，只把想讓 agent 2 看到的資訊放進 tool call parameters。agent 2 根據這些參數工作，最後把結果作為 tool call response 回傳。這種方式更簡單、更封裝，但資訊邊界比較窄。

影片用這兩種方式來區分 supervisor 和 supervisor with tools：

- supervisor architecture：可以把 overall state 傳給 sub-agent。
- supervisor with tools：通常只把 tool call parameters 傳給 sub-agent。

這個差異很關鍵，因為它決定了 sub-agent 能看到多少上下文，也決定系統如何控制資訊流。

## 6. Message list 管理是 context engineering 問題

影片特別提到 messages list，因為 LangGraph 裡常見 state 是 message list，而多個 agents 可能都會讀寫同一份 messages。

如果把每個 agent 的 tool calls、內部過程和 final response 全部 append 到共享 message list，優點是資訊完整；缺點是 message list 很快變得很大、很吵，包含大量不一定需要被其他 agents 看到的內部工具呼叫紀錄。

另一種做法是：shared message state 只放 final responses，各 agent 的 internal tool calls 保存在各自內部的 message list。這樣共享上下文更精簡，也能避免把所有 agent 的內部過程混在一起。

這段其實是影片最實用的工程提醒：multi-agent system 的問題不是只有 routing，還包括 **哪些資訊應該共享、哪些資訊應該隔離、全域 context 要放到多細**。這和一般把 MAS 想成「多個人聊天」很不一樣；在 production 裡，context 設計本身就是架構設計的一部分。

## 7. 和兩篇 paper 的對讀點

### 7.1 對讀 MacNet / Scaling Large-Language-Model-based Multi-Agent Collaboration

MacNet paper 關心的是 agent topology 如何影響 collaboration performance，例如 chain、tree、mesh、random graph 等拓樸。LangChain 影片則從工程角度提醒：完全自由的 network of agents 雖然彈性高，但 production 中控制性不足、成本高、可靠性差。

這兩者可以一起看：MacNet 是研究上對 topology 的系統比較；LangChain 影片則提醒 production architecture 不能只看「連得多不多」，還要看 control flow 是否可控、context 是否可管理、LLM calls 是否過多。

也就是說，MacNet 的 topology 比較可以回答「不同網路結構表現如何」；LangChain 影片則回答「工程上為什麼不能隨便讓所有 agents 互相 route」。

### 7.2 對讀 Multi-Agent Debate 評估 paper

`If Multi-Agent Debate is the Answer, What is the Question?` 那篇指出，多 agent debate 常常沒有穩定贏過 strong single-agent baselines，例如 CoT 或 Self-Consistency，而且成本更高。

LangChain 影片從工程端給出類似警訊：network of agents 容易不可靠、耗時、昂貴，不能因為「多 agent」看起來合理就直接用。兩者共同指向一個結論：MAS 的價值不在 agent 數量，而在差異化能力、資訊流設計、成本控制和可驗證效果。

影片談 specialization；MAD 評估 paper 談 model heterogeneity。兩者其實在說相近的事：如果多 agent 只是多個相似模型互相講話，價值可能有限；如果每個 agent 有不同能力、不同工具、不同資訊邊界，MAS 才比較可能有實質意義。

## 8. かに讀後判斷

這支影片很適合作為 MAS engineering 的入門框架。它沒有提供實驗數字，也不是研究 paper，但它把 production multi-agent system 最容易被忽略的幾個問題講得很清楚：工具數量、context 複雜度、specialization、routing、shared state、tool-call parameters、message list 管理。

我覺得最值得帶走的是三點：

1. **不要把 MAS 理解成「多個 agents 自由聊天」**。真正重要的是 control flow 和 communication pattern。
2. **network of agents 不一定適合 production**。完全自由 routing 會帶來可靠性、成本與控制問題。
3. **custom cognitive architecture 才是重點**。supervisor、hierarchical、tool-calling 都只是可借用的 pattern；最後要依 domain 設計自己的資訊流與控制流。

如果要和兩篇 paper 一起讀，這支影片可以補上工程視角：MacNet 告訴我們 topology 會影響 performance；MAD 評估 paper 告訴我們多 agent 不一定贏 strong single-agent baseline；LangChain 影片則提醒我們，真正落地時要先問控制流、context 和 communication 是否設計得夠清楚。