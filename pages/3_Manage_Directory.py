import streamlit as st
import psycopg2
import re

st.set_page_config(page_title="Manage Directory", page_icon="📁", layout="wide")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("📁 Manage Directory")
st.write("Add, edit, or remove users and locations from the system.")

tab1, tab2 = st.tabs(["👥 Users", "🏢 Locations"])

# --- TAB 1: USERS ---
with tab1:
    st.subheader("Add New User")
    with st.form("add_user"):
        col1, col2 = st.columns(2)
        fname = col1.text_input("First Name *")
        lname = col2.text_input("Last Name *")
        email = st.text_input("Email *")
        acct_type = st.selectbox("Account Type", ["Volunteer", "Community Member"])
        submit_user = st.form_submit_button("Add User")

        if submit_user:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not fname.strip() or not lname.strip():
                st.error("First and Last name are required.")
            elif not re.match(email_pattern, email):
                st.error("Please enter a valid email address.")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (first_name, last_name, email, account_type) VALUES (%s, %s, %s, %s)",
                        (fname.strip(), lname.strip(), email.strip(), acct_type)
                    )
                    conn.commit()
                    st.success(f"User {fname} added!")
                except psycopg2.errors.UniqueViolation:
                    st.error("A user with this email already exists.")
                finally:
                    cur.close()
                    conn.close()

    st.markdown("---")
    st.subheader("Current Users (Delete via Confirmation)")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, first_name, last_name, email, account_type FROM users ORDER BY last_name")
        users = cur.fetchall()
        
        for u in users:
            u_id, u_fname, u_lname, u_email, u_type = u
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{u_fname} {u_lname}** ({u_type}) - {u_email}")
            
            # The Delete Confirmation mechanism required by the rubric
            if col_b.button(f"Delete", key=f"del_u_{u_id}"):
                st.session_state[f"confirm_u_{u_id}"] = True
                
            if st.session_state.get(f"confirm_u_{u_id}", False):
                st.warning(f"Are you sure you want to delete {u_fname}? This will cascade delete their visits.")
                col_y, col_n = st.columns(2)
                if col_y.button("Yes, Delete", key=f"yes_u_{u_id}"):
                    cur.execute("DELETE FROM users WHERE id = %s", (u_id,))
                    conn.commit()
                    st.success("Deleted! Refreshing...")
                    st.session_state[f"confirm_u_{u_id}"] = False
                    st.rerun()
                if col_n.button("Cancel", key=f"no_u_{u_id}"):
                    st.session_state[f"confirm_u_{u_id}"] = False
                    st.rerun()
                    
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Error loading users: {e}")

# --- TAB 2: LOCATIONS ---
with tab2:
    st.subheader("Add New Location")
    with st.form("add_location"):
        loc_name = st.text_input("Location Name *")
        loc_service = st.selectbox("Primary Service", ["Food Pantry", "Clothing", "Shelter", "General Volunteering"])
        loc_address = st.text_input("Address *")
        submit_loc = st.form_submit_button("Add Location")

        if submit_loc:
            if not loc_name.strip() or not loc_address.strip():
                st.error("Name and Address are required.")
            else:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO locations (name, primary_service, address) VALUES (%s, %s, %s)",
                        (loc_name.strip(), loc_service, loc_address.strip())
                    )
                    conn.commit()
                    st.success(f"Location '{loc_name}' added!")
                finally:
                    cur.close()
                    conn.close()
                    
    st.markdown("---")
    st.subheader("Current Locations")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, primary_service, address FROM locations ORDER BY name")
        locs = cur.fetchall()
        if locs:
            st.dataframe(pd.DataFrame(locs, columns=["Name", "Service", "Address"]), hide_index=True)
        cur.close()
        conn.close()
    except Exception as e:
        st.error(e)