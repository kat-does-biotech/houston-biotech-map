# Houston biotech ecosystem map

A three-layer, click-through map of the Houston biotech ecosystem:
categories → institution list → institution detail with cross-category
connections. Built as a Streamlit app so it deploys free and public on
Streamlit Community Cloud.

## Running it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
app.py                     # entry point: session state, URL sync, screen routing
lib/data_loader.py         # loads the three CSVs, computes connections for a node
lib/ui.py                  # renders the category grid, list, and detail screens
data/institutions.csv      # entity table
data/relationship_types.csv# small fixed lookup of relationship types
data/edges.csv             # the actual connections between institutions
```

## The data model

**institutions.csv** — one row per entity.
`parent_id` is how a structural hierarchy works (e.g. Baylor and MD
Anderson have `parent_id = tmc`). `scale_value` / `scale_unit` are placeholder
columns for later bubble-sizing (sq ft, headcount, etc.) — currently empty.
`source_url` and `last_updated` are there so you can eventually show
provenance in the UI, which matters if this is going to double as a
credibility signal for a portfolio piece.

**relationship_types.csv** — a small, fixed lookup (5 rows to start:
structural, physical, capital, pipeline, partnership). Each type carries an
icon and a forward/reverse label pair, so a `member_of` edge reads as
"parent organization" on the child's page and "member institution" on the
parent's page, without storing the relationship twice.

**edges.csv** — the actual connections, stored once per pair
(`source_id, target_id, type_id`). `connections_for()` in `data_loader.py`
walks this table and resolves the correct label depending on which side of
the edge you're viewing from.

## Currently placeholder data

The 12 institutions and 14 edges in `data/` are the same set from the
prototyping conversation — enough to exercise every relationship type and
the TMC-as-parent structure, not a real dataset yet. Replace/extend these
CSVs directly, or swap `load_data()` in `lib/data_loader.py` for a pull
from Google Sheets / Airtable once you're ready — nothing else in the app
needs to change as long as the three dataframes keep the same columns.

## Known gaps / next steps

- No search or filter within a category yet — fine at 12 entities, will
  matter once the list gets long.
- `scale_value` isn't used anywhere yet — reserved for a future bubble-map
  entry screen.
- Relationship icons are plain emoji for now (version-safe across Streamlit
  releases); swap for a proper icon font if you want tighter visual control.
- No confirmed/inferred badge shown in the UI yet, even though the column
  exists in `edges.csv` — worth surfacing once you start citing sources.
