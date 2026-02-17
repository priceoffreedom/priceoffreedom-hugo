# Price of Freedom Museum - Hugo Site

## Project Overview
Hugo static site for the Price of Freedom Museum (priceoffreedom.us), a military museum in China Grove, NC. Migrated from WordPress.

## Tech Stack
- **Hugo** v0.155.3 (extended) - static site generator
- **Theme**: [hugo-universal-theme](https://github.com/devcows/hugo-universal-theme) (git submodule)
- **Hosting**: GitHub Pages via GitHub Actions
- **Repo**: github.com/priceoffreedom/priceoffreedom-hugo

## Directory Structure
```
priceoffreedom/
├── content/              # Markdown content pages
│   ├── _index.md         # Homepage
│   ├── reviews/          # Reviews/testimonials page
│   ├── media/            # Photo gallery (27 images)
│   └── posts/            # Blog posts
├── data/                 # Theme data files (YAML)
│   ├── carousel/         # Homepage carousel slides
│   ├── features/         # Feature cards on homepage
│   └── testimonials/     # Testimonial quotes
├── static/
│   ├── css/style.olive.css  # Custom color scheme (#848233)
│   ├── img/              # Logo and carousel images
│   └── images/           # All scraped site images
├── themes/
│   └── hugo-universal-theme/  # Theme (git submodule)
├── scripts/              # Utility scripts and reference
│   ├── scrape_pof.py     # Scraper that pulled content from WordPress
│   ├── raw_html/         # Original HTML from WordPress site
│   ├── install_requirements.sh
│   └── setup_second_github.sh
├── .github/workflows/hugo.yml  # GitHub Pages deployment
├── hugo.toml             # Site configuration
└── TODO.md               # Admin/setup task tracking
```

## Git / GitHub Setup
- **GitHub account**: `priceoffreedom` (separate from main dev account `mrbell-dev`)
- **SSH config**: Uses `github-priceoffreedom` host alias in `~/.ssh/config` with dedicated key `~/.ssh/id_ed25519_priceoffreedom`
- **Remote**: `git@github-priceoffreedom:priceoffreedom/priceoffreedom-hugo.git`
- **Repo-local git identity**: user `priceoffreedom`, email `priceoffreedom@users.noreply.github.com` (TODO: change to museum email)

## Custom Color Scheme
The theme's default blue was replaced with olive green `#848233`. This is done via `static/css/style.olive.css` (a copy of the theme's default CSS with custom CSS variables). The `style = "olive"` setting in `hugo.toml` activates it.

## Key Commands
```bash
# Local preview
hugo server -s ~/Desktop/webdev/priceoffreedom --buildDrafts

# Production build
hugo -s ~/Desktop/webdev/priceoffreedom --gc --minify

# Re-scrape WordPress site (if needed)
~/Desktop/webdev/scraper_venv/bin/python scripts/scrape_pof.py
```

## Theme Customization
- Theme config is in `hugo.toml` under `[params]`
- Carousel slides: `data/carousel/*.yaml`
- Feature cards: `data/features/*.yaml`
- Testimonials: `data/testimonials/*.yaml`
- Colors: CSS custom properties in `static/css/style.olive.css` (first 11 lines)
- The theme uses Bootstrap 3.4 and FontAwesome icons
