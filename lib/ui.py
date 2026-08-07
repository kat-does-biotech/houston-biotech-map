import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from lib.data_loader import CATEGORIES, CATEGORY_COLORS, connections_for

def render_infographic(institutions, edges, stats):
    st.markdown(
        """
        <style>
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            line-height: 1.2;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Houston biotech ecosystem, at a glance")

    def safe(text):
        return str(text).replace("$", "\\$")

    all_stats = [(safe(row["label"]), safe(row["value"])) for _, row in stats.iterrows()]
    all_stats.append(("Institutions tracked", str(len(institutions))))
    all_stats.append(("Ecosystem connections mapped", str(len(edges))))

    PER_ROW = 4
    for i in range(0, len(all_stats), PER_ROW):
        row_stats = all_stats[i:i + PER_ROW]
        cols = st.columns(PER_ROW)
        for col, (label, value) in zip(cols, row_stats):
            with col:
                st.metric(label, value)
    st.caption(
        "Regional figures via Greater Houston Partnership, TMC, and Texas State resources. "
        "Institution and connection counts reflect this map's current dataset."
    )

def render_network_map(institutions, edges, rel_types, go_node):
    """Force-directed network map using real graph connectivity (via networkx)
    for node positions, rendered with Plotly so clicks return to Python
    natively -- no iframe, no sandbox restrictions."""
    G = nx.Graph()
    G.add_nodes_from(institutions.index)
    for _, row in edges.iterrows():
        G.add_edge(row["source_id"], row["target_id"])
    pos = nx.spring_layout(G, seed=42, k=0.8)

    edge_x, edge_y = [], []
    for _, row in edges.iterrows():
        x0, y0 = pos[row["source_id"]]
        x1, y1 = pos[row["target_id"]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1, color="rgba(150,150,150,0.45)"),
        hoverinfo="none", showlegend=False,
    )

    node_ids = list(institutions.index)
    counts = {nid: len(connections_for(nid, edges, rel_types)) for nid in node_ids}
    label_cutoff = np.quantile(list(counts.values()), 0.75) if counts else 0

    node_trace = go.Scatter(
        x=[pos[nid][0] for nid in node_ids],
        y=[pos[nid][1] for nid in node_ids],
        mode="markers+text",
        text=[institutions.loc[nid, "name"] if counts[nid] >= label_cutoff else "" for nid in node_ids],
        textposition="middle center",
        textfont=dict(size=8),
        customdata=node_ids,
        hovertext=[
            f"{institutions.loc[nid, 'name']} \u2014 {counts[nid]} connection{'s' if counts[nid] != 1 else ''}"
            for nid in node_ids
        ],
        hoverinfo="text",
        marker=dict(
            size=[20 + min(counts[nid], 10) * 5 for nid in node_ids],
            color=[CATEGORY_COLORS.get(institutions.loc[nid, "category"], "#999999") for nid in node_ids],
            line=dict(width=1, color="white"),
        ),
        showlegend=False,
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        height=750,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)",
    )

    event = st.plotly_chart(fig, use_container_width=True, key="network_map", on_select="rerun")
    points = event.selection.get("points") if event and event.selection else None
    if points:
        clicked = points[0].get("customdata")
        clicked_id = clicked[0] if isinstance(clicked, list) else clicked
        if clicked_id:
            go_node(clicked_id)
            st.rerun()

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
