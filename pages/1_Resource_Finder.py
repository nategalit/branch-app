import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Find Resources", page_icon="🔍")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("🔍 Resource & Opportunity Finder")
st.write("Search for active community locations by the services they provide.")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Get distinct service types for the filter dropdown
    cur.execute("SELECT DISTINCT primary_service FROM locations WHERE is_active = true;")
    services = [row[0] for row in cur.fetchall()]
    
    # Add a 'Show All' option at the beginning
    services.insert(0, "Show All")

    # The Filter
    selected_service = st.selectbox("Filter by Service Type:", services)

    # The Search Bar
    search_term = st.text_input("Or search by location name:")

    st.markdown("---")

    # Build the query dynamically based on filters
    query = "SELECT name AS \"Location\", primary_service AS \"Service\", address AS \"Address\" FROM locations WHERE is_active = true"
    params = []

    if selected_service != "Show All":
        query += " AND primary_service = %s"
        params.append(selected_service)
    
    if search_term.strip():
        query += " AND name ILIKE %s"
        params.append(f"%{search_term.strip()}%")

    query += " ORDER BY name;"

    # Execute and display
    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["Location", "Service", "Address"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No locations found matching your criteria.")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database error: {e}")