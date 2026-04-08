import streamlit as st
import psycopg2

st.set_page_config(page_title="Log Activity", page_icon="✅")

def get_connection():
    return psycopg2.connect(st.secrets["DB_URL"])

st.title("✅ Log Activity or Check-In")

try:
    conn = get_connection()
    cur = conn.cursor()

    # Fetch dynamic data for dropdowns
    cur.execute("SELECT id, first_name || ' ' || last_name AS name FROM users ORDER BY last_name;")
    users = cur.fetchall()

    cur.execute("SELECT id, name FROM locations WHERE is_active = true ORDER BY name;")
    locations = cur.fetchall()

    if not users:
        st.warning("No users found. Please add a user in the directory first.")
    elif not locations:
        st.warning("No active locations found. Please add a location first.")
    else:
        user_dict = {u[1]: u[0] for u in users}
        location_dict = {l[1]: l[0] for l in locations}

        with st.form("log_visit_form"):
            selected_user = st.selectbox("Who are you?", options=user_dict.keys())
            selected_location = st.selectbox("Where are you?", options=location_dict.keys())
            
            visit_type = st.radio("What are you doing today?", ["Volunteered", "Received Resources"])
            
            st.write("*(Only required if volunteering)*")
            hours = st.number_input("Hours Logged", min_value=0.0, step=0.5, value=0.0)
            
            submitted = st.form_submit_button("Submit Visit")

            if submitted:
                # Validation
                if visit_type == "Volunteered" and hours <= 0:
                    st.error("⚠️ Please enter a valid number of hours greater than 0.")
                else:
                    user_id = user_dict[selected_user]
                    loc_id = location_dict[selected_location]
                    final_hours = hours if visit_type == "Volunteered" else None

                    # Insert the visit
                    cur.execute(
                        "INSERT INTO visits (user_id, location_id, visit_type, hours_logged) VALUES (%s, %s, %s, %s);",
                        (user_id, loc_id, visit_type, final_hours)
                    )
                    
                    # Gamification: Update user points if they volunteered (1 hr = 100 pts)
                    if visit_type == "Volunteered":
                        points_earned = int(hours * 100)
                        cur.execute(
                            "UPDATE users SET total_points = total_points + %s WHERE id = %s;",
                            (points_earned, user_id)
                        )
                        st.success(f"🎉 Success! You logged {hours} hours and earned {points_earned} points!")
                    else:
                        st.success("✅ Check-in successful. We're glad we could help today!")
                    
                    conn.commit()

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Database error: {e}")