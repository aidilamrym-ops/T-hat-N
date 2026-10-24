"""Visualization helpers for prime‑theory method diagram.
Exports:
- method_graph() -> str (Graphviz DOT description)
- render_diagram(output_path: str) -> None (write DOT file)
"""

def method_graph() -> str:
    """Return Graphviz DOT describing the analytic‑combinatorial‑probabilistic pipeline."""
    return """
    digraph PrimeBridge {
        rankdir=LR;
        node [shape=box, style=filled, color=lightgrey];
        AIInsight [label=\"AI‑Insight (OpenAI‑Kalim / Claude)\"];
        Analytic  [label=\"Analytic Core (Zeta‑free series)\"];
        Combinatorial [label=\"Combinatorial Core (Exact π(x))\"];
        Probabilistic [label=\"Probabilistic Layer (Cramér, Random‑matrix)\"];
        Computational [label=\"Computational Engine (Segmented sieve)\"];
        Geometry   [label=\"Geometric Interface (Penrose, Circle‑method)\"];
        AIInsight -> Analytic;
        AIInsight -> Combinatorial;
        Analytic -> Computational;
        Combinatorial -> Computational;
        Computational -> Probabilistic;
        Probabilistic -> Geometry;
    }
    """

def render_diagram(output_path: str) -> None:
    """Write DOT description to `output_path`. Caller can run `dot -Tpng` etc."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(method_graph())
