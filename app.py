import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Comparator", layout="wide")

st.title("📊 Confronto e Unione File Excel")

# Upload file
file1 = st.file_uploader("Carica il primo file Excel", type=["xlsx"])
file2 = st.file_uploader("Carica il secondo file Excel", type=["xlsx"])

if file1 and file2:
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    st.subheader("Anteprima file 1")
    st.dataframe(df1)

    st.subheader("Anteprima file 2")
    st.dataframe(df2)

    st.divider()

    # Colonne comuni
    common_cols = list(set(df1.columns).intersection(set(df2.columns)))

    if common_cols:
        key_col = st.selectbox("🔑 Colonna chiave per confronto", common_cols)

        # Merge
        merged_df = pd.merge(
            df1,
            df2,
            on=key_col,
            how="outer",
            indicator=True,
            suffixes=('_file1', '_file2')
        )

        st.subheader("🔍 Confronto dati")
        st.dataframe(merged_df)

        # Differenze
        st.subheader("⚠️ Differenze")
        diff = merged_df[merged_df["_merge"] != "both"]
        st.dataframe(diff)

        # Filtri
        st.subheader("🔎 Filtri")

        filter_col = st.selectbox("Colonna", merged_df.columns)
        unique_vals = merged_df[filter_col].dropna().unique()

        selected_vals = st.multiselect("Valori", unique_vals)

        filtered_df = merged_df
        if selected_vals:
            filtered_df = merged_df[merged_df[filter_col].isin(selected_vals)]

        st.dataframe(filtered_df)

        # Group by
        st.subheader("📊 Raggruppamento")

        numeric_cols = filtered_df.select_dtypes(include='number').columns

        if len(numeric_cols) > 0:
            group_col = st.selectbox("Raggruppa per", filtered_df.columns)
            agg_col = st.selectbox("Aggrega", numeric_cols)

            grouped = filtered_df.groupby(group_col)[agg_col].sum().reset_index()

            st.dataframe(grouped)
            st.bar_chart(grouped.set_index(group_col))

        # Pulizia
        st.subheader("🧹 Pulizia dati")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Rimuovi duplicati"):
                filtered_df = filtered_df.drop_duplicates()
                st.success("Duplicati rimossi")
                st.dataframe(filtered_df)

        with col2:
            if st.button("Rimuovi null"):
                filtered_df = filtered_df.dropna()
                st.success("Null rimossi")
                st.dataframe(filtered_df)

        # Download
        st.subheader("⬇️ Download")

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Scarica CSV",
            csv,
            "risultato.csv",
            "text/csv"
        )

    else:
        st.error("❌ Nessuna colonna in comune tra i file")
