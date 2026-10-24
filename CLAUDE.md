# Jennifer Abadi's website (jenniferabadi.com)

Jennifer is a cooking instructor, cookbook author and recipe tester. This repository is her
whole website. She is not technical: she will ask for changes in plain language
("add my December class at the JCC", "change the price of a virtual lesson").
Do the work, show her what changed, and publish only after she says it looks right.
Explain things in plain words; never ask her to run commands.

## How the site works
- `docs/` is the published website. GitHub Pages serves it; pushing to `main` puts it live in about a minute.
- `docs/` is generated. Do not edit pages in `docs/` by hand (except images, see below).
  Change the content, then run `python3 builder/build.py` to regenerate everything.
- The build must end with `unknown internal links: [] 0`. Commit `content/`, `raw/`, `builder/` and `docs/` together.
- The look copies her former WordPress theme exactly. Do not restyle anything unless she asks.

## Where the content lives
| What | File |
|---|---|
| Upcoming classes & events (homepage + Upcoming Events page) | `content/upcoming.json` (create it if missing) |
| Recipes and articles | `content/posts.json` |
| Cooking class catalog + one page per class | `content/classes.json` |
| About, Cookbooks, Gift Certificates, Contact, Catalog intro/FAQ | `raw/about.html`, `raw/cookbooks.html`, `raw/gift-certificates-2023.html`, `raw/contact-jennifer.html`, `raw/cooking-class-catalog.html` (captured WordPress markup: find the text and edit it in place) |
| Homepage text, testimonials, portfolio slider | `builder/build.py` (`build_home`) and `raw/portfolio_data.json` |
| Header, menu, footer | `builder/common.py` |
| Styles / scripts | `docs/css/style.css`, `docs/js/site.js` (these two are edited directly) |

### Upcoming event entry (`content/upcoming.json`, a list, soonest first)
```json
{"date": "Sunday, December 14, 2026", "time": "11:00 AM – 12:30 PM",
 "title": "Hanukkah Sufganiyot Workshop", "where": "JCC Manhattan (in-person)",
 "description": "<p>One or two sentences.</p>",
 "link": "https://registration-page", "link_text": "Register", "image": "images/photo.jpg"}
```
Remove events once they are past. An empty list shows "Currently, there are no events planned."

### New recipe or article (`content/posts.json`, newest first)
Copy an existing entry. Required: `slug` (lowercase-with-dashes, becomes the address),
`title`, `date`, `categories` (recipes: e.g. `["All Recipes", "Passover Recipes"]`; articles: `["Articles"]`),
`hero_image`, `content_html`, `excerpt`, `tags`.

### New class (`content/classes.json`)
Copy an existing entry. `formats` decides whether it appears in the catalog: only these six are listed
(see `CATALOG_FORMATS` in `builder/build.py`): 1-DISH VIRTUAL…, 2-DISH/LONGER DISH VIRTUAL…, IN-PERSON PRIVATE 3-HOUR…,
KIDS COOKING CLASSES, TEENS AND TWEENS COOKING CLASSES, VIRTUAL CHEF TALK…. Any other format (e.g. "Private Events")
gets its own page but stays out of the catalog. `topics` feed the cuisine/holiday filter.

## Images
Save new photos into `docs/images/` (JPEG, at most 1600 px wide, under ~400 KB) and refer to them as `images/<file name>`.
Never delete images: old pages use them.

## Contact form & newsletter
- The contact form sends through Web3Forms (access key in `builder/build.py`, safe to be public) to Jennifer's email.
- The pre-ticked newsletter box also subscribes the visitor to her Mailchimp list (double opt-in). Mailchimp address is in the form's `data-mailchimp` attribute.
- "Sign Up for Class Updates" buttons link to http://eepurl.com/cyZruf.

## Rules
- Never commit the WordPress export (`*.xml`) or anything with customers' personal details.
- Keep page addresses unchanged (they match the old WordPress URLs so existing links keep working).
- Her email (@jenniferabadi.com) is hosted separately at DreamHost; never touch DNS email (MX) records.
