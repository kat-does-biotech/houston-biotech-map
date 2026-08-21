import requests
import streamlit as st


@st.cache_data(ttl=24 * 60 * 60)  # refresh at most every 6 hours -- be a polite API citizen
def get_open_role_count(job_board_type, job_board_ref):
    """Look up a live open-role count from a known ATS's public API.
    Returns None on any failure so the UI can fall back gracefully
    instead of crashing the page over a jobs API being down."""
    if not job_board_type or not job_board_ref:
        return None
    try:
        if job_board_type == "greenhouse":
            url = f"https://boards-api.greenhouse.io/v1/boards/{job_board_ref}/jobs"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return len(resp.json().get("jobs", []))
        elif job_board_type == "lever":
            url = f"https://api.lever.co/v0/postings/{job_board_ref}?mode=json"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return len(resp.json())
    except Exception:
        return None
    return None