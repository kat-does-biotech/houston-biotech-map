import streamlit as st
from lib.data_loader import load_data
from lib.ui import render_breadcrumbs, render_categories, render_list, render_detail

st.set_page_config(page_title="Houston Biotech Ecosystem Map", layout="wide")


institutions, rel_types, edges = load_data()

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

st.title("Houston biotech ecosystem map")
st.caption("Developed and maintained by [Kaitlyn Sanchez-Nussberger](https://www.linkedin.com/in/kaitlyn-sanchez-nussberger/)")
render_breadcrumbs(institutions, go_categories, go_category)

#if st.session_state.screen == "categories":
    #render_categories(institutions, go_category)
if st.session_state.screen == "categories":
    view_mode = st.radio("View", ["Categories", "Bubble map"], horizontal=True, label_visibility="collapsed")
    if view_mode == "Categories":
        render_categories(institutions, go_category)
    else:
        render_bubble_map(institutions, edges, rel_types)
elif st.session_state.screen == "list":
    render_list(institutions, edges, rel_types, st.session_state.category, go_node)
elif st.session_state.screen == "detail":
    render_detail(institutions, rel_types, edges, st.session_state.node, go_node, go_category)
