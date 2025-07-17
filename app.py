import streamlit as st
import pandas as pd

# Load CSV with cleaned format
@st.cache_data
def load_data():
    df = pd.read_csv("Contest_Rule.csv")
    df.fillna(method='ffill', inplace=True)  # fill down segment and code
    return df

df = load_data()

# Extract numeric value from Points (supports "per", "per member", etc.)
def extract_points(point_str):
    if pd.isna(point_str):
        return 0
    try:
        digits = ''.join(c for c in str(point_str) if c.isdigit())
        return int(digits) if digits else 0
    except:
        return 0

df["Numeric Points"] = df["Points"].apply(extract_points)

st.title("🏆 Leo Club Contest Points Calculator")

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

# 1. Select Segment
segments = df["Segment"].dropna().unique()
segment = st.selectbox("1️⃣ Select Segment", segments)

# 2. Select Code + Activity
activity_df = df[df["Segment"] == segment]
codes = activity_df["Code : Activity"].dropna().unique()
code = st.selectbox("2️⃣ Select Code and Activity", codes)

code_df = activity_df[activity_df["Code : Activity"] == code]

# 3. Sub-category (optional)
has_sub_categories = code_df["Sub-category"].notna().any()
selected_sub = None
selected_points = 0

if has_sub_categories and len(code_df) > 1:
    sub_options = code_df["Sub-category"].dropna().unique()
    selected_sub = st.selectbox("3️⃣ Select Sub-category", sub_options)
    sub_row = code_df[code_df["Sub-category"] == selected_sub].iloc[0]
    selected_points = sub_row["Numeric Points"]
else:
    selected_sub = code_df.iloc[0]["Code : Activity"]
    selected_points = code_df.iloc[0]["Numeric Points"]
    
# 6. Show allocated points as a note (help text)
st.text_input(
    "💡 Allocated Points for this Activity",
    value=f"{selected_points} points per unit",
    disabled=True,
    label_visibility="collapsed",
    placeholder="Points per activity will appear here"
)

# 6. Number of times activity was done
count = st.number_input("5️⃣ Enter how many times this activity was done", min_value=1, value=1)

# 7. Multiply for total
total_points = selected_points * count
st.markdown(f"**🧮 Points: {selected_points} × {count} = {total_points}**")

# 7. Add to table
if st.button("➕ Add to Activity Log"):
    st.session_state.activity_log.append({
        "Segment": segment,
        "Code": code,
        "Activity": selected_sub,
        "Points per Unit": selected_points,
        "Count": count,
        "Total Points": total_points
    })

# 8 & 9. Show table and total
if st.session_state.activity_log:
    log_df = pd.DataFrame(st.session_state.activity_log)
    st.subheader("📋 Activity Summary Table")
    st.dataframe(log_df)
    st.markdown(f"### 🔢 **Total Points: {log_df['Total Points'].sum()}**")
