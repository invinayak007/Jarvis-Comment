import json
def get_filler_text(dt,length):
    if length == '' or length is None:
        length = 2
    if dt == 'date':
        return 'DD-MON-YYYY'
    if dt == 'time':
        return 'Time'
    if dt == 'datetime':
        return 'DateTime'
    if dt == 'text':
        return 'A'+str(length)
    if dt == 'integer':
        return 'X'*int(length)
    if dt == 'float':
        return 'X'*int(length)+'.'
def json_to_pdf_string_xml(json_content):
    html = "<html><head><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'></head><body>"
    data = json.loads(json_content)
    for study in data['Study']:
        # Line1
        # Loop through forms in each study
        for form in study['Forms']:
            sl_no = 0
            forms_repeating = ''
            if form['Repeating'] == 'Yes':
                forms_repeating = '- Repeating'
            # Line2
            html += f"<h3>{form['FormName']}  {forms_repeating}</h3>"
            # Loop through item groups
            for item_group in form['ItemGroups']:
                in_repeat = False
                item_grp_repeating = ''
                if item_group['Repeating'] == 'Yes':
                    item_grp_repeating = '- Repeating'
                html += f"<h4>{item_group['ItemGroupName']} {item_grp_repeating}</h4>"
                html += "<table width='100%' style='border:1px solid black;border-collapse: collapse;'><thead><tr><th>No</th><th>Question</th><th>InputField</th></tr></thead><tbody>"
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
                    html += f"<td style='border:1px solid black;border-collapse: collapse;' width='15%'>{idx_text}</td>"
                    #print(item)
                    html += f"<td style='border:1px solid black;border-collapse: collapse;' width='50%'>" \
                            f"<p style='color: white; font-size: 10px;'>{form['FormOID']}</p>" \
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
                        filler = get_filler_text(dt,length)
                        #print(filler)
                        if dt == 'date':
                            html += f"<td style='border:1px solid black;border-collapse: collapse;' width='35%'><input type='text' value='{filler}' readonly/>" \
                                    f"<span class='far fa-calendar-alt'></span><br>(2023-2030)</td>"
                        else:
                            html += f"<td style='border:1px solid black;border-collapse: collapse;' width='30%'><input type='text' value='{filler}' readonly/></td>"

                    #html += "<td style='border:1px solid black;border-collapse: collapse;' width='20%'><textarea rows='3' cols='20'></textarea><br>"
                    '''
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
                    '''
            html += "</tr></tbody></table>"

    html += "</body></html>"

    return html