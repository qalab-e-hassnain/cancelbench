# Submission guide (conference fallback)

The primary target is now a journal; see [JOURNAL_SUBMISSION_GUIDE.md](JOURNAL_SUBMISSION_GUIDE.md). This guide covers the conference route as a fallback.

This repository contains the manuscript source, HTML version, LaTeX source, results, tests, and reproducibility artifacts. The repository does not currently contain a PDF because this environment has no TeX or HTML-to-PDF engine. Do not submit the Markdown or HTML file as the final conference manuscript.

## 1. Review the public repository

Open https://github.com/qalab-e-hassnain/cancelbench and verify that no private files, API keys, recordings, or business code are present. The public repository is the artifact URL to use in the paper after the venue permits it.

From the repository root, run:

```sh
python3 scripts/verify.py
python3 scripts/runtime_races.py
python3 scripts/compare_policies.py
git diff --check
```

Do not change results, timing values, or claims after this check without rerunning the verification suite.

## 2. Compile the PDF locally on macOS

Install MacTeX from https://www.tug.org/mactex/ or install a smaller TeX distribution that provides `pdflatex`, `lmodern`, `listings`, `tabularx`, and `hyperref`. Open a new terminal after installation and check:

```sh
pdflatex --version
```

Build the manuscript from the repository root:

```sh
python3 scripts/build_paper.py
cd paper
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex
```

The final file is `paper/manuscript.pdf`. Open it and inspect every page. Check that tables fit, references are readable, the author block contains the ORCID, no URLs are clipped, and the manuscript does not contain draft-only wording that the venue disallows.

## 3. Compile without installing TeX

Use Overleaf:

1. Create a new blank project.
2. Upload `paper/manuscript.tex`.
3. Upload any required source assets; this manuscript currently has no image assets.
4. Select `pdfLaTeX` as the compiler.
5. Compile twice.
6. Download the generated PDF as `manuscript.pdf`.
7. Compare the PDF visually with `paper/manuscript.html`.

Do not upload `.env` files, provider keys, private business repositories, or human speech recordings.

## 4. Add the PDF to the public repository

After inspecting the downloaded file, copy it to `paper/manuscript.pdf` and check it:

```sh
file paper/manuscript.pdf
pdfinfo paper/manuscript.pdf
```

The PDF should be a non-empty PDF document with the venue's page limit. Then run:

```sh
git add paper/manuscript.pdf
git commit -m "Add inspected manuscript PDF"
git push
```

The PDF must not contain an API key, private URL, or unreviewed experimental claim.

## 5. Submit to the recommended venues

### ACM CUI 2027

Monitor https://cui.acm.org/2027/ for the call and submission system. This is the closest topical fit. When the call opens:

1. Read the exact page limit and select the short-paper or work-in-progress track if available.
2. Create the author account using `support@qalabagha.com`.
3. Enter Qalab Hassnain Agha as the sole author.
4. Add ORCID `0009-0006-6242-2761`.
5. Use `Quickgen Technologies (SMC-Private) Limited, Islamabad, Pakistan` as affiliation and `qalab@quickgentech.com` as contact email.
6. Upload the venue-formatted PDF and any required supplementary artifact link.
7. Disclose AI assistance according to the venue's current policy.
8. Confirm whether registration is required after acceptance; submission being free does not mean conference attendance is free.

### ACL 2027

Read https://2027.aclweb.org/calls/main/ and the linked ARR instructions. The currently listed ARR deadline is January 4, 2027. Before submitting:

1. Convert the manuscript to the ACL template and obey its page limit.
2. Prepare an anonymized PDF if required; remove author names, ORCID, email, repository URL, and self-identifying acknowledgments from the review copy.
3. Submit through the January ARR cycle.
4. Do not submit the same paper simultaneously to CUI or another reviewing venue.
5. If reviewed by ARR, follow the later ACL commitment process.

ACL and CUI submission policies can change. Follow the official call, not this local checklist, when the submission form opens.

### arXiv

Use arXiv only after human review and after checking the selected conference's dual-submission rules. Upload the final PDF and source, select the most accurate category, and label the work as a preprint. arXiv moderation or endorsement is not peer review.

## 6. What must happen before submission

- The author reads and approves every claim, proof, result, reference, and AI-assistance statement.
- A researcher or engineer independently reviews the code and manuscript.
- The paper clearly says that the main experiment uses oracle intent and no real speech.
- The public artifact and PDF contain no secrets or private data.
- The PDF is visually inspected and complies with the chosen venue's template and page limit.
- The author keeps a copy of the submitted PDF and records the submission ID.
