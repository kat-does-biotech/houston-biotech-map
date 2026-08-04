import pandas as pd
import streamlit as st

# Category id -> display label. Order here controls display order everywhere.
CATEGORIES = {
    "academic": "Academic institutions",
    "industry": "Industry HQ / infrastructure",
    "accelerator": "Startup resources / accelerators",
    "funding": "Funding / local VC",
    "support": "Convener / support orgs",
}

# Light tint used for category cards. Keep in sync with CATEGORIES keys.
CATEGORY_COLORS = {
    "academic": "#7F77DD",
    "industry": "#378ADD",
    "accelerator": "#D85A30",
    "funding": "#BA7517",
    "support": "#1D9E75",
}


@st.cache_data
def load_data():
    """Load institutions, relationship types, and edges from /data.

    Swap these read_csv calls for a Google Sheets / Airtable pull later —
    everything downstream just expects three dataframes with these columns,
    so the rest of the app doesn't need to change.
    """
    institutions = pd.read_csv("data/institutions.csv").set_index("id")
    rel_types = pd.read_csv("data/relationship_types.csv").set_index("type_id")
    edges = pd.read_csv("data/edges.csv")
    return institutions, rel_types, edges


def connections_for(node_id, edges, rel_types):
    """Return the list of connections for one institution, from either side.

    Each edge is stored once (source_id, target_id, type_id). This walks the
    full edge list and picks the forward_label when node_id is the source,
    or the reverse_label when node_id is the target — so you never have to
    store both directions of a relationship.
    """
    conns = []
    for _, row in edges.iterrows():
        rel = rel_types.loc[row["type_id"]]
        if row["source_id"] == node_id:
            conns.append({
                "other": row["target_id"],
                "icon": rel["icon"],
                "label": rel["forward_label"],
                "note": row.get("note", "") or "",
            })
        elif row["target_id"] == node_id:
            conns.append({
                "other": row["source_id"],
                "icon": rel["icon"],
                "label": rel["reverse_label"],
                "note": row.get("note", "") or "",
            })
    return conns
