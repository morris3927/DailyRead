# GRAPH_REPORT — DailyRead Paper Knowledge Graph

這是針對 DailyRead paper / domain knowledge 建立的 Graphify-compatible knowledge graph。
目前刻意不匯入個人記憶、郵件、行事曆或帳號資訊。

## Scope
- DeepRead reports and metadata
- DailyRead domain/topic notes
- Paper-related domain knowledge only

## Stats
- Nodes: 59
- Edges: 106
- Papers / paper notes: 3
- Research topics: 6
- Methods / systems: 7

## Most connected nodes
- `The Silicon Society Cookbook: Design Space of LLM-based Social Simulations` — degree 26
- `AI Agents Alone Are Not (Yet) Sufficient for Social Simulation` — degree 19
- `Graphify Paper Knowledge Graph` — degree 15
- `LLM evaluation` — degree 14
- `Agent memory` — degree 10
- `Silicon Sampling Social Simulation: 2026-05-11` — degree 8
- `Harness Engineering: 2026-05-13` — degree 7
- `Silicon Sampling Social Simulation: 2026-05-12` — degree 7
- `Silicon Sampling Social Simulation: 2026-05-13` — degree 7
- `LLM-based social simulation` — degree 6
- `Harness engineering` — degree 6
- `Silicon sampling` — degree 5

## Suggested queries
- `graphify query "social simulation design space" --graph graphify-paper-kg/graphify-out/graph.json`
- `graphify query "agent memory knowledge graph" --graph graphify-paper-kg/graphify-out/graph.json`
- `graphify path "paper:2603.00113" "topic:llm_based_social_simulation" --graph graphify-paper-kg/graphify-out/graph.json`
- `graphify explain "topic:llm_based_social_simulation" --graph graphify-paper-kg/graphify-out/graph.json`

## Schema sketch
- Paper / paper_note → RELATED_TO_TOPIC → ResearchTopic
- Paper → USES_OR_DISCUSS_METHOD → Method/System
- Paper → CLAIMS / CONTRIBUTES / LIMITED_BY → Claim or Limitation nodes
- Domain note → DOCUMENTS_TOPIC / DOCUMENTS_METHOD → Topic or Method nodes
