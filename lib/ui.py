import streamlit as st
from lib.data_loader import CATEGORIES, CATEGORY_COLORS, connections_for


def render_breadcrumbs(institutions, go_categories, go_category):
    crumbs = st.columns([1.4, 1.4, 2, 4])
    with crumbs[0]:
        if st.button("Ecosystem map", key="crumb_home", use_container_width=True):
            go_categories()
            st.rerun()
    if st.session_state.category:
        with crumbs[1]:
            label = CATEGORIES[st.session_state.category]
            if st.button(label, key="crumb_cat", use_container_width=True):
                go_category(st.session_state.category)
                st.rerun()
    if st.session_state.node:
        with crumbs[2]:
            st.markdown(f"**{institutions.loc[st.session_state.node, 'name']}**")
    st.divider()


def render_categories(institutions, go_category):
    cols = st.columns(3)
    for i, (cat_id, label) in enumerate(CATEGORIES.items()):
        count = int((institutions["category"] == cat_id).sum())
        color = CATEGORY_COLORS[cat_id]
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(
                    f'<div style="width:10px;height:10px;border-radius:50%;'
                    f'background:{color};display:inline-block;margin-right:6px;"></div>'
                    f'<span style="font-weight:600;">{label}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(f"{count} listed")
                if st.button("View", key=f"cat_{cat_id}", use_container_width=True):
                    go_category(cat_id)
                    st.rerun()


def render_list(institutions, edges, rel_types, category, go_node):
    subset = institutions[institutions["category"] == category]
    if subset.empty:
        st.info("No institutions logged in this category yet.")
        return
    for node_id, row in subset.iterrows():
        conns = connections_for(node_id, edges, rel_types)
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1.4, 1])
            with c1:
                st.markdown(f"**{row['name']}**")
                st.caption(row["summary"])
            with c2:
                n = len(conns)
                st.caption(f"{n} ecosystem link{'s' if n != 1 else ''}")
            with c3:
                if st.button("Open", key=f"open_{node_id}", use_container_width=True):
                    go_node(node_id)
                    st.rerun()


def render_detail(institutions, rel_types, edges, node_id, go_node, go_category):
    row = institutions.loc[node_id]
    st.subheader(row["name"])
    if isinstance(row.get("parent_id"), str) and row["parent_id"]:
        parent_name = institutions.loc[row["parent_id"], "name"]
        st.caption(f"Part of {parent_name}")
    st.write(row["summary"])
    st.markdown(f"[Visit main site \u2197]({row['url']})")

    conns = connections_for(node_id, edges, rel_types)
    if not conns:
        st.caption("No connections logged yet.")
        return

    st.markdown("**Connected to:**")
    cols = st.columns(2)
    for i, c in enumerate(conns):
        other = institutions.loc[c["other"]]
        label = f"{c['icon']}  {other['name']} \u2014 {c['label']}"
        with cols[i % 2]:
            if st.button(label, key=f"chip_{node_id}_{c['other']}_{i}", use_container_width=True):
                go_node(c["other"])
                st.rerun()
            if c["note"]:
                st.caption(c["note"])
