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
    text = text.translate(str.maketrans({"“": "``", "”": "''", "’": "'", "–": "--", "—": "---", "×": "x"}))
    chars = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
             "#": r"\#", "_": r"\_\allowbreak{}", "{": r"\{", "}": r"\}",
             "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(chars.get(c, c) for c in text)


def inline(text, fmt):
    tokens = re.split(r"(\[[^\]]+\]\(https?://[^)]+\)|`[^`]+`|\*\*[^*]+\*\*|https?://[^\s)]*[^\s).,;])", text)
    rendered = []
    esc = html.escape if fmt == "html" else latex_escape
    for token in tokens:
        link = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)]+)\)", token)
        if link:
            label, url = link.groups()
            rendered.append(f'<a href="{html.escape(url, quote=True)}">{esc(label)}</a>' if fmt == "html"
                            else r"\href{" + url + "}{" + esc(label) + "}")
        elif re.fullmatch(r"https?://\S+", token):
            rendered.append(f'<a href="{html.escape(token, quote=True)}">{html.escape(token)}</a>' if fmt == "html"
                            else r"\url{" + token + "}")
        elif token.startswith("`") and token.endswith("`"):
            rendered.append("<code>" + esc(token[1:-1]) + "</code>" if fmt == "html"
                            else r"\texttt{" + esc(token[1:-1]) + "}")
        elif token.startswith("**") and token.endswith("**"):
            rendered.append("<strong>" + esc(token[2:-2]) + "</strong>" if fmt == "html"
                            else r"\textbf{" + esc(token[2:-2]) + "}")
        else:
            rendered.append(esc(token))
    return "".join(rendered)


AUTHOR = "Qalab Hassnain Agha"
ROLE = "Co-Founder and Chief Technology Officer"
ORG = "Quickgen Technologies (SMC-Private) Limited"
ADDRESS = "National Science and Technology Park, NUST H-12 Campus"
CITY, COUNTRY = "Islamabad", "Pakistan"
EMAIL = "qalab@quickgentech.com"
ORCID = "0009-0006-6242-2761"
DATE = "1 November 2026"
JOURNAL = "Computer Speech & Language"


def blocks(md, fmt):
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
                out.append(r"\title{" + latex_escape(title) + "}\n\\author{" + AUTHOR + r"\\" + latex_escape(ROLE)
                           + r"\\" + latex_escape(ORG) + r"\\" + latex_escape(f"{ADDRESS}, {CITY}, {COUNTRY}")
                           + r"\\" + EMAIL + r"\\ORCID: " + ORCID + "}\n\\date{" + DATE + "}\n\\maketitle")
            else:
                command = "section*" if level == 2 else "subsection*"
                out.append("\\" + command + "{" + inline(title, fmt) + "}")
            i += 1
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(inline(lines[i][2:], fmt))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>" if fmt == "html"
                       else "\\begin{itemize}\n" + "\n".join(r"\item " + x for x in items) + "\n\\end{itemize}")
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
                out.append("{\\scriptsize\n\\begin{tabularx}{\\textwidth}{" + r">{\raggedright\arraybackslash}X" * len(rows[0]) + "}\n\\hline\n" + body + "\n\\hline\n\\end{tabularx}\n}\n")
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", "| ", "- ")):
            paragraph.append(lines[i])
            i += 1
        text = " ".join(paragraph)
        out.append("<p>" + inline(text, fmt) + "</p>" if fmt == "html" else inline(text, fmt) + "\n")
    return "\n\n".join(out)


PACKAGES = r"""\usepackage[T1]{fontenc}
\usepackage{xurl}
\usepackage{setspace}
\usepackage{hyperref}
\usepackage{tabularx}
\usepackage{listings}
\lstset{basicstyle=\ttfamily\footnotesize,breaklines=true,columns=fullflexible}
\hypersetup{colorlinks=true,urlcolor=blue}
\setlength{\parindent}{0pt}
"""


def render(md, fmt):
    body = blocks(md, fmt)
    if fmt == "html":
        return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wait, Cancel That: author-reviewed manuscript</title><style>
