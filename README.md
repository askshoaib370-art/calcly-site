# Calcly — static calculator site

This is a fully static website: plain HTML, CSS, and vanilla JavaScript. No WordPress, no database,
no server-side code required. It can be hosted for free on Cloudflare Pages, GitHub Pages, Netlify, or Vercel.

## What's in here
- `index.html` — homepage
- `calculators/<category>/<slug>/index.html` — 25 working calculators across 7 categories
- `assets/css/style.css` — all site styling (one shared file)
- `about/`, `privacy/`, `terms/`, `contact/` — required pages before AdSense will approve the site
- `sitemap.xml`, `robots.txt` — for Google Search Console
- `build.py` — the generator script. All calculator content and logic lives in the `CALCULATORS` list
  near the top of this file. **This is how you scale toward 5,000 calculators**: add a new dict to that
  list (copy an existing one as a template, change the slug/category/formula/content/JS) and rerun:

  ```
  python3 build.py
  ```

  This regenerates every page. You never hand-edit the generated HTML files.

## Deploying (first time)
1. Push this whole folder to a GitHub repository.
2. In Cloudflare: Workers & Pages → Create → Pages → Connect to Git → select the repo.
3. Build settings: **no build command needed**, output directory = `/` (the repo root).
4. Deploy. You'll get a free `*.pages.dev` URL immediately.
5. Later, add your purchased domain under that Pages project's "Custom domains" tab — free SSL included.

## Before applying to Google AdSense
- Update the real email in `contact/index.html` and `build.py` (`static_pages()`).
- Update `BASE_URL` in `build.py` to your real domain, then rerun `python3 build.py`.
- Make sure about/privacy/terms pages reflect your actual business details.

## Adding more calculators
Each entry in `CALCULATORS` needs: `slug`, `category` (must match a key in `CATEGORIES`), `name`,
`intro`, `form_html` (inputs), `result_html` (output placeholders), `script` (the JS `calc()` function),
`how_it_works`, and `faq` (list of Q/A tuples). Follow the pattern of any existing entry.
