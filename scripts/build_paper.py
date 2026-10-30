"""Build measured tables and standalone manuscript formats; no dependencies."""

import argparse
import html
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(map(str, row)) + " |" for row in rows)])


def latex_escape(text):
    text = text.translate(str.maketrans({"“": '"', "”": '"', "’": "'", "–": "--", "—": "---", "×": "x"}))
    chars = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
             "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
             "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(chars.get(c, c) for c in text)


def inline(text, fmt):
    tokens = re.split(r"(\[[^\]]+\]\(https?://[^)]+\)|`[^`]+`|\*\*[^*]+\*\*)", text)
    rendered = []
    esc = html.escape if fmt == "html" else latex_escape
    for token in tokens:
        link = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)]+)\)", token)
        if link:
            label, url = link.groups()
            rendered.append(f'<a href="{html.escape(url, quote=True)}">{esc(label)}</a>' if fmt == "html"
                            else r"\href{" + url + "}{" + esc(label) + "}")
        elif token.startswith("`") and token.endswith("`"):
            rendered.append("<code>" + esc(token[1:-1]) + "</code>" if fmt == "html"
                            else r"\texttt{" + esc(token[1:-1]) + "}")
        elif token.startswith("**") and token.endswith("**"):
            rendered.append("<strong>" + esc(token[2:-2]) + "</strong>" if fmt == "html"
                            else r"\textbf{" + esc(token[2:-2]) + "}")
        else:
            rendered.append(esc(token))
    return "".join(rendered)


def render(md, fmt, pjcis=False):
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            value = "\n".join(code)
            out.append("<pre><code>" + html.escape(value) + "</code></pre>" if fmt == "html"
                       else "\\begin{lstlisting}\n" + value + "\n\\end{lstlisting}")
            i += 1
            continue
        heading = re.match(r"^(#{1,3}) (.*)", line)
        if heading:
            level, title = len(heading[1]), heading[2]
            if fmt == "html":
                out.append(f"<h{level}>{inline(title, fmt)}</h{level}>")
            elif level == 1:
                out.append(r"\title{" + latex_escape(title) + "}\n\\author{Qalab Hassnain Agha\\\\Independent Researcher, Islamabad, Pakistan\\\\qagha.hassnain39@ce.ceme.edu.pk\\\\ORCID: 0009-0006-6242-2761}\n\\date{30 October 2026}\n\\maketitle")
            else:
                command = "section*" if level == 2 else "subsection*"
                out.append("\\" + command + "{" + inline(title, fmt) + "}")
            i += 1
            continue
        if line.startswith("| "):
            rows = []
            while i < len(lines) and lines[i].startswith("| "):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            if fmt == "html":
                head = "<tr>" + "".join("<th>" + inline(c, fmt) + "</th>" for c in rows[0]) + "</tr>"
                body = "".join("<tr>" + "".join("<td>" + inline(c, fmt) + "</td>" for c in row) + "</tr>" for row in rows[1:])
                out.append("<div class='table'><table><thead>" + head + "</thead><tbody>" + body + "</tbody></table></div>")
            else:
                body = "\n".join(" & ".join(inline(c, fmt) for c in row) + r" \\" for row in rows)
                out.append("{\\scriptsize\n\\begin{tabularx}{\\textwidth}{" + "X" * len(rows[0]) + "}\n\\hline\n" + body + "\n\\hline\n\\end{tabularx}\n}\n")
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", "| ")):
            paragraph.append(lines[i])
            i += 1
        text = " ".join(paragraph)
        out.append("<p>" + inline(text, fmt) + "</p>" if fmt == "html" else inline(text, fmt) + "\n")
    body = "\n\n".join(out)
    if fmt == "html":
        return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wait, Cancel That — final author-reviewed manuscript</title><style>
