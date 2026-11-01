# PJCIS submission guide (superseded)

Superseded: the paper now targets Computer Speech & Language. See [JOURNAL_SUBMISSION_GUIDE.md](JOURNAL_SUBMISSION_GUIDE.md). The `paper/manuscript_pjcis.*` files are no longer built and can be deleted.

This guide is for submitting the finalized manuscript to the Pakistan Journal
of Computer and Information Systems (PJCIS), published by PASTIC.

Official pages:

- Journal: <https://www.pastic.gov.pk/pjcis.aspx>
- Author guidelines: <https://www.pastic.gov.pk/pjcis-authorguidelines.aspx?cmenu=pjcisauthor&par=pjcis>
- Call for papers: <https://pastic.gov.pk/pjcis-callforpapers.aspx?cmenu=pjciscall&par=pjcis>

PJCIS describes itself as a peer-reviewed, open-access computer science and
information-systems journal. Its call states that submissions and processing
are free, and that it accepts authors from academia, research institutions,
government, and industry. Confirm current HEC recognition and category in
HJRS before relying on the publication for a degree requirement.

## 1. Prepare the files

Use these files from this repository:

- `paper/manuscript_pjcis.pdf` — condensed submission PDF
- `paper/manuscript_pjcis.tex` — LaTeX source, if requested
- `paper/manuscript_pjcis.md` — readable source copy
- `CITATION.md` — citation and attribution information
- `PUBLIC_RELEASE.md` — public artifact and data restrictions

Do not attach or upload:

- QuickComm recordings or transcripts;
- Full-Duplex-Bench source audio;
- Azure/SAS URLs, database exports, API keys, `.env` files, or private logs;
- temporary files such as `texput.log`;
- unrelated application or product repositories.

## 2. Format the manuscript

PJCIS author guidance specifies English manuscripts in Word or LaTeX, with
Times New Roman, double spacing, and at least 1-inch margins. The stated paper
length limit is up to 12 pages. Before submission:

1. Check the final PDF page count.
2. Apply the PJCIS template or formatting instructions if the editor provides
   a newer version.
3. Keep the following order where possible:
   abstract, keywords, introduction, methods, results, discussion,
   conclusion, recommendations, acknowledgements, and references.
4. Ensure tables, references, URLs, and the ORCID are readable.
5. Remove any “draft,” “not submitted,” or temporary-build wording.

The current paper is a reference-model and diagnostic study. Keep its scope
accurate: it does not claim production voice-agent reliability or ground-truth
cancellation labels from the public speech benchmark.

## 3. Check authorship and disclosure

The listed author should be reviewed and approved by the human author before
submission. Keep the manuscript's AI-assistance disclosure accurate. The AI
assistant is not listed as a co-author and must not be presented as a human
author or independent scientific reviewer.

The author block should include:

- Qalab Hassnain Agha;
- Independent Researcher, Islamabad, Pakistan;
- ORCID: `0009-0006-6242-2761`;
- active email address;
- public repository URL: <https://github.com/qalab-e-hassnain/cancelbench>.

## 4. Run the final local checks

From the repository root:

```sh
python3 scripts/build_paper.py --pjcis
cd paper
pdflatex -interaction=nonstopmode manuscript_pjcis.tex
pdflatex -interaction=nonstopmode manuscript_pjcis.tex
cd ..
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Then visually inspect every page of `paper/manuscript_pjcis.pdf`. Confirm that no `.env`, key, raw audio,
private transcript, SAS URL, or temporary log is included in the submission
package.

## 5. Prepare the email submission

The PJCIS page contains an apparent typo in the `journals.org.pk` address;
your delivery failure confirms that domain is not resolving. Use the working
contact listed on the same official page:

- `editor.pjcis@gmail.com`
- `info.pjcis@journal.org.pk`

Use a clear subject line:

```text
Manuscript submission: Wait, Cancel That: Release Monotonicity and Cancellation Semantics
```

Suggested email:

```text
Dear PJCIS Editorial Office,

Please consider the attached manuscript for publication in the Pakistan Journal
of Computer and Information Systems.

Title: “Wait, Cancel That”: Release Monotonicity and Cancellation Semantics
for Streaming Voice-Agent Actions
Author: Qalab Hassnain Agha
ORCID: 0009-0006-6242-2761
Affiliation: Independent Researcher, Islamabad, Pakistan

The manuscript proves that, under atomic version fencing, releasing a voice
agent's effects later never adds a committed or notified version, and that
holding irreversible effects until the system's own end-of-turn decision costs
no acknowledgement latency. The results are verified exhaustively in a
reproducible discrete-event model with oracle intent events; the study does not
claim production voice-agent or human-subject performance.

The manuscript is original, is not under review elsewhere, and contains no
private QuickComm recordings, transcripts, credentials, or restricted source
audio. The code and aggregate artifacts are available at:
https://github.com/qalab-e-hassnain/cancelbench

I confirm that I am the author and approve this submission. Please let me know
if PJCIS requires a specific template, declaration, cover sheet, or additional
files.

Sincerely,
Qalab Hassnain Agha
Independent Researcher
ORCID: 0009-0006-6242-2761
Email: qagha.hassnain39@ce.ceme.edu.pk
```

Attach only the final PDF unless the editor requests the source files. Do not
send the entire repository archive by email.

## 6. Submission declarations

Before sending, verify each statement below:

- The manuscript is not simultaneously submitted elsewhere.
- The title and author list are final.
- The author has approved the AI-assistance disclosure.
- All references and dataset licenses are acknowledged.
- No private or confidential data is included.
- The public repository contains only relevant research artifacts.
- The PDF opens correctly and matches the final source.
- The email address is monitored for editorial responses.

## 7. After submission

Keep the sent email, attached PDF, date, and any manuscript ID. Do not revise
the submitted PDF silently. For revisions, preserve the original submission
copy and record changes in a response-to-reviewers document.

PJCIS's current instructions and HEC status can change. Follow the journal's
latest website instructions if they differ from this guide.

