# Journal submission guide

## Target

**Primary: Computer Speech & Language** (Elsevier, official journal of ISCA). Its scope names spoken language dialogue systems, speech-based interaction and the evaluation of speech-based interactive systems. The paper's central quantity is the system's endpoint decision, a turn-taking concept, and it cites the turn-taking review published in this journal [14].

Main risk: the journal states that new manuscripts must address some aspect of spoken language processing and no longer takes pure NLP. The paper uses oracle intent events and no audio, so the cover letter argues scope explicitly (release point defined by endpointing, phenomenon is spoken self-repair, contribution is to evaluating speech-based interactive systems). Expect a reviewer to ask for speech data; the Limitations section already answers this.

**Backup: Dialogue & Discourse** (free, open access, Scopus-indexed). The closest formal precedent the paper builds on, Schlangen and Skantze's abstract model of incremental dialogue processing [8], appeared there. Resubmitting needs only its template; the content is ready.

Do not submit to both at once. Both prohibit simultaneous submission.

## Before submitting

1. Read the current Computer Speech & Language guide for authors on elsevier.com and confirm abstract length, highlights rules and the exact wording required for the generative AI declaration. This guide was prepared without access to that page.
2. Work through every proof in Section 4.3 yourself. The AI declaration states that you reviewed the content and take full responsibility.
3. Check references 11 to 18 against the original papers (they were added without DOIs) and add DOIs where available.
4. Tag a release of the repository and archive it on Zenodo, then replace the GitHub URL in the Data Availability section with the DOI.
5. Optional but useful for PhD applications: post the paper to arXiv (cs.CL, cross-list cs.DC). Elsevier permits preprints; mention the arXiv ID in the cover letter.

## How to submit

1. Open the journal's page on elsevier.com (search "Computer Speech & Language Elsevier") and use its **Submit your article** button. An older third-party copy of the guide lists Editorial Manager at editorialmanager.com/ycsla; trust the button on the official page over that link.
2. Create or sign in to an Elsevier account with qalab@quickgentech.com and link ORCID 0009-0006-6242-2761.
3. In the guide for authors, check whether review is single or double anonymized. If double, upload an anonymized copy: remove the author block, the Quickgen declarations and the GitHub link (write "repository link withheld for review"), and keep the named version for after acceptance.
4. Article type: research article. Enter the title, abstract, keywords and the five highlights from `paper/highlights_csl.txt`.
5. Upload the PDF, the highlights file and the cover letter, then answer the declaration questions (competing interests, funding, data, generative AI) with the same text as the manuscript.
6. Choose subscription publication unless you want to pay for open access; submission itself is free. Typical first decision takes about three months.
7. After submitting, record the manuscript number in this repository and do not submit elsewhere until a decision arrives.

## Build and files

```sh
PYTHONPATH=src python3 -m cancelbench.run --output results
python3 scripts/build_paper.py --journal
cd paper && pdflatex manuscript_csl.tex && pdflatex manuscript_csl.tex
```

Upload:

- `paper/manuscript_csl.pdf` (review format: double spaced, line numbers) and `paper/manuscript_csl.tex` if source is requested
- `paper/highlights_csl.txt` as the separate highlights file
- the cover letter below
- the repository link or Zenodo DOI as the data and code statement

Account details: Qalab Hassnain Agha, Quickgen Technologies (SMC-Private) Limited, Islamabad, Pakistan; qalab@quickgentech.com; ORCID 0009-0006-6242-2761.

Suggested reviewers, if requested: choose three to five researchers who work on turn-taking, incremental dialogue processing or voice-agent tool use, drawn from the authors of cited work, with whom you have never collaborated. Take their current addresses from their institutional pages.

## Cover letter

```text
Dear Editors,

Please consider the enclosed manuscript, "Wait, Cancel That": Release
Monotonicity and Cancellation Semantics for Streaming Voice-Agent Actions,
for publication in Computer Speech & Language.

Spoken dialogue systems increasingly begin tool work before the user has
finished speaking, while users routinely revise an instruction mid-utterance.
The manuscript asks when such a system may release an effect that cannot be
recalled, such as a dispatch notification. It proves that, under version
fencing, releasing effects later never adds a committed or notified version,
and that holding irreversible effects until the system's own endpoint
decision costs no acknowledgement latency and is optimal among causal
policies that add none. A gate that holds only irreversible effects weakly
dominates eager execution. In short, the endpoint decision is the zero-cost
commit point for spoken intent.

We believe the work fits the journal's scope on spoken dialogue systems and
the evaluation of speech-based interactive systems. The release point is
defined by endpointing, the motivating phenomenon is spoken self-repair, and
the results show that evaluating a voice agent by its final backend state
cannot reveal whether a spoken cancellation prevented an effect. The study
deliberately isolates execution semantics with oracle intent events and
states plainly that it does not evaluate recognition.

Every result is checked exhaustively against an open, reproducible artifact:
12,348 simulated runs with event traces, an independent rescoring program and
paired per-scenario checks of the theorems.

The manuscript is original and is not under consideration elsewhere. The
author declares no competing interests; the work was carried out independently,
received no funding, and used no company data. The use of an AI coding assistant is declared in line
with Elsevier policy.

Sincerely,
Qalab Hassnain Agha
Quickgen Technologies (SMC-Private) Limited, Islamabad, Pakistan
qalab@quickgentech.com
ORCID: 0009-0006-6242-2761
```
