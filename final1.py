import streamlit as st
import pandas as pd

# Load dataset
file_path = "your_file.csv"   # <-- replace with your dataset file path
df = pd.read_csv(r"C:\Users\DNYANDIP\Desktop\anjali\project.data.csv")

# Filter only Mumbai data
mumbai_data = df[df['City'].str.lower() == "mumbai"]

# Create layout
col1, col2, col3 = st.columns(3)

with col3:
    st.image(
        r"C:\Users\DNYANDIP\Desktop\anjali\WhatsApp Image 2025-09-04 at 03.39.56_19c731ae.jpg",
        use_column_width=True
    )
    st.caption("Mumbai, Maharashtra")

    if st.button("➡ Mumbai Data"):
        st.subheader("📊 Mumbai Noise Pollution Data")
        st.dataframe(mumbai_data)   # shows Mumbai dataset in an interactive table