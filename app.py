import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from PIL import Image

# Load CSV with cleaned format
@st.cache_data
def load_data():
    df = pd.read_csv("Contest_Rule.csv")
    df.fillna(method='ffill', inplace=True)  # fill down segment and code
    return df

df = load_data()

st.title("🏆 Leo Club Contest Points Calculator")

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

# 1. Select Segment
segments = df["Segment"].dropna().unique()
segment = st.selectbox("Select Segment", segments)

# 2. Select Code + Activity
activity_df = df[df["Segment"] == segment]
codes = activity_df["Code : Activity"].dropna().unique()
code = st.selectbox("Select Code and Activity", codes)

code_df = activity_df[activity_df["Code : Activity"] == code]

# 3. Sub-category (optional)
has_sub_categories = code_df["Sub-category"].notna().any()
selected_sub = None
selected_points = 0

if has_sub_categories and len(code_df) > 1:
    sub_options = code_df["Sub-category"].dropna().unique()
    selected_sub = st.selectbox("Select Sub-category", sub_options)
    sub_row = code_df[code_df["Sub-category"] == selected_sub].iloc[0]
    selected_points = sub_row["Points"]
else:
    selected_sub = code_df.iloc[0]["Code : Activity"]
    selected_points = code_df.iloc[0]["Points"]
    
# 6. Show allocated points as a note (help text)
st.text_input(
    "💡 Allocated Points for this Activity",
    value=f"{selected_points} points per unit",
    disabled=True,
    label_visibility="collapsed",
    placeholder="Points per activity will appear here"
)

# 6. Number of times activity was done
count = st.number_input("Enter how many times this activity was done", min_value=1, value=1)

# 7. Multiply for total
total_points = selected_points * count
st.markdown(f"**🧮 Points: {selected_points} × {count} = {total_points}**")

# 7. Add to table
if st.button("➕ Add to Activity Table"):
    st.session_state.activity_log.append({
        "Segment": segment,
        "Code": code,
        "Activity": selected_sub,
        "Points per Unit": selected_points,
        "Count": count,
        "Total Points": total_points
    })

# 8 & 9. Show table and total
# If there are activity logs to display
if st.session_state.activity_log:
    log_df = pd.DataFrame(st.session_state.activity_log)

    st.subheader("📋 Activity Summary Table")

    # Show deletable rows with checkboxes
    delete_indices = st.multiselect("🗑️ Select rows to delete", log_df.index, format_func=lambda i: f"{log_df.loc[i, 'Activity']} ({log_df.loc[i, 'Total Points']} pts)")
    
    if st.button("❌ Delete Selected"):
        st.session_state.activity_log = [row for idx, row in enumerate(st.session_state.activity_log) if idx not in delete_indices]
        st.rerun()

    # Show table
    st.dataframe(log_df)

    # Total points
    st.markdown(f"### 🔢 **Total Points: {log_df['Total Points'].sum()}**")

    # Download as image
    def df_to_image(df):
        fig, ax = plt.subplots(figsize=(10, len(df) * 0.6 + 1))
        ax.axis('off')
        ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        return buf

    img_buf = df_to_image(log_df)
    st.download_button("📥 Download Table as Image", data=img_buf, file_name="activity_log.png", mime="image/png")
