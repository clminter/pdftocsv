import streamlit as st
import pandas as pd
from io import StringIO
from docx import Document
import base64
import camelot
import PyPDF2
import tempfile
import os

# set page to wide mode
st.set_page_config(layout="wide")

# Read and preprocess PDF documents
def read_pdf(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(file.getbuffer())
        tables = camelot.read_pdf(temp.name, pages='all', flavor='stream')
    os.remove(temp.name)  # clean up
    return tables

def read_txt(file):
    text = file.read()
    return text.decode()

def read_docx(file):
    document = Document(file)
    text = []
    for para in document.paragraphs:
        text.append(para.text)
    return "\n".join(text)

st.title('⏭️PDF of Estimate to CSV')
st.write("A MINTER 🤖")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        tables = read_pdf(uploaded_file)
        dataframes = []
        for i in range(len(tables)):
            # Clean data: remove dollar sign
            tables[i].df = tables[i].df.replace('\$', '', regex=True)
            dataframes.append(tables[i].df)
            st.write(f'Table {i+1}:')
            st.dataframe(tables[i].df)
            if st.sidebar.button(f'Download Table {i+1} as CSV'):
                csv = tables[i].df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="mydata.csv">Download csv file</a>'
                st.sidebar.markdown(href, unsafe_allow_html=True)
        if st.sidebar.button('Download All Tables as CSV'):
            combined_df = pd.concat(dataframes)
            csv = combined_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="mydata.csv">Download csv file</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)

    elif uploaded_file.type == "text/plain":
        text = read_txt(uploaded_file)
        lines = text.split("\n")
        df = pd.DataFrame(lines, columns=['Text'])
        df = df.replace('\$', '', regex=True)  # Clean data: remove dollar sign
        st.write(df)

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
        lines = text.split("\n")
        df = pd.DataFrame(lines, columns=['Text'])
        df = df.replace('\$', '', regex=True)  # Clean data: remove dollar sign
        st.write(df)
    else:
        st.sidebar.write("Unsupported file type")
