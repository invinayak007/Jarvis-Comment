import streamlit as st
import base64
import os
import XMLHandler
import PDFHandler
import openai_impl
# File paths
TEST_PDF = "test.pdf"
NEW_PDF = "new.pdf"
xml_content = ''
st.title("📄 XML to PDF Viewer & Comments")

from lxml import etree

def validate_xml_syntax(xml_str):
    try:
        etree.fromstring(xml_str)
        return True, "XML is well-formed."
    except etree.XMLSyntaxError as e:
        return False, f"Syntax Error: {str(e)}"

# 1. Upload XML
xml_file = st.file_uploader("Upload XML", type="xml")
# Store session flags
if "pdf_shown" not in st.session_state:
    st.session_state.pdf_shown = None

if xml_file:
    xml_content = xml_file.read().decode("utf-8")
    XMLHandler.write_xmlcontent(xml_content,xml_file.name)
    st.text_area("XML Content", xml_content, height=200, disabled=True)

    # 2. Generate PDF button
    if st.button("Generate PDF"):
        # 🔧 You generate 'test.pdf' from xml_content
        json_content = XMLHandler.xml_to_json(xml_content)
        pdf_str = XMLHandler.json_to_pdf_string(json_content, [])
        PDFHandler.write_to_pdf(pdf_str, 'test.pdf', False)
        st.session_state.pdf_shown = TEST_PDF

# 3. Display PDF (test.pdf or new.pdf)
if st.session_state.pdf_shown and os.path.exists(st.session_state.pdf_shown):
    st.subheader("📄 PDF Preview")
    with open(st.session_state.pdf_shown, "rb") as f:
        pdf_data = f.read()
    '''
    try:
        b64 = base64.b64encode(pdf_data).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" width="1000" height="800" type="application/pdf"></iframe>',
            unsafe_allow_html=True
        )
    except Exception as e:
    '''
    st.error(f"Could not display PDF inline.")
    st.download_button("Download PDF", pdf_data, file_name="test.pdf", mime="application/pdf")

    # 4. Comment section
    comment = st.text_area("💬 Add your comment")
    if st.button("Submit Comment"):
        if comment.strip():
            # 🔧 You modify 'test.pdf' to 'new.pdf' here
            xml_content = XMLHandler.get_xml_content(xml_file.name)
            print('XML Content before->',xml_content)
            '''
            valid, message = validate_xml_syntax(xml_content)
            if not valid:
                print('XML is not valid')
                print(message)
                pass
            '''
            new_xml = openai_impl.modify_xml_with_llm(xml_content,comment)
            print('XML Content after->',new_xml)
            XMLHandler.write_xmlcontent(new_xml,xml_file.name)
            new_cont = XMLHandler.get_xml_content(xml_file.name)
            json_content1 = XMLHandler.xml_to_json(new_cont)
            pdf_str1 = XMLHandler.json_to_pdf_string(json_content1, [])
            PDFHandler.write_to_pdf(pdf_str1, 'new.pdf', False)
            if os.path.exists(NEW_PDF):
                #st.session_state.pdf_shown = NEW_PDF
                #st.success("Updated PDF displayed.")
                with open(st.session_state.pdf_shown, "rb") as f:
                    pdf_data1 = f.read()
                st.download_button("Download Updated PDF", pdf_data1, file_name="new.pdf", mime="application/pdf")
                st.experimental_rerun()
            else:
                st.error("Updated PDF (new.pdf) not found.")
