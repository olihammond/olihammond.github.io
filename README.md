# olihammond.github.io

Source for my personal site, <https://olihammond.github.io>. Built with the [al-folio](https://github.com/alshedivat/al-folio) Jekyll theme and deployed by GitHub Actions to GitHub Pages.

## Where things live

| To change...                 | Edit...                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| Front page text and photo    | `_pages/about.md`, `assets/img/prof_pic.jpg`                                           |
| CV                           | `_data/cv.yml`                                                                         |
| Publications                 | `_bibliography/papers.bib` (add `selected = {true}` to feature one on the front page)  |
| Job openings                 | `_data/openings.yml` (an empty list shows the "no positions" message)                  |
| Blog posts                   | add `_posts/YYYY-MM-DD-title.md` (copy `_drafts/post-template.md`)                     |
| News items on the front page | add a file to `_news/`                                                                 |
| Social links                 | `_data/socials.yml`                                                                    |
| Site name, colours, features | `_config.yml`                                                                          |

Every push to `main` rebuilds and publishes the site (see the **Actions** tab); it takes a few minutes. Files can be edited directly on github.com.

## Publications from ORCID

`.github/workflows/orcid-sync.yml` runs every Monday (or on demand from the Actions tab). It compares the public ORCID record with `papers.bib` and opens a pull request containing any missing works, with BibTeX fetched from doi.org. Existing entries are never touched. Review the new entries, add `†` / `*` markers, then merge.

This needs one setting: **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**.

To run it by hand: `pip install requests pyyaml && python bin/orcid_sync.py --dry-run`.

## CV as a PDF

Put a PDF in `assets/pdf/` and add `cv_pdf: /assets/pdf/<name>.pdf` to the header of `_pages/cv.md` to show a download button on the CV page.

## Previewing locally (optional)

With Docker installed: `docker compose up`, then open <http://localhost:8080>.

## Licence

Theme code is MIT licensed (see `LICENSE`). Text and images are © Oliver S. Hammond.
