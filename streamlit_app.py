import streamlit as st
import psycopg2
import pandas as pd

# 1. Configure the page settings
st.set_page_config(page_title="Branch | Community Connection", page_icon="🌿", layout="wide")

# 2. Define the database connection function
def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

# 3. Main Page Header
st.title("🌿 Branch")
st.subheader("Connecting Volunteers with Community Resources")
st.write("Welcome to Branch! Use the sidebar to navigate between finding resources, logging activity, and managing the directory.")
st.markdown("---")

# 4. Dashboard Metrics
st.header("📊 Community Impact Dashboard")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Get total volunteers
    cur.execute("SELECT COUNT(*) FROM users WHERE account_type = 'Volunteer';")
    total_volunteers = cur.fetchone()[0]

    # Get total community members
    cur.execute("SELECT COUNT(*) FROM users WHERE account_type = 'Community Member';")
    total_members = cur.fetchone()[0]

    # Get total hours logged
    cur.execute("SELECT SUM(hours_logged) FROM visits WHERE visit_type = 'Volunteered';")
    total_hours = cur.fetchone()[0]
    if total_hours is None:
        total_hours = 0

    # Get active locations
    cur.execute("SELECT COUNT(*) FROM locations WHERE is_active = true;")
    active_locations = cur.fetchone()[0]

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Volunteers", total_volunteers)
    col2.metric("Community Members", total_members)
    col3.metric("Total Hours Volunteered", f"{total_hours:.1f}")
    col4.metric("Active Locations", active_locations)

    st.markdown("---")

    # 5. Recent Activity Table
    st.subheader("Recent Activity")
    
    # This query joins our 3 tables together to make the data readable
    cur.execute("""
        SELECT 
            u.first_name || ' ' || u.last_name AS "User",
            u.account_type AS "Account",
            v.visit_type AS "Action",
            l.name AS "Location",
            v.hours_logged AS "Hours",
            TO_CHAR(v.visit_date, 'YYYY-MM-DD HH12:MI AM') AS "Date"
        FROM visits v
        JOIN users u ON v.user_id = u.id
        JOIN locations l ON v.location_id = l.id
        ORDER BY v.visit_date DESC
        LIMIT 10;
    """)
    
    rows = cur.fetchall()
    
    if rows:
        # Define column names based on the query above
        columns = ["User", "Account", "Action", "Location", "Hours", "Date"]
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity logged yet. Head to 'Log Activity' to record a visit!")

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database connection error: {e}")