# Houston Biotech Ecosystem Map

[**Live app →**](https://houston-biotech-map.streamlit.app/)

An interactive map of the Houston biotech and life sciences ecosystem —
institutions, startups, funders, accelerators, and the relationships
between them — built for job seekers, investors, industry med affairs,
and economic development professionals.

This started as a personal project to build career-relevant knowledge in
tech transfer, commercialization, and ecosystem development, and grew into
a maintained tool. It's actively curated and will always be incomplete —
see [Known limitations](#known-limitations) below.

## What it does

* **Network map** — every tracked institution as a node, sized by how
connected it is and colored by category, positioned by an actual
force-directed graph layout (not just visually grouped). Click any
node to drill into it.
* **Typed relationships** — connections between institutions aren't just
links, they're categorized (structural, physical, capital, pipeline,
partnership) with plain-language labels, so you can see *how* two
organizations relate, not just *that* they do.
* **Category browser** — Academic Institutions, Industry HQ/Infrastructure,
Startups \& Emerging Biotech, Accelerators, Funding/Local VC, and
Convener/Support Orgs, each with its own listing and detail pages.
* **Ecosystem snapshot** — headline regional stats (NIH funding, lab
space, etc.) alongside live counts of what's actually tracked in this
map.
* **Events calendar** — upcoming and past ecosystem events, linked back
to the hosting institution where applicable.

**Careers links**



Tech stack

Built with [Streamlit](https://streamlit.io), deployed free on Streamlit
Community Cloud. Network layout via
[networkx](https://networkx.org), visualization via
[Plotly](https://plotly.com/python/), data stored as plain CSVs.

## Project structure

```
app.py                       # entry point: navigation, session state, screen routing
lib/
├── data\_loader.py           # loads all data tables, category/color definitions
├── ui.py                    # renders every screen: map, categories, list, detail, calendar
└── jobs.py                  # live open-role lookups for supported ATS platforms (currently unsupported)
data/
├── institutions.csv         # every tracked entity
├── relationship\_types.csv   # the fixed vocabulary of connection types
├── edges.csv                # the actual connections between institutions
├── stats.csv                # curated regional headline figures
└── events.csv               # ecosystem events
```

## Running it locally

```bash
git clone https://github.com/kat-does-biotech/houston-biotech-map.git
cd houston-biotech-map
pip install -r requirements.txt
streamlit run app.py
```

## The data model, briefly

Institutions can have a `parent\_id` (so, e.g., a hospital system can be
listed as its member institutions' parent rather than a peer). Every
connection between two institutions is stored once, with a relationship
*type* that carries a forward and reverse label — so the same edge reads
correctly from either institution's page (a "member institution" from
one side is a "parent organization" from the other). Adding a new
institution or connection is just adding a row to a CSV; adding a new
*kind* of category or relationship type requires a small code change.




## Known limitations

* **This is not exhaustive.** Coverage reflects what's been researched
and curated so far, not the full Houston biotech landscape. If your
organization is missing or something's wrong, reach out.
* **Data is primarily manually curated**, sourced from public press coverage,
organizational websites, and (where noted) direct outreach. 



## A note on how this was built

This project, including its data model, the ecosystem research behind
it, and every curation decision, was designed and directed by me. However, I
used Claude (Anthropic's AI assistant) throughout development for
coding and debugging assistance.



## Get in touch

Built and maintained by **Kaitlyn Sanchez-Nussberger** —
[LinkedIn](https://www.linkedin.com/in/kaitlyn-sanchez-nussberger/).
Corrections, additions, and conversations about the Houston biotech
ecosystem are always welcome.

