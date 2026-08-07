import streamlit as st
from lib.data_loader import load_data
from lib.ui import render_breadcrumbs, render_categories, render_list, render_detail, render_network_map, render_infographic

st.set_page_config(page_title="Houston Biotech Ecosystem Map", layout="wide")

institutions, rel_types, edges, stats = load_data()

# --- Session state, seeded from the URL so a specific view is bookmarkable/shareable ---
params = st.query_params
if "screen" not in st.session_state:
    st.session_state.screen = params.get("screen", "categories")
    st.session_state.category = params.get("category") or None
    st.session_state.node = params.get("node") or None


def go_categories():
    st.session_state.screen = "categories"
    st.session_state.category = None
    st.session_state.node = None


def go_category(cat_id):
    st.session_state.screen = "list"
    st.session_state.category = cat_id
    st.session_state.node = None


def go_node(node_id):
    st.session_state.screen = "detail"
    st.session_state.category = institutions.loc[node_id, "category"]
    st.session_state.node = node_id


# keep the URL in sync with the current view
st.query_params["screen"] = st.session_state.screen
if st.session_state.category:
    st.query_params["category"] = st.session_state.category
elif "category" in st.query_params:
    del st.query_params["category"]
if st.session_state.node:
    st.query_params["node"] = st.session_state.node
elif "node" in st.query_params:
    del st.query_params["node"]

st.title("Houston Biotech Ecosystem Map")
st.caption("Developed and maintained by [Kaitlyn Sanchez-Nussberger](https://www.linkedin.com/in/kaitlyn-sanchez-nussberger/)")
st.caption("An inexhaustive list")

render_breadcrumbs(institutions, go_categories, go_category)

if st.session_state.screen == "categories":
    render_infographic(institutions, edges, stats)
    render_network_map(institutions, edges, rel_types, go_node)
    st.markdown("#### Browse by category")
    render_categories(institutions, go_category)
elif st.session_state.screen == "list":
    render_list(institutions, edges, rel_types, st.session_state.category, go_node)
elif st.session_state.screen == "detail":
    render_detail(institutions, rel_types, edges, st.session_state.node, go_node, go_category)