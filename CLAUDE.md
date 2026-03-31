# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jekyll-based academic portfolio website built on the [al-folio](https://github.com/alshedivat/al-folio) template. Deployed to GitHub Pages via GitHub Actions.

## Development Commands

### Local development (Dev Container — recommended in VS Code/Codespaces)

The dev container auto-starts Jekyll via `./bin/entry_point.sh` on attach. Site is served at `http://localhost:8080` with live reload. Config changes (`_config.yml`) trigger an automatic server restart via inotify.

### Docker

```bash
docker compose up        # Serve at http://localhost:8080
```

### Manual build

```bash
bundle exec jekyll serve --host=0.0.0.0 --port=8080 --livereload  # Dev server
bundle exec jekyll build                                            # Build only
npm run build:css                                                   # PurgeCSS + Autoprefixer (run after jekyll build)
npm run build                                                       # Jekyll build + CSS optimization
```

### Formatting

```bash
npx prettier --write .   # Format Liquid, Markdown, etc. (uses @shopify/prettier-plugin-liquid)
```

## Architecture

### Content

- **`_pages/`** — Static pages (about, blog, publications, projects, 404). The home page is `about.md` with `permalink: /`.
- **`_posts/`** — Blog posts. Permalink pattern: `/blog/:year/:title/`.
- **`_projects/`** — Project collection entries.
- **`_bibliography/papers.bib`** — BibTeX file for publications, rendered by `jekyll-scholar`.
- **`assets/json/resume.json`** — CV data in JSON Resume format, fetched via `jekyll-get-json`.

### Templates

- **`_layouts/`** — Liquid layouts. Key ones: `default.liquid` (base), `about.liquid` (home), `post.liquid` (blog), `bib.liquid` (publications).
- **`_includes/`** — Liquid partials (header, footer, head, giscus comments, bib search, etc.).
- **`_sass/`** — SCSS styles with `_variables.scss` for theming and `_themes.scss` for light/dark mode.

### Plugins & Build

- **`_plugins/`** — Custom Ruby plugins (cache busting, 3rd-party library downloads, Google Scholar citations, external posts).
- **`_config.yml`** — Main config (~630 lines). Contains site metadata, plugin settings, third-party library CDN URLs with integrity hashes, and feature toggles.
- Third-party JS/CSS libraries are downloaded to `assets/libs/` at build time by `_plugins/download-3rd-party.rb` based on URLs in `_config.yml`.

### CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **`deploy.yml`** — Main deployment (sets `JEKYLL_ENV=production`, builds with imagemagick, runs PurgeCSS, deploys to GitHub Pages).
- **`prettier.yml`** — Format checking.
- **`broken-links.yml`** — Link validation.
- **`axe.yml`** — Accessibility testing.

### Key Integrations

- **Comments:** Giscus (GitHub Discussions) — configured in `_config.yml`, template in `_includes/giscus.liquid`.
- **Analytics:** Google Analytics.
- **Math:** MathJax, enabled per-page via front matter (`math: true`).
- **Bibliography badges:** Altmetric, Dimensions, Google Scholar, Inspire HEP.

## Commit Guidelines

- Do NOT include `Co-Authored-By` lines referencing Claude or any AI tool in commit messages.
- Do NOT include any AI attribution in commits, PRs, or code comments.
