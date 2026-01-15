"""
Project: Relational Microblogging & Analytics Platform (Streamlit App with SQL Backend)
Author: Muhtasim Fuad Chowdhury
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
from datetime import datetime
from contextlib import closing
from pathlib import Path
import bcrypt

# ************
# Connect SQL
# ************
def connect():
    return sqlite3.connect("database.db", check_same_thread=False)

def run_query(sql_query, params=()):
    with closing(connect()) as conn:
        return pd.read_sql_query(sql_query, conn, params=params)

def run_exec(sql_query, params=()):
    with closing(connect()) as conn:
        conn.execute(sql_query, params)
        conn.commit()


# *******
# Checks
# *******
def user_exists(usr: str) -> bool:
    with closing(connect()) as conn:
        return conn.execute("SELECT 1 FROM users WHERE usr = ?", (usr,)).fetchone() is not None

def email_exists(email: str) -> bool:
    with closing(connect()) as conn:
        return conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone() is not None

def hash_pwd(pwd: str) -> str:
    hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_pwd(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode("utf-8"), hashed.encode("utf-8"))

def check_credentials(usr: str, pwd: str) -> bool:
    with closing(connect()) as conn:
        row = conn.execute("SELECT pwd_hash FROM users WHERE usr = ?", (usr,)).fetchone()
        if row is None:
            return False
        return verify_pwd(pwd, row[0])

def follow_exists(follower, followee) -> bool:
    with closing(connect()) as conn:
        return conn.execute("SELECT 1 FROM follows WHERE follower_usr = ? AND followee_usr = ?", (follower, followee),).fetchone() is not None

def blocked_exists(blocker: str, blocked: str) -> bool:
    with closing(connect()) as conn:
        return conn.execute("SELECT 1 FROM blocks WHERE blocker_usr = ? AND blocked_usr = ?", (blocker, blocked),).fetchone() is not None

# ******
# Title
# ******
st.set_page_config(page_title="Fuad's MAP", layout="wide")
st.title("🎩 Fuad’s Microblogging & Analytics Platform")

if "user" not in st.session_state:
    st.session_state.user = None # Manage user session

if "confirm_logout" not in st.session_state:
    st.session_state.confirm_logout = False # Manage logout


# *********************
# Sign In/Sign Up Page
# *********************
def show_auth_page():
    st.subheader("Welcome! Sign in or create an account below.")

    tab1, tab2 = st.tabs(["🔒 Sign in", "🆕 Sign up"])

    with tab1:
        usr = st.text_input("User ID", key="signin_usr")
        pwd = st.text_input("Password", type="password", key="signin_pwd")
        
        # Checks
        if st.button("Sign in"):
            if not usr or not pwd:
                st.error("Please fill in both fields.")
            elif check_credentials(usr.strip(), pwd):
                st.session_state.user = usr.strip()
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    with tab2:
        name = st.text_input("Name", key="new_usr_name")
        email = st.text_input("Email", key="new_usr_email").strip().lower()
        phone = st.text_input("Phone number", key="new_usr_phone")
        pwd = st.text_input("Password", type="password", key="new_usr_password")
        c_pwd = st.text_input("Confirm password", type="password", key="new_usr_c_password")
        usr = st.text_input("Choose User ID", key="new_user_ID")

        # Checks
        if st.button("Sign up"):
            email_regex = r"^[a-z0-9]+[\._]?[a-z0-9]+@[\w\-]+\.\w+$"

            if not name:
                st.error("Name cannot be empty.")

            elif not re.match(email_regex, email):
                st.error("Invalid email format.")
            elif email_exists(email):
                st.error("You already have an account with this email.")

            elif not phone.isdigit():
                st.error("Phone number must be numeric.")

            elif not pwd:
                st.error("Password cannot be empty.")
            elif pwd != c_pwd:
                st.error("Passwords do not match.")

            elif not usr:
                st.error("User ID cannot be empty.")
            elif user_exists(usr):
                st.error("User ID already taken. Please choose another one.")

            else:
                pwd_hash = hash_pwd(pwd)
                run_exec(
                    "INSERT INTO users (usr, name, email, phone, pwd_hash) VALUES (?, ?, ?, ?, ?)",
                    (usr, name, email, phone, pwd_hash),
                )
                st.session_state.user = usr.strip()
                st.rerun()


# ********************
# USER DASHBOARD MENU
# ********************
def user_menu():
    st.sidebar.header(f"User: {st.session_state.user}")
    st.sidebar.markdown("---")

    option = st.sidebar.radio(
        "Navigation",
        [
            "Home / Feed",
            "Compose Post",
            "All Users",
            "Following List",
            "Followers List",
            "App Analysis"
        ],
        key='nav_choice'
    )

    if option == "Home / Feed":
        show_feed()
    elif option == "Compose Post":
        post()
    elif option == "All Users":
        show_all_users()
    elif option == "Following List":
        show_following()
    elif option == "Followers List":
        show_followers()
    elif option == "App Analysis":
        show_analysis()

    st.sidebar.markdown("---")

    # Logout Feature
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.confirm_logout = True

    if st.session_state.confirm_logout:
        st.sidebar.warning("Are you sure you want to log out?")
        yes, no = st.sidebar.columns(2)
        with yes:
            if st.button("Yes", key="logout"):
                st.session_state.user = None
                st.session_state.confirm_logout = False
                st.rerun()
        with no:
            if st.button("No", key="logout_no"):
                st.session_state.confirm_logout = False
                st.rerun()
        
    
# ************
# Home / Feed
# ************
def show_feed():
    st.subheader("Your Feed")

    st.markdown("---")

    # Display User Analytics KPIs
    col1, col2, col3 = st.columns(3)

    user_posts = run_query("SELECT COUNT(*) AS count FROM posts WHERE author_usr = ?", (st.session_state.user,))["count"][0]
    user_following = run_query("SELECT COUNT(*) AS count FROM follows WHERE follower_usr = ?", (st.session_state.user,))["count"][0]
    user_followers = run_query("SELECT COUNT(*) AS count FROM follows WHERE followee_usr = ?", (st.session_state.user,))["count"][0]

    col1.metric("My Posts", user_posts)
    col2.metric("Following", user_following)
    col3.metric("Followers", user_followers)

    st.markdown("---")

    # Display Followers Posts
    sql_query = """
        SELECT p.author_usr, u.name, p.content, p.created_at
        FROM posts p
        JOIN follows f ON f.followee_usr = p.author_usr
        JOIN users   u ON u.usr = p.author_usr
        WHERE f.follower_usr = ?
          AND NOT EXISTS (
                SELECT 1 FROM blocks b
                WHERE b.blocker_usr = p.author_usr
                  AND b.blocked_usr = ?
          ) 
          AND NOT EXISTS (
                SELECT 1 FROM blocks b2
                WHERE b2.blocker_usr = ?
                  AND b2.blocked_usr = p.author_usr
          ) -- I blocked author
        ORDER BY datetime(p.created_at) DESC
    """
    posts = run_query(sql_query, (st.session_state.user, st.session_state.user, st.session_state.user)) # st.session_state.user called thrice as blocker and blocked checked

    if posts.empty:
        st.info("No posts in your feed yet.")
    else:
        for _, row in posts.iterrows():
            st.markdown(
                f"""
                <div class="post-card">
                    <strong>{row['name']} (@{row['author_usr']})</strong><br>
                    <small>{row['created_at']}</small>
                    <p>{row['content']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("---")


# *************
# COMPOSE POST
# *************
def post():
    st.subheader("Compose a new post")
    content = st.text_area("Write your post (max 360 characters)", max_chars=360)

    if st.button("Post"):
        if not content.strip():
            st.warning("Post cannot be empty.")
        else:
            run_exec(
                "INSERT INTO posts (author_usr, content, created_at) VALUES (?, ?, datetime('now'))",
                (st.session_state.user, content.strip()),
            )
            st.success("Posted! Your followers will see it in their feed.")

    # Engagement: Top 5 Most Active Users of the App
    st.markdown("### Top 5 Most Active Users")

    top_users = run_query("""
        SELECT u.usr, COUNT(p.id) AS post_count
        FROM users u
        LEFT JOIN posts p ON p.author_usr = u.usr
        GROUP BY u.usr
        ORDER BY post_count DESC
        LIMIT 5
    """)

    st.dataframe(top_users, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("### My Posts")

    my_posts = run_query(
        """
        SELECT id, content, created_at
        FROM posts
        WHERE author_usr = ?
        ORDER BY datetime(created_at) DESC
        """,
        (st.session_state.user,)
    )

    if my_posts.empty:
        st.info("You haven't posted anything yet.")
    else:
        for _, row in my_posts.iterrows():
            st.markdown(
                f"""
                <div class="post-card">
                    <small>{row['created_at']}</small>
                    <p>{row['content']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Delete button (unique per post)
            if st.button("Delete", key=f"delete_post_{row['id']}"):
                run_exec(
                    """
                    DELETE FROM posts
                    WHERE id = ? AND author_usr = ?
                    """,
                    (row["id"], st.session_state.user),
                )
                st.success("Post deleted.")
                st.rerun()

            st.markdown("---")


# **********
# ALL USERS
# **********
def show_all_users():
    st.subheader("All Users")

    df = run_query("SELECT usr, name, email FROM users ORDER BY LOWER(name), email")

    if df.empty:
        st.info("No users found.")
        return

    st.dataframe(df.rename(columns={"usr": "User ID", "name": "Name", "email": "Email"}),
        use_container_width=True, 
        hide_index=True
    )

    # Follow a user
    st.markdown("### Follow a user")
    follow_target = st.text_input("Enter User ID to follow")

    if st.button("Follow"):
        if follow_target == st.session_state.user:
            st.error("You cannot follow yourself.")
        elif not user_exists(follow_target):
            st.error("User does not exist.")
        elif follow_exists(st.session_state.user, follow_target):
            st.error("You already follow this user.")
        elif blocked_exists(follow_target, st.session_state.user):
            st.error("You are blocked by this user.")
        elif blocked_exists(st.session_state.user, follow_target):
            st.error("You have blocked this user. Unblock them if you want to follow the user.")
        else:
            run_exec(
                "INSERT INTO follows (follower_usr, followee_usr, created_at) VALUES (?, ?, datetime('now'))",
                (st.session_state.user, follow_target),
            )
            st.success(f"You are now following {follow_target}!")


# ***************
# FOLLOWING LIST
# ***************
def show_following():
    st.subheader("Your Following")

    sql_query = """
        SELECT u.usr, u.name, u.email
        FROM follows f
        JOIN users u ON u.usr = f.followee_usr
        WHERE f.follower_usr = ?
        ORDER BY LOWER(u.name), u.usr
    """
    df = run_query(sql_query, (st.session_state.user,))

    if df.empty:
        st.info("You’re not following anyone yet.")
        return

    st.dataframe(df.rename(columns={"usr": "User ID", "name": "Name", "email": "Email"}),
        use_container_width=True, 
        hide_index=True
    )

    # Unfollow a user
    st.markdown("### Unfollow a user")
    unfollow_target = st.text_input("Enter User ID to unfollow")

    if st.button("Unfollow"):
        target = unfollow_target.strip()
        if not target:
            st.error("Please enter a User ID.")
        elif target == st.session_state.user:
            st.error("You cannot unfollow yourself.")
        elif not user_exists(target):
            st.error("User does not exist.")
        elif not follow_exists(st.session_state.user, target):
            st.error("You don’t follow this user.")
        else:
            run_exec(
                "DELETE FROM follows WHERE follower_usr = ? AND followee_usr = ?",
                (st.session_state.user, target),
            )
            st.success(f"You unfollowed {target}.")
            st.rerun()


# **************
# FOLLOWER LIST
# **************
def show_followers():
    st.subheader("Your Followers")

    sql_query = """
        SELECT u.usr, u.name, u.email
        FROM follows f
        JOIN users u ON u.usr = f.follower_usr
        WHERE f.followee_usr = ?
        ORDER BY LOWER(u.name), u.usr
    """

    df = run_query(sql_query, (st.session_state.user,))

    if df.empty:
        st.info("You have no followers yet.")
        return

    st.dataframe(df.rename(columns={"usr": "User ID", "name": "Name", "email": "Email"}),
        use_container_width=True, 
        hide_index=True
    )

    # Block a follower
    st.markdown("### Block a follower")
    block_target = st.text_input("Enter follower User ID to block")

    if st.button("Block"):
        target = (block_target or "").strip()
        if not target:
            st.error("Please enter a User ID.")
        elif target == st.session_state.user:
            st.error("You cannot block yourself.")
        elif not user_exists(target):
            st.error("User does not exist. (This is case-sensitive. Please enter exact User ID.)")
        else:
            # Ensure they are actually your follower
            is_follower = run_query(
                "SELECT 1 FROM follows WHERE follower_usr = ? AND followee_usr = ?",
                (target, st.session_state.user),
            )
            if is_follower.empty:
                st.error(f"{target} is not currently your follower.")
            else:
                run_exec(
                    "INSERT INTO blocks (blocker_usr, blocked_usr, created_at) VALUES (?, ?, datetime('now'))",
                    (st.session_state.user, target),
                )
                run_exec(
                    "DELETE FROM follows WHERE follower_usr = ? AND followee_usr = ?",
                    (target, st.session_state.user),
                )
                st.success(f"Blocked {target}. They can’t follow you or see your posts.")
                st.rerun()


# *************
# App Analysis
# *************
def show_analysis():
    st.subheader("App Analysis")

    col1, col2, col3 = st.columns(3)

    # App Analytics KPI metrics
    total_users = run_query("SELECT COUNT(*) AS count FROM users")["count"][0]
    total_posts = run_query("SELECT COUNT(*) AS count FROM posts")["count"][0]
    total_follows = run_query("SELECT COUNT(*) AS count FROM follows")["count"][0]

    col1.metric("Total Users", total_users)
    col2.metric("Total Posts", total_posts)
    col3.metric("Total Follows", total_follows)

    st.markdown("---")

    # Engagement: Followers per User
    st.markdown("### Followers per User")

    followers_df = run_query("""
        SELECT u.usr, COUNT(f.follower_usr) AS followers
        FROM users u
        LEFT JOIN follows f ON f.followee_usr = u.usr
        GROUP BY u.usr
        ORDER BY followers DESC
    """)

    st.bar_chart(
        followers_df.set_index("usr")
    )

    st.markdown("---")

    # Time-series: Posts over time (per minute)
    st.markdown("### Posts Over Time")

    posts_over_time = run_query("""
        SELECT 
            strftime('%Y-%m-%d %H:%M', created_at) AS time,
            COUNT(*) AS post_count
        FROM posts
        WHERE created_at IS NOT NULL 
            AND created_at >= datetime('now', '-60 minutes')
        GROUP BY time
        ORDER BY time;
    """)

    if posts_over_time.empty:
        st.info("Not enough data to display post activity over time.")
    else:
        posts_over_time["time"] = pd.to_datetime(posts_over_time["time"], errors="coerce")

        posts_over_time = posts_over_time.dropna()
        
        st.line_chart(posts_over_time.set_index("time"))

    # I use minute-level aggregation for demos and day-level aggregation for long-term trend analysis
    # Time-series: Posts over time (per day)
    # st.markdown("### Posts Over Time") 
    # posts_over_time = run_query(""" 
    #     SELECT 
    #         date(created_at) AS post_date, 
    #         COUNT(*) AS post_count 
    #     FROM posts 
    #     GROUP BY date(created_at) 
    #     ORDER BY post_date 
    # """) 
    
    # if posts_over_time.empty: 
    #     st.info("Not enough data to display post activity over time.") 
    # else: 
    #     posts_over_time["post_date"] = pd.to_datetime(posts_over_time["post_date"]) 
        
    # st.line_chart(posts_over_time.set_index("post_date"))


# ***********
# APP ROUTER
# ***********
if st.session_state.user:
    user_menu()
else:
    show_auth_page()
