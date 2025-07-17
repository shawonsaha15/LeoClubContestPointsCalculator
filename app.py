import streamlit as st
import pandas as pd

# Load CSV data
@st.cache_data
def load_data():
    df = pd.read_csv("Contest Rule.csv")
    df.fillna(method='ffill', inplace=True)  # Forward fill to group sub-activities
    return df

df = load_data()

# Parse numeric points from "Points" column
def extract_point_value(point_str):
    if pd.isna(point_str):
        return 0
    try:
        num = ''.join(c for c in str(point_str) if c.isdigit())
        return int(num) if num else 0
    except:
        return 0

df["Numeric Points"] = df["Points"].apply(extract_point_value)

st.title("🏆 Contest Points Calculator (CSV-based)")

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

# 1. Select Segment
segments = df["Segment"].dropna().unique()
segment = st.selectbox("1️⃣ Select Segment", segments)

# 2. Select Code
filtered_df = df[df["Segment"] == segment]
codes = filtered_df["Code"].dropna().unique()
code = st.selectbox("2️⃣ Select Code", codes)

# 3. Select Activity (Category)
code_df = filtered_df[filtered_df["Code"] == code]
activities = code_df["Activity"].dropna().unique()
activity = st.selectbox("3️⃣ Select Activity", activities)

# 4. Get numeric points
row = code_df[code_df["Activity"] == activity].iloc[0]
points = row["Numeric Points"]

# 5. Number of times activity was done
count = st.number_input("5️⃣ How many times was this activity done?", min_value=1, value=1)

# 6. Calculate total
total_points = points * count
st.write(f"**Points: {points} × {count} = {total_points}**")

# 7. Add to table
if st.button("➕ Add to Activity List"):
    st.session_state.activity_log.append({
        "Segment": segment,
        "Code": code,
        "Activity": activity,
        "Points per Activity": points,
        "Count": count,
        "Total Points": total_points
    })

# 8–9. Show table + total
if st.session_state.activity_log:
    log_df = pd.DataFrame(st.session_state.activity_log)
    st.subheader("🧾 Activity Log")
    st.dataframe(log_df)
    st.markdown(f"### 🔢 Total Points: **{log_df['Total Points'].sum()}**")
