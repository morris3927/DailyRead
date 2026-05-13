#!/usr/bin/env python3
"""Build a curated Graphify-compatible knowledge graph for DailyRead papers.

This deliberately focuses on paper/domain knowledge only. It does not ingest
OpenClaw MEMORY.md, mail/calendar state, or private account notes.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import networkx as nx
from graphify.export import to_html, to_json

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
CORPUS = ROOT / "corpus"
OUT = ROOT / "graphify-out"

COMMUNITIES = {
    0: "Papers",
    1: "Authors",
    2: "Research Topics",
    3: "Methods / Systems",
    4: "Claims / Findings",
    5: "Limitations / Caveats",
    6: "Projects / Corpora",
}

TOPIC_KEYWORDS = {
    "LLM-based social simulation": ["social simulation", "silicon societ", "agent-based", "society"],
    "Silicon sampling": ["silicon sampling", "silicon societ", "simbench"],
    "Agent memory": ["agent memory", "memory", "persistent", "long-term"],
    "Harness engineering": ["harness", "observability", "evaluation harness"],
    "LLM evaluation": ["evaluation", "benchmark", "metric", "detectability", "validation"],
    "Domain knowledge graph": ["knowledge graph", "graphify", "structured knowledge"],
}

METHOD_KEYWORDS = {
    "Environment-involved Markov game formalization": ["markov game", "environment-involved"],
    "Visibility / exposure mechanism": ["visibility", "exposure"],
    "Scheduler / activation order": ["scheduler", "activation", "turn order"],
    "Design-space roll-out analysis": ["design space", "roll-outs", "595"],
    "BluePrint social media LoRA": ["blueprint", "lora"],
    "ANOVA effect-size analysis": ["anova", "η²", "effect"],
    "Graphify paper knowledge graph": ["graphify", "knowledge graph"],
}


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    return re.sub(r"_+", "_", text).strip("_").casefold()[:140]


def add_node(G: nx.Graph, node_id: str, label: str, file_type: str, source_file: str, community: int, **attrs):
    G.add_node(
        node_id,
        label=label,
        file_type=file_type,
        source_file=source_file,
        community=community,
        norm_label=unicodedata.normalize("NFKD", label).lower(),
        **attrs,
    )


def add_edge(G: nx.Graph, src: str, tgt: str, relation: str, source_file: str, confidence: str = "EXTRACTED", **attrs):
    if src == tgt:
        return
    G.add_edge(
        src,
        tgt,
        relation=relation,
        confidence=confidence,
        confidence_score={"EXTRACTED": 1.0, "INFERRED": 0.7, "AMBIGUOUS": 0.4}.get(confidence, 1.0),
        source_file=source_file,
        _src=src,
        _tgt=tgt,
        **attrs,
    )


def read_summary(report: str) -> str:
    m = re.search(r"> \[!summary\].*?\n>\s*(.+?)(?:\n\n##|\Z)", report, re.S)
    if m:
        return " ".join(line.strip().lstrip("> ") for line in m.group(1).splitlines()).strip()
    return ""


def extract_section(report: str, number: int) -> str:
    m = re.search(rf"\n## {number}\. .*?\n(.+?)(?=\n## \d+\.|\n## 附|\Z)", report, re.S)
    return m.group(1).strip() if m else ""


def sentences(text: str, limit: int = 3) -> list[str]:
    raw = re.split(r"(?<=[。.!?])\s+|\n+", text)
    out = []
    for s in raw:
        s = re.sub(r"\s+", " ", s).strip(" -*：:")
        if 35 <= len(s) <= 220 and not s.startswith("目前從 paper"):
            out.append(s)
        if len(out) >= limit:
            break
    return out


def match_terms(text: str, table: dict[str, list[str]]) -> Iterable[str]:
    low = text.lower()
    for label, keys in table.items():
        if any(k.lower() in low for k in keys):
            yield label


def add_topic_or_method(G: nx.Graph, label: str, community: int, source_file: str) -> str:
    prefix = "topic" if community == 2 else "method"
    nid = f"{prefix}:{slug(label)}"
    add_node(G, nid, label, "concept", source_file, community)
    return nid


def build() -> nx.Graph:
    G = nx.DiGraph()

    # Project/corpus anchors
    add_node(G, "project:dailyread", "DailyRead", "concept", "README.md", 6)
    add_node(G, "corpus:graphify_paper_kg", "Graphify Paper Knowledge Graph", "concept", "graphify-paper-kg/README.md", 6)
    add_edge(G, "corpus:graphify_paper_kg", "project:dailyread", "INDEXES_PROJECT", "graphify-paper-kg/README.md")

    for report_path in sorted(CORPUS.glob("deepread/**/report.md")):
        rel = report_path.relative_to(CORPUS).as_posix()
        report = report_path.read_text(encoding="utf-8")
        meta_path = report_path.with_name("metadata.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        title = meta.get("title") or re.search(r"完整標題\*\*：(.+)", report)
        title = title if isinstance(title, str) else (title.group(1).strip() if title else report_path.parent.name)
        paper_id = f"paper:{meta.get('arxiv_id') or slug(title)}"
        summary = read_summary(report)
        add_node(
            G, paper_id, title, "paper", rel, 0,
            arxiv_id=meta.get("arxiv_id"), doi=meta.get("doi"), url=meta.get("url") or meta.get("abs_url"),
            paper_type=meta.get("paper_type"), summary=summary[:700]
        )
        add_edge(G, "corpus:graphify_paper_kg", paper_id, "CONTAINS_PAPER", rel)
        add_edge(G, "project:dailyread", paper_id, "HAS_DEEPREAD", rel)

        for a in meta.get("authors", []):
            aid = f"author:{slug(a)}"
            add_node(G, aid, a, "concept", rel, 1)
            add_edge(G, aid, paper_id, "AUTHORED", rel)

        text = report + "\n" + json.dumps(meta, ensure_ascii=False)
        for topic in match_terms(text, TOPIC_KEYWORDS):
            tid = add_topic_or_method(G, topic, 2, rel)
            add_edge(G, paper_id, tid, "RELATED_TO_TOPIC", rel, "INFERRED")
        for method in match_terms(text, METHOD_KEYWORDS):
            mid = add_topic_or_method(G, method, 3, rel)
            add_edge(G, paper_id, mid, "USES_OR_DISCUSS_METHOD", rel, "INFERRED")

        for i, finding in enumerate(meta.get("key_findings", [])[:5], 1):
            cid = f"claim:{slug(title)}:{i}"
            add_node(G, cid, finding[:110], "concept", rel, 4, detail=finding)
            add_edge(G, paper_id, cid, "CLAIMS", rel)

        for i, s in enumerate(sentences(extract_section(report, 5), 4), 1):
            cid = f"contribution:{slug(title)}:{i}"
            add_node(G, cid, s[:110], "concept", rel, 4, detail=s)
            add_edge(G, paper_id, cid, "CONTRIBUTES", rel, "INFERRED")

        for i, s in enumerate(sentences(extract_section(report, 6), 5), 1):
            lid = f"limitation:{slug(title)}:{i}"
            add_node(G, lid, s[:110], "concept", rel, 5, detail=s)
            add_edge(G, paper_id, lid, "LIMITED_BY", rel, "INFERRED")

    # Standalone deepread markdown files
    for p in sorted(CORPUS.glob("deepread/*.md")):
        rel = p.relative_to(CORPUS).as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        title = p.stem.replace("-", " ")
        pid = f"paper_note:{slug(title)}"
        add_node(G, pid, title, "paper", rel, 0, summary=text[:500])
        add_edge(G, "project:dailyread", pid, "HAS_DEEPREAD", rel)
        for topic in match_terms(text, TOPIC_KEYWORDS):
            add_edge(G, pid, add_topic_or_method(G, topic, 2, rel), "RELATED_TO_TOPIC", rel, "INFERRED")
        for method in match_terms(text, METHOD_KEYWORDS):
            add_edge(G, pid, add_topic_or_method(G, method, 3, rel), "USES_OR_DISCUSS_METHOD", rel, "INFERRED")

    # Topic/domain notes as domain-knowledge anchors
    for p in sorted((CORPUS / "topics").glob("**/*.md")):
        rel = p.relative_to(CORPUS).as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        folder = p.parent.name.replace("-", " ").title()
        note_id = f"domain_note:{slug(p.parent.name + '_' + p.stem)}"
        add_node(G, note_id, f"{folder}: {p.stem}", "document", rel, 6, summary=text[:500])
        add_edge(G, "corpus:graphify_paper_kg", note_id, "CONTAINS_DOMAIN_NOTE", rel)
        for topic in match_terms(text + " " + folder, TOPIC_KEYWORDS):
            add_edge(G, note_id, add_topic_or_method(G, topic, 2, rel), "DOCUMENTS_TOPIC", rel, "INFERRED")
        for method in match_terms(text, METHOD_KEYWORDS):
            add_edge(G, note_id, add_topic_or_method(G, method, 3, rel), "DOCUMENTS_METHOD", rel, "INFERRED")

    return G


def write_report(G: nx.Graph):
    OUT.mkdir(parents=True, exist_ok=True)
    degree = sorted(G.degree, key=lambda x: x[1], reverse=True)[:12]
    papers = [n for n, d in G.nodes(data=True) if d.get("file_type") == "paper"]
    topics = [n for n, d in G.nodes(data=True) if d.get("community") == 2]
    methods = [n for n, d in G.nodes(data=True) if d.get("community") == 3]
    lines = [
        "# GRAPH_REPORT — DailyRead Paper Knowledge Graph",
        "",
        "這是針對 DailyRead paper / domain knowledge 建立的 Graphify-compatible knowledge graph。",
        "目前刻意不匯入個人記憶、郵件、行事曆或帳號資訊。",
        "",
        "## Scope",
        "- DeepRead reports and metadata",
        "- DailyRead domain/topic notes",
        "- Paper-related domain knowledge only",
        "",
        "## Stats",
        f"- Nodes: {G.number_of_nodes()}",
        f"- Edges: {G.number_of_edges()}",
        f"- Papers / paper notes: {len(papers)}",
        f"- Research topics: {len(topics)}",
        f"- Methods / systems: {len(methods)}",
        "",
        "## Most connected nodes",
    ]
    for nid, deg in degree:
        lines.append(f"- `{G.nodes[nid].get('label', nid)}` — degree {deg}")
    lines += [
        "",
        "## Suggested queries",
        "- `graphify query \"social simulation design space\" --graph graphify-paper-kg/graphify-out/graph.json`",
        "- `graphify query \"agent memory knowledge graph\" --graph graphify-paper-kg/graphify-out/graph.json`",
        "- `graphify path \"paper:2603.00113\" \"topic:llm_based_social_simulation\" --graph graphify-paper-kg/graphify-out/graph.json`",
        "- `graphify explain \"topic:llm_based_social_simulation\" --graph graphify-paper-kg/graphify-out/graph.json`",
        "",
        "## Schema sketch",
        "- Paper / paper_note → RELATED_TO_TOPIC → ResearchTopic",
        "- Paper → USES_OR_DISCUSS_METHOD → Method/System",
        "- Paper → CLAIMS / CONTRIBUTES / LIMITED_BY → Claim or Limitation nodes",
        "- Domain note → DOCUMENTS_TOPIC / DOCUMENTS_METHOD → Topic or Method nodes",
    ]
    (OUT / "GRAPH_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    G = build()
    communities: dict[int, list[str]] = {cid: [] for cid in COMMUNITIES}
    for nid, data in G.nodes(data=True):
        communities.setdefault(int(data.get("community", 6)), []).append(nid)
    to_json(G, communities, str(OUT / "graph.json"), force=True)
    to_html(G, communities, str(OUT / "graph.html"), community_labels=COMMUNITIES)
    write_report(G)
    print(f"Wrote {OUT / 'graph.json'}")
    print(f"Nodes={G.number_of_nodes()} Edges={G.number_of_edges()}")


if __name__ == "__main__":
    main()