body{max-width:920px;margin:50px auto;padding:0 24px;font:17px/1.65 Georgia,serif;color:#17202a}h1{line-height:1.2}h2{margin-top:2em}h3{margin-top:1.7em}a{color:#175d8d}table{border-collapse:collapse;width:100%;font:13px/1.5 system-ui}th,td{border-bottom:1px solid #ccd1d1;padding:9px;text-align:left}thead{background:#edf2f7}.table{overflow-x:auto}pre{background:#f2f4f4;padding:18px;overflow:auto;font:12px/1.6 monospace}p{overflow-wrap:anywhere}@media print{body{max-width:none;margin:0;font-size:10pt}h2,h3{break-after:avoid}table,pre{break-inside:avoid}a{color:inherit}}
</style><main>""" + body + "</main></html>\n"
    # The Markdown source keeps a readable author block, while LaTeX places
    # that metadata in the formal title block above. Avoid duplicating it.
    body = re.sub(r"(?s)(\\maketitle).*?(\\section\*\{Abstract\})", r"\1\n\n\2", body, count=1)
    if pjcis:
        body = body.replace(r"\section*{References}", r"\begin{singlespace}\small\section*{References}", 1)
        body += "\n\\end{singlespace}\n"
    document_class = r"\documentclass[10pt]{article}" if pjcis else r"\documentclass[11pt]{article}"
    paragraph_spacing = r"\setlength{\parskip}{0pt}" if pjcis else r"\setlength{\parskip}{0.6em}"
    return document_class + r"""
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{mathptmx}
\usepackage{setspace}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage{listings}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,columns=fullflexible}
\hypersetup{colorlinks=true,urlcolor=blue}
""" + paragraph_spacing + r"""
\setlength{\parindent}{0pt}
\doublespacing
\begin{document}
""" + body + "\n\\end{document}\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    parser.add_argument("--output", type=Path, default=ROOT / "paper")
    parser.add_argument("--pjcis", action="store_true", help="build condensed PJCIS submission sources")
    args = parser.parse_args()
    summary = json.loads((args.results / "summary.json").read_text())
    manifest = json.loads((args.results / "manifest.json").read_text())
    sensitivity = json.loads((args.results / "sensitivity.json").read_text())
    names = list(summary)
    primary = table(["Policy", "Final correct", "Known-stale commit", "World-stale commit", "Superseded notification*", "Stable latency (ms)"], [
        [n, f"{summary[n]['final_correct_rate']:.2%}", f"{summary[n]['stale_known_commit_rate']:.2%}",
         f"{summary[n]['stale_world_commit_rate']:.2%}", f"{summary[n]['changed_superseded_notification_rate']:.2%}",
         f"{summary[n]['stable_mean_settlement_ms']:.1f}"] for n in names])
    primary += "\n\nEach policy: 1,764 runs. *Changed-scenario denominator: 1,512 per policy. Stable latency: 36 stable scenarios per policy."
    cancellation = table(["Policy", "Cancellation scenarios", "Prevented any commit", "Final empty database"], [
        [n, summary[n]["cancel_runs"], f"{summary[n]['cancel_prevented_rate']:.2%}",
         f"{summary[n]['cancel_final_correct_rate']:.2%}"] for n in names])
    delay_rows = []
    for n in ("wait", "eager", "guarded_0", "guarded_500"):
        rates = []
        for delay in (0, 100, 350):
            group = [r for r in sensitivity if r["policy"] == n and r["delivery_ms"] == delay]
            rate = sum(r["stale_world_commit_rate"] * r["runs"] for r in group) / sum(r["runs"] for r in group)
            rates.append(f"{rate:.2%}")
        delay_rows.append([n, *rates])
    delays = table(["Policy", "d = 0 ms", "d = 100 ms", "d = 350 ms"], delay_rows)
    delays += "\n\nWorld-stale commit incidence among changed scenarios: 504 per policy and delivery-delay setting."
    values = {
        "SCENARIOS": str(manifest["scenario_count"]), "RUNS": str(manifest["run_count"]),
        "EAGER_NOTICE": f"{summary['eager']['changed_superseded_notification_rate']:.2%}",
        "GUARD_NOTICE": f"{summary['guarded_0']['changed_superseded_notification_rate']:.2%}",
        "GUARD_STABLE": f"{summary['guarded_0']['stable_mean_settlement_ms']:.1f}",
        "WAIT_STABLE": f"{summary['wait']['stable_mean_settlement_ms']:.1f}",
        "ABLATION_CORRECT": f"{summary['guarded_no_fence']['final_correct_rate']:.2%}",
        "PRIMARY_TABLE": primary, "CANCEL_TABLE": cancellation, "DELAY_TABLE": delays,
    }
    md = (ROOT / "paper/manuscript.template.md").read_text()
    if args.pjcis:
        md = re.split(r"^## Appendix A\. Reproduction\s*$", md, maxsplit=1, flags=re.M)[0].rstrip() + "\n"
        # Keep the journal version focused on the empirical reference model;
        # the full formal propositions remain in manuscript.md and the repo.
        md = re.sub(
            r"### 4\.2 Received-version freshness.*?(?=## 5\. Experimental Design)",
            "### 4.2 Safety guarantees\\n\\nWith atomic version checks at the database and notification boundaries, a scheduled operation cannot commit or notify stale relative to the latest received intent. This does not protect against corrections that have not yet arrived. Under finite inputs, reliable delivery, finite preparation, successful compensation and fencing, the modeled database converges to the final target; convergence does not erase already emitted notifications.\\n\\n",
            md,
            flags=re.S,
        )
    for key, value in values.items():
        md = md.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", md):
        raise ValueError("Unresolved manuscript placeholder")
    args.output.mkdir(parents=True, exist_ok=True)
    stem = "manuscript_pjcis" if args.pjcis else "manuscript"
    (args.output / f"{stem}.md").write_text(md)
    (args.output / f"{stem}.html").write_text(render(md, "html", args.pjcis))
    (args.output / f"{stem}.tex").write_text(render(md, "latex", args.pjcis))
    print(f"Built Markdown, HTML and LaTeX manuscript in {args.output} ({stem})")


if __name__ == "__main__":
    main()
