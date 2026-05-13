# DailyRead Agent Notes

## Graphify paper knowledge graph

This repository has a curated paper/domain knowledge graph at:

- `graphify-paper-kg/graphify-out/GRAPH_REPORT.md`
- `graphify-paper-kg/graphify-out/graph.json`
- `graphify-paper-kg/graphify-out/graph.html`

Scope: paper-related knowledge only, especially DeepRead reports and DailyRead domain notes. Do not add private assistant memory, mail/calendar/account information, or credentials to this graph.

Before answering cross-paper or domain-knowledge questions in this repo, read `graphify-paper-kg/graphify-out/GRAPH_REPORT.md` first, then prefer Graphify queries over raw grep when relationships matter:

```bash
graphify query "social simulation design space" --graph graphify-paper-kg/graphify-out/graph.json
graphify explain "topic:llm_based_social_simulation" --graph graphify-paper-kg/graphify-out/graph.json
graphify path "paper:2603.00113" "topic:llm_based_social_simulation" --graph graphify-paper-kg/graphify-out/graph.json
```

To rebuild the curated graph after adding new DeepRead reports or topic notes:

```bash
/Users/morris/.local/share/uv/tools/graphifyy/bin/python3 graphify-paper-kg/build_paper_graph.py
graphify global add graphify-paper-kg/graphify-out/graph.json --as DailyRead-paper-kg
```
