import streamlit as st
import pandas as pd
import io


def process_data(file):
    # Load the data from the uploaded Excel file
    df = pd.read_excel(file, sheet_name='Site Rollout Plan')

    # Process and calculate aging
    df['date'] = df['Updated Date'].str[4:10] + " " + df['Updated Date'].str[24:]
    df['date'] = pd.to_datetime(df['date'], format='%b %d %Y')
    df['formatted_date'] = df['date'].dt.strftime('%d/%m/%y')

    # Calculate the difference between consecutive start times for each ID
    df['Aging'] = (df.groupby('DU ID')['date'].shift(-1) - df['date']).dt.days
    df['Aging'] = abs(df['Aging'])

    # Replace NaN with 0 if the previous project is None
    df.loc[(df['Previous Value'].isna()) & (df['Aging'].isna()), 'Aging'] = 0

    # Replace NaN with "No value updated" if the current project is None
    df.loc[(df['New Value'].isna()), 'Aging'] = "No value updated"

    return df


# Streamlit App
st.title('Excel Aging Calculation')

# File upload
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    try:
        # Process the uploaded file
        st.write("Processing file...")
        processed_df = process_data(uploaded_file)

        # Display the processed DataFrame
        st.write("Processed Data:")
        st.dataframe(processed_df)

        # Convert DataFrame to Excel format for download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)

        # Provide download link
        st.download_button(
            label="Download Processed File",
            data=output,
            file_name="processed_aging.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.write("Please upload an Excel file to process.")