body{max-width:920px;margin:50px auto;padding:0 24px;font:17px/1.65 Georgia,serif;color:#17202a}h1{line-height:1.2}h2{margin-top:2em}h3{margin-top:1.7em}a{color:#175d8d}table{border-collapse:collapse;width:100%;font:13px/1.5 system-ui}th,td{border-bottom:1px solid #ccd1d1;padding:9px;text-align:left}thead{background:#edf2f7}.table{overflow-x:auto}pre{background:#f2f4f4;padding:18px;overflow:auto;font:12px/1.6 monospace}p{overflow-wrap:anywhere}@media print{body{max-width:none;margin:0;font-size:10pt}h2,h3{break-after:avoid}table,pre{break-inside:avoid}a{color:inherit}}
</style><main>""" + body + "</main></html>\n"
    # The Markdown source keeps a readable author block, while LaTeX places
    # that metadata in the formal title block above. Avoid duplicating it.
    body = re.sub(r"(?s)(\\maketitle).*?(\\section\*\{Abstract\})", r"\1\n\n\2", body, count=1)
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{mathptmx}
""" + PACKAGES + r"""\setlength{\parskip}{0.6em}
\doublespacing
\begin{document}
""" + body + "\n\\end{document}\n"


def section(md, name):
    match = re.search(r"^## " + re.escape(name) + r"\s*$(.*?)(?=^## )", md, re.M | re.S)
    if not match:
        raise ValueError(f"Missing section: {name}")
    return match[1].strip()


def render_journal(md):
    """Elsevier elsarticle review format: front matter, highlights, line numbers."""
    title = re.search(r"^# (.*)$", md, re.M)[1]
    highlights = re.findall(r"^- (.*)$", section(md, "Highlights"), re.M)
    if not 3 <= len(highlights) <= 5 or any(len(h) > 85 for h in highlights):
        raise ValueError("Highlights must be 3 to 5 bullets of at most 85 characters")
    abstract, keywords = section(md, "Abstract").split("**Keywords:**")
    if len(abstract.split()) > 250:
        raise ValueError("Abstract exceeds 250 words")
    keywords = [k.strip().rstrip(".") for k in keywords.split(";")]
    body = blocks(md[md.index("## 1. Introduction"):], "latex")
    return r"""\documentclass[review,12pt]{elsarticle}
\usepackage{lineno}
""" + PACKAGES + r"""\journal{""" + latex_escape(JOURNAL) + r"""}
\begin{document}
\begin{frontmatter}
\title{""" + latex_escape(title) + r"""}
\author[qg]{""" + AUTHOR + r"""\corref{cor}\fnref{role}}
\ead{""" + EMAIL + r"""}
\cortext[cor]{Corresponding author.}
\fntext[role]{""" + latex_escape(ROLE) + ". ORCID: " + ORCID + r""".}
\affiliation[qg]{organization={""" + latex_escape(ORG) + r"""},
  addressline={""" + latex_escape(ADDRESS) + r"""}, city={""" + CITY + r"""}, country={""" + COUNTRY + r"""}}
\begin{abstract}
""" + inline(" ".join(abstract.split()), "latex") + r"""
\end{abstract}
\begin{highlights}
""" + "\n".join(r"\item " + inline(h, "latex") for h in highlights) + r"""
\end{highlights}
\begin{keyword}
""" + r" \sep ".join(latex_escape(k) for k in keywords) + r"""
\end{keyword}
\end{frontmatter}
\linenumbers
\sloppy
""" + body + "\n\\end{document}\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    parser.add_argument("--output", type=Path, default=ROOT / "paper")
    parser.add_argument("--journal", action="store_true", help="build the Elsevier journal submission source")
    args = parser.parse_args()
    summary = json.loads((args.results / "summary.json").read_text())
    manifest = json.loads((args.results / "manifest.json").read_text())
    sensitivity = json.loads((args.results / "sensitivity.json").read_text())
    mono = json.loads((args.results / "monotonicity.json").read_text())
    names = list(summary)
    primary = table(["Policy", "Final correct", "Known-stale commit", "World-stale commit", "Superseded notification*", "Stable latency (ms)"], [
        [n, f"{summary[n]['final_correct_rate']:.2%}", f"{summary[n]['stale_known_commit_rate']:.2%}",
         f"{summary[n]['stale_world_commit_rate']:.2%}", f"{summary[n]['changed_superseded_notification_rate']:.2%}",
         f"{summary[n]['stable_mean_settlement_ms']:.1f}"] for n in names])
    primary += "\n\nEach policy: 1,764 runs. *Changed-scenario denominator: 1,512 per policy. Stable latency: 36 stable scenarios per policy."
    cancellation = table(["Policy", "Cancellation scenarios", "No database commit", "No notification emitted", "Final empty database"], [
        [n, summary[n]["cancel_runs"], f"{summary[n]['cancel_prevented_rate']:.2%}",
         f"{summary[n]['cancel_notice_prevented_rate']:.2%}",
         f"{summary[n]['cancel_final_correct_rate']:.2%}"] for n in names])
    delay_rows = []
    for n in ("wait", "eager", "guarded_0", "guarded_200", "guarded_500", "release_gate"):
        rates = []
        for delay in (0, 100, 350):
            group = [r for r in sensitivity if r["policy"] == n and r["delivery_ms"] == delay]
            rate = sum(r["stale_world_commit_rate"] * r["runs"] for r in group) / sum(r["runs"] for r in group)
            rates.append(f"{rate:.2%}")
        delay_rows.append([n, *rates])
    delays = table(["Policy", "d = 0 ms", "d = 100 ms", "d = 350 ms"], delay_rows)
    delays += "\n\nWorld-stale commit incidence among changed scenarios: 504 per policy and delivery-delay setting."
    pairs = mono["ordered_pairs"]
    monotone = table(["Earlier release", "Later release", "Notified-set violations", "Commit-set violations", "Prevention lost", "Fewer superseded notifications", "World-stale commit added"], [
        [r["earlier"], r["later"], r["notice_violation"], r["commit_violation"], r["prevention_worse"],
         r["fewer_superseded"], r["world_stale_worse"]] for r in pairs])
    monotone += f"\n\nEach row: {pairs[0]['scenarios']:,} paired scenarios. Violation and loss columns count scenarios that contradict Theorem 1; the last two columns count scenarios."
    sweep = table(["Earlier release", "Later release", "Notified-set violations", "Commit-set violations", "Fewer superseded notifications"], [
        [r["earlier"], r["later"], r["notice_violation"], r["commit_violation"], r["fewer_superseded"]]
        for r in mono["endpoint_sweep"]])
    sweep += f"\n\ngate@x commits at max(r + P, x). Each row: {mono['endpoint_sweep'][0]['scenarios']:,} paired scenarios."
    strata = mono["strata"]
    within = table(["Policy", "Correction during turn", "Correction after turn"], [
        [n, f"{strata[n]['within_turn']['superseded_notification_rate']:.2%}",
         f"{strata[n]['after_turn']['superseded_notification_rate']:.2%}"] for n in names if n != "guarded_no_fence"])
    within += f"\n\nSuperseded-notification incidence. Denominators: {strata['eager']['within_turn']['runs']} changed scenarios with first change before E and {strata['eager']['after_turn']['runs']} at or after E, per policy."
    unordered = mono["unordered_pairs"][0]
    rate = lambda n, key: f"{summary[n][key]:.2%}"
    srate = lambda n, part: f"{strata[n][part]['superseded_notification_rate']:.2%}"
    values = {
        "SCENARIOS": f"{manifest['scenario_count']:,}", "RUNS": f"{manifest['run_count']:,}",
        "EAGER_NOTICE": f"{summary['eager']['changed_superseded_notification_rate']:.2%}",
        "GUARD_NOTICE": f"{summary['guarded_0']['changed_superseded_notification_rate']:.2%}",
        "GUARD_STABLE": f"{summary['guarded_0']['stable_mean_settlement_ms']:.1f}",
        "WAIT_STABLE": f"{summary['wait']['stable_mean_settlement_ms']:.1f}",
        "ABLATION_CORRECT": f"{summary['guarded_no_fence']['final_correct_rate']:.2%}",
        "PRIMARY_TABLE": primary, "CANCEL_TABLE": cancellation, "DELAY_TABLE": delays,
        "MONO_TABLE": monotone, "SWEEP_TABLE": sweep, "STRATA_TABLE": within,
        "PAIRED": f"{pairs[0]['scenarios']:,}",
        "CLOSED_FORM": f"{mono['closed_form']['matched']:,} of {mono['closed_form']['checked']:,}",
        "RELEASE_EQUIV": f"{mono['release_gate_equals_guarded_0_notices']:,}",
        "STRICT_EG": str(pairs[0]["fewer_superseded"]), "WS_WORSE_EG": str(pairs[0]["world_stale_worse"]),
        "UNORDERED_FIRST": str(unordered["fewer_superseded"]), "UNORDERED_SECOND": str(unordered["more_superseded"]),
        "EAGER_WITHIN": srate("eager", "within_turn"), "GUARD_WITHIN": srate("guarded_0", "within_turn"),
        "EAGER_AFTER": srate("eager", "after_turn"), "GUARD_AFTER": srate("guarded_0", "after_turn"),
        "G500_AFTER": srate("guarded_500", "after_turn"),
        "G500_NOTICE": rate("guarded_500", "changed_superseded_notification_rate"),
        "SWEEP_VIOLATIONS": str(sum(r["notice_violation"] + r["commit_violation"] for r in mono["endpoint_sweep"])),
        "SWEEP_STRICT": ", ".join(str(r["fewer_superseded"]) for r in mono["endpoint_sweep"][:-1])
                        + " and " + str(mono["endpoint_sweep"][-1]["fewer_superseded"]),
        "EAGER_PREVENT": rate("eager", "cancel_prevented_rate"),
        "RELEASE_NOTICE_PREVENT": rate("release_gate", "cancel_notice_prevented_rate"),
        "GUARD_NOTICE_PREVENT": rate("guarded_0", "cancel_notice_prevented_rate"),
    }
    md = (ROOT / "paper/manuscript.template.md").read_text()
    for key, value in values.items():
        md = md.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", md):
        raise ValueError("Unresolved manuscript placeholder")
    args.output.mkdir(parents=True, exist_ok=True)
    if args.journal:
        (args.output / "manuscript_csl.tex").write_text(render_journal(md))
        highlights = re.findall(r"^- (.*)$", section(md, "Highlights"), re.M)
        (args.output / "highlights_csl.txt").write_text("\n".join(highlights) + "\n")
        print(f"Built Elsevier journal LaTeX in {args.output} (manuscript_csl)")
        return
    (args.output / "manuscript.md").write_text(md)
    (args.output / "manuscript.html").write_text(render(md, "html"))
    (args.output / "manuscript.tex").write_text(render(md, "latex"))
    print(f"Built Markdown, HTML and LaTeX manuscript in {args.output} (manuscript)")


if __name__ == "__main__":
    main()
