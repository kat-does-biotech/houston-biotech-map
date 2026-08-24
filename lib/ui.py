import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import pandas as pd
from lib.data_loader import CATEGORIES, CATEGORY_COLORS, connections_for
"""from lib.jobs import get_open_role_count"""
from datetime import datetime
from streamlit_calendar import calendar as st_calendar

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
            font-size: 1.75rem !important;
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

    """total_known = 0
    any_unresolved = False
    for node_id, row in subset.iterrows():
        job_board_type = row.get("job_board_type", "")
        careers_url = row.get("careers_url", "")
        if job_board_type:
            count = get_open_role_count(job_board_type, row.get("job_board_ref", ""))
            if count is not None:
                total_known += count
            else:
                any_unresolved = True
        elif careers_url:
            any_unresolved = True  # has a careers page, just no queryable API

    if total_known or any_unresolved:
        suffix = "+" if any_unresolved else ""
        st.markdown(f"**{total_known}{suffix} jobs available in this sector**")"""

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
    careers_url = row.get("careers_url", "")
    careers_url = row.get("careers_url", "")
    if careers_url:
        count = None
        job_board_type = row.get("job_board_type", "")
        if job_board_type:
            count = get_open_role_count(job_board_type, row.get("job_board_ref", ""))
        if count:
            st.markdown(f"[{count} open role{'s' if str(count) != '1' else ''} \u2014 View careers page \u2197]({careers_url})")
        else:
            st.markdown(f"[View open roles \u2197]({careers_url})")

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

def render_nav(go_categories, go_calendar):
    cols = st.columns([1, 1, 6])
    with cols[0]:
        if st.button("🗺️ Ecosystem map", key="nav_map", use_container_width=True):
            go_categories()
            st.rerun()
    with cols[1]:
        if st.button("📅 Events calendar", key="nav_cal", use_container_width=True):
            go_calendar()
            st.rerun()
    st.divider()

def render_calendar(institutions, events, go_node):
    today = pd.Timestamp(datetime.now().date())
    upcoming = events[events["date_parsed"] >= today].sort_values("date_parsed")

    main_col, side_col = st.columns([3, 1])

    with side_col:
        st.markdown("#### Coming up")
        if upcoming.empty:
            st.caption("No upcoming events logged.")
        for _, ev in upcoming.head(3).iterrows():
            with st.container(border=True):
                st.markdown(f"**{ev['title']}**")
                st.caption(ev["date_parsed"].strftime("%b %d"))

    with main_col:
        calendar_events = []
        for idx, ev in events.iterrows():
            if pd.isna(ev["date_parsed"]):
                continue
            calendar_events.append({
                "id": str(idx),
                "title": ev["title"],
                "start": ev["date_parsed"].strftime("%Y-%m-%d"),
            })

        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,listMonth",
            },
            "initialView": "dayGridMonth",
            "height": 650,
        }

        result = st_calendar(events=calendar_events, options=calendar_options, key="ecosystem_calendar")

        if result and result.get("callback") == "eventClick":
            clicked_id = result["eventClick"]["event"].get("id")
            if clicked_id is not None and int(clicked_id) in events.index:
                st.markdown("---")
                _render_event_card(events.loc[int(clicked_id)], institutions, go_node)


def _render_event_card(ev, institutions, go_node):
    with st.container(border=True):
        st.markdown(f"**{ev['title']}**")
        date_str = ev["date_parsed"].strftime("%B %d, %Y") if pd.notna(ev["date_parsed"]) else ev["date"]
        detail = f"{date_str}"
        if ev["time"]:
            detail += f" \u00b7 {ev['time']}"
        if ev["location"]:
            detail += f" \u00b7 {ev['location']}"
        st.caption(detail)
        if ev["description"]:
            st.write(ev["description"])

        inst_id = ev["institution_id"]
        if inst_id and inst_id in institutions.index:
            if st.button(f"Hosted by {institutions.loc[inst_id, 'name']}", key=f"ev_inst_{ev['event_id']}"):
                go_node(inst_id)
                st.rerun()
        if ev["url"]:
            st.markdown(f"[Event page \u2197]({ev['url']})")

FEEDBACK_FORM_URL = "https://forms.gle/https://forms.gle/Nsfgj51FbFm39kZX7"

def render_footer():
    st.divider()
    st.link_button("🚩 Report a broken link, text errors, and request added content", FEEDBACK_FORM_URL)