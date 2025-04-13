from openai import OpenAI  # or use Azure, Cohere, etc.
import streamlit as st
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"])


def clean_xml(received_string):
    xml_content = ''
    start_marker = "```xml\n"
    end_marker = "\n```"
    start_index = received_string.find(start_marker)
    if start_index != -1:
        start_index += len(start_marker)
        end_index = received_string.find(end_marker, start_index)
        if end_index != -1:
            xml_content = received_string[start_index:end_index].strip()
            #print(xml_content)
            # Now you can try to parse this xml_content
        else:
            print("End marker not found.")
    else:
        print("Start marker not found.")
    return xml_content


def modify_xml_with_llm(xml_str, comment):
    prompt = f"""You are an expert in CDASH (Clinical Data Acquisition Standards Harmonization) standards and XML editing.

Your task is to modify a CDASH-compliant XML file based on a specific instruction.

Please ensure the following:
- The modified XML must strictly conform to CDASH standards and XML schema.
- Do not alter any part of the XML that is not directly related to the instruction.
- Maintain all formatting, indentation, namespaces, and structural integrity.
- Do not add or remove any unrelated nodes or attributes.
- The output must be a valid XML string that can be parsed and validated against CDASH metadata models.
- Dont include some characters which might cause problem in XML. Ex: if you want to include '>' then add '&gt;'
- Validate that the XML should be valid, starting with <?xml and ending with </ODM> 

Instruction:
{comment}

Original XML:
{xml_str}

Return only the final modified XML.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an XML editing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content.strip()
    return clean_xml(content)


'''
original_xml = """
<invoice>
  <header>
    <date>2024-04-11</date>
    <customer>John Doe</customer>
  </header>
  <items>
    <item>
      <name>Widget A</name>
      <price>100</price>
    </item>
  </items>
  <status>pending</status>
</invoice>
"""

comment_instruction = "Remove the <header> section and change <status> to 'completed'."


modified_xml = modify_xml_with_llm(original_xml, comment_instruction)

print("🔧 Modified XML:\n")
#print(modified_xml)
'''
