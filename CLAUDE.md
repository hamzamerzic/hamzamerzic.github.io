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

- **Comments:** Giscus (GitHub Discussions) — configured in `_config.yml`, template in `_includes/giscus.liquid`. Enable on a post with `giscus_comments: true` in its front matter (the gate is `{% if site.giscus and page.giscus_comments %}` in `_layouts/post.liquid`).
- **Analytics:** Google Analytics.
- **Math:** MathJax, enabled per-page via front matter (`math: true`).
- **Bibliography badges:** Altmetric, Dimensions, Google Scholar, Inspire HEP.

## Design system

The site uses a charcoal + emerald palette matching the [Möbius](/mobius/) project. The lever is the `--global-*` custom properties in `_sass/_themes.scss` (per light/dark mode), built from Sass tokens in `_sass/_variables.scss`. Fonts: Inter (UI/body) + JetBrains Mono (code, metadata, table numerics), loaded via `_config.yml` `google_fonts`. `_sass/_mobius-modern.scss` is the modernization layer (imported in `assets/css/main.scss` after `base`): translucent nav, card hover-lift, code chips, shared post components (`.tldr`, `.stat-callout`, `.pull-quote`), modern content tables, and a themed HTML **diagram kit** (`.mb-diagram`, `.mb-flow`, `.mb-node`, `.mb-stack`, `.mb-lanes`, `.mb-cycle`) — prefer these over ASCII art or stock images in posts. To verify CSS without the full Jekyll/Docker build, compile `assets/css/main.scss` with dart-sass (`--load-path _sass`, substituting the `{{ site.max_width }}` Liquid) and screenshot a harness page that links the real `main.css` + `assets/css/bootstrap.min.css` + Google Fonts in both `<html data-theme="dark">` and light.

## Blog: the Möbius series

Three linked posts under `_posts/2026-*`: `mobius-an-app-that-builds-itself`, `the-self-improvement-harness`, `the-agent-is-the-kernel` (app store / OS). They cross-link as a series and share the components above. Honest "shipped vs aspirational" framing is a deliberate house style — do not overclaim about Möbius features.

## Commit Guidelines

- Do NOT include `Co-Authored-By` lines referencing Claude or any AI tool in commit messages.
- Do NOT include any AI attribution in commits, PRs, or code comments.
