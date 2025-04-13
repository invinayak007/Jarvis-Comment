import json
import xml.etree.ElementTree as ET
import PDFHandler
import JSONHandler
import os
def get_xml_content(file):
    # Read the XML file
    print('In get XML content ->',file)
    with open(file, "r") as f:
        xml_content = f.read()
    return xml_content
def xml_to_json(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    json_content = None
    # Extract data from the XML into a Python dictionary
    study_data = {
        'Study': []
    }

    namespaces = {'ns': 'http://www.cdisc.org/ns/odm/v1.3'}

    for study in root.findall('.//ns:Study', namespaces=namespaces):
        study_dict = {
            'OID': study.attrib['OID'],
            'Forms': []
        }
        for form in study.findall('.//ns:FormDef', namespaces=namespaces):
            form_dict = {
                'FormOID': form.attrib['OID'],
                'FormName': form.attrib['Name'],
                'Repeating': form.attrib['Repeating'],
                'ItemGroups': []
            }
            item_group_refs = form.findall('.//ns:ItemGroupRef', namespaces=namespaces)
            print('item group refs->', item_group_refs)
            item_group_refs = sorted(item_group_refs, key=lambda x: int(x.attrib['OrderNumber']))
            for item_group_ref in item_group_refs:
                item_group_oid = item_group_ref.attrib['ItemGroupOID']
                item_group = study.find(f'.//ns:ItemGroupDef[@OID="{item_group_oid}"]', namespaces=namespaces)
                print('item group->',item_group.items())
                item_group_dict = {
                    'ItemGroupOID': item_group.attrib['OID'],
                    'ItemGroupName': item_group.attrib['Name'],
                    'Repeating': item_group.attrib['Repeating'],
                    'Items': []
                }

                item_refs = item_group.findall('.//ns:ItemRef', namespaces=namespaces)
                # Sort ItemRefs based on OrderNumber
                item_refs = sorted(item_refs, key=lambda x: int(x.attrib['OrderNumber']))

                for item_ref in item_refs:
                    item_oid = item_ref.attrib['ItemOID']
                    item = study.find(f'.//ns:ItemDef[@OID="{item_oid}"]', namespaces=namespaces)

                    if item is not None:
                        item_dict = {
                            'ItemOID': item.attrib['OID'],
                            'ItemName': item.attrib['Name'],
                            'DataType': item.attrib['DataType'],
                            'Length': item.attrib.get('Length', ''),
                            'Mandatory': item_ref.attrib.get('Mandatory', 'No'),
                            'QuestionText': item.find('.//ns:Question/ns:TranslatedText', namespaces=namespaces).text
                        }

                        # Extract code list if available
                        code_list_ref = item.find('.//ns:CodeListRef', namespaces=namespaces)
                        if code_list_ref is not None:
                            code_list_oid = code_list_ref.attrib['CodeListOID']
                            code_list = study.find(f'.//ns:CodeList[@OID="{code_list_oid}"]', namespaces=namespaces)
                            code_list_dict = {
                                'CodeListOID': code_list.attrib['OID'],
                                'CodeListName': code_list.attrib['Name'],
                                'CodedValues': []
                            }

                            for code_list_item in code_list.findall('.//ns:CodeListItem', namespaces=namespaces):
                                code_list_item_dict = {
                                    'CodedValue': code_list_item.attrib['CodedValue'],
                                    'CodedText': code_list_item.find('.//ns:Decode/ns:TranslatedText',
                                                                     namespaces=namespaces).text
                                }

                                code_list_dict['CodedValues'].append(code_list_item_dict)

                            item_dict['CodeList'] = code_list_dict

                        item_group_dict['Items'].append(item_dict)

                form_dict['ItemGroups'].append(item_group_dict)

            study_dict['Forms'].append(form_dict)

        study_data['Study'].append(study_dict)
        json_content = json.dumps(study_data, indent=4)
        return json_content
def json_to_pdf_string(json_content,visit_list):
    print(visit_list)
    head_flag = False
    html = "<html><head><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'></head><body>"
    data = json.loads(json_content)
    #print(data)
    #html += "<table border='1'><thead><tr><th>No</th><th>Title/Item</th><th>Input</th><th>Comments</th></tr></thead><tbody>"
     #Loop through studies
    for study in data['Study']:
        # Line1
        #html += f"<h2>{study['OID']} [Form present in Visit(s):{(', '.join(visit_list))}]</h2>"
        #html += f"<td width='10%'>{slno}.</td>"
        #html += f"<td width='40%'><h1>{study['OID']}</h1></td>"
        #html += f"<td width='30%'><h1>NA</h1></td>"
        #html += f"<td width='20%'><textarea rows='6' cols='20'></textarea><br></td><tr>"
        # Loop through forms in each study
        for form in study['Forms']:
            sl_no = 0
            forms_repeating = ''
            if form['Repeating'] == 'Yes':
                forms_repeating = '- Repeating'
            # Line2
            form_name = form['FormName']
            form_name = str(form_name).replace('-',' ')
            html += f"<h2>{form_name}</h2>"
            #html += f"<td width='10%'>{slno}.</td>"
            html += "<table width='100%' style='border:1px solid black;border-collapse: collapse;'>" \
                    "<thead><tr><th>  </th><th>~Form_Comments~</th></tr></thead><tbody>"
            html += f"<td width='80%'><h3>{form['FormName']} [{form['FormOID']}] {forms_repeating}" \
                    f"[Form present in Visit(s):{(', '.join(visit_list))}]</h3></td>"
            #html += f"<td width='30%'><h2>NA</h2></td>"
            html += "<td width='20%'><textarea rows='4' cols='20' placeholder='Add your comment here'></textarea><br></td><tr>"
            html += "</tbody></table>"
            # Create table
            #html += "<table border='1'><thead><tr><th>No</th><th>Question</th><th>InputField</th><th>Comments</th></tr></thead><tbody>"

            # Loop through item groups
            for item_group in form['ItemGroups']:
                in_repeat = False
                item_grp_repeating = ''
                if item_group['Repeating'] == 'Yes':
                    item_grp_repeating = '- Repeating'
                #html += f"<td width='10%'>{slno}.</td>"
                html += "<table width='100%' style='border:1px solid black;border-collapse: collapse;'>" \
                    "<thead><tr><th>  </th><th>~Group_Comments~</th></tr></thead><tbody>"
                html += f"<td width='80%'><h4>{item_group['ItemGroupName']} {item_grp_repeating}</h4></td>"
                #html += f"<td width='30%'><h3>NA</h3></td>"
                html += "<td width='20%'><textarea rows='4' cols='20' placeholder='Add your comment here'></textarea><br></td><tr>"
                html += "</tbody></table>"

                #html += f"<tr><td colspan='4'><h3>{item_group['ItemGroupName']} </h3></td></tr>"
                html += "<table width='100%' style='border:1px solid black;border-collapse: collapse;'><thead><tr><th>No</th><th>Question</th><th>InputField</th><th>Comments</th></tr></thead><tbody>"
                # Loop through items
                for idx, item in enumerate(item_group['Items']):
                    print(sl_no)
                    html += "<tr style='border:1px solid black; border-collapse: collapse;'>"
                    if item_group['Repeating'] == 'Yes':
                        if not in_repeat:
                            sl_no = sl_no + 1
                            dec_sl_no  = 1
                        else:
                            dec_sl_no = dec_sl_no + 1
                        in_repeat = True
                        str_sl = str(sl_no) + '.' + str(dec_sl_no)
                    else:
                        in_repeat = False
                        sl_no = sl_no + 1
                        str_sl = str(sl_no)+'.'
                    if item['Mandatory'] == 'Yes':
                        #idx_text = str(slno)+'.'+'&#9733 &#10003;'
                        idx_text = str_sl + '*' + '&#10003;'
                    else:
                        idx_text = str_sl
                    html += f"<td style='border:1px solid black;border-collapse: collapse;' width='10%'>{idx_text}</td>"
                    #print(item)
                    if len(form['FormOID']) == 2:
                        xml_form = form['FormOID']
                    else:
                        xml_form = form['FormName'][5:7]
                    html += f"<td style='border:1px solid black;border-collapse: collapse;' width='50%'>" \
                            f"<p style='color: white; font-size: 10px;'>{xml_form}</p>" \
                            f"{item['QuestionText']}<br/>[{item['ItemName']}]</td>"
                    # If 'CodeList' exists, create radio buttons, otherwise an input field
                    if "CodeList" in item:
                        html += "<td style='border:1px solid black;border-collapse: collapse;' width='30%'>"
                        for coded_value in item['CodeList']['CodedValues']:
                            html += f"<input type='radio' name='{item['ItemName']}' " \
                                    f"value='{coded_value['CodedValue']}' disabled>{coded_value['CodedText']} " \
                                    f"[{coded_value['CodedValue']}]<br>"
                        html += "</td>"
                    else:
                        length = item['Length']
                        dt = item['DataType']
                        filler = JSONHandler.get_filler_text(dt,length)
                        #print(filler)
                        if dt == 'date':
                            html += f"<td style='border:1px solid black;border-collapse: collapse;' width='30%'><input type='text' value='{filler}' readonly/>" \
                                    f"<span class='far fa-calendar-alt'></span><br>(2023-2030)</td>"
                        else:
                            html += f"<td style='border:1px solid black;border-collapse: collapse;' width='30%'><input type='text' value='{filler}' readonly/></td>"

                    html += "<td style='border:1px solid black;border-collapse: collapse;' width='20%'><textarea rows='3' cols='20'></textarea><br>"
                    if item['Mandatory'] == 'Yes':
                        html += "<input type='checkbox' id='man' value='Mandatory' checked />" \
                                "<label for='man'> Mandatory </label>" \
                                "<input type='checkbox' id='sdv' value='SDV' checked />" \
                                "<label for='sdv'> SDV </label><br>"
                    else:
                        html += "<input type='checkbox' id='man' value='Mandatory'/>" \
                            "<label for='man'> Mandatory </label>" \
                            "<input type='checkbox' id='sdv' value='SDV'/>" \
                            "<label for='sdv'> SDV </label><br>"
                    html += "</td></tr>"

            html += "</tbody></table>"
        html += "<table width='100%'><thead><tr><th>~General_Comments~</th></tr></thead>" \
                "<tbody><tr><td style='border:1px solid black;border-collapse: collapse;' width='100%'>" \
                "<textarea rows='3' style='width: 100%;'>Additional Comments</textarea>" \
                "</td></tr></tbody></table>"
    html += "</body></html>"

    return html
def xml_to_pdf(xml_file_list,xml_with_visits,pdf_file,path='xmls/',use_pdfcrowd=False):
    merged_pdf_str = ''
    print('File ->',xml_file_list)
    print('XML with visits->', xml_with_visits)
    for key, value in xml_with_visits.items():
        print('Key->',key,'Value->',value)
        print(merged_pdf_str)
        if os.path.exists(path+key):
            content = get_xml_content(path+key)
            json_content = xml_to_json(content)
            pdf_str = json_to_pdf_string(json_content,value)
            merged_pdf_str = str(merged_pdf_str) + str(pdf_str)
    PDFHandler.write_to_pdf(merged_pdf_str,pdf_file,use_pdfcrowd=use_pdfcrowd)

def write_xmlcontent(xml_content,file):
    # Read HTML from file
    print('In write XML content',file)
    with open(file, 'w') as f:
        f.write(xml_content)

