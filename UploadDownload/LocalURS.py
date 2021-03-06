import tkinter as tk
from tkinter import filedialog
from xlsxwriter.workbook import Workbook
from tika import parser
import codecs
print("imports done")
root = tk.Tk()  # tkinter to find file
root.withdraw()
file_path = filedialog.askopenfilename()  # dialog box to navigate to file
file_ext = file_path[file_path.rfind(".") + 1:]  # find the filename extension
i=1
while i >0:
   j=i
   i=file_path.rfind("\\")

file_name=file_path[j + 1:file_path.rfind(".")]
if file_ext.lower().find("pdf") == 0:  # if extension starts with "pdf"
    doc_type = "pdf"
elif file_ext.find("doc") == 0:  # if extension starts with "doc"
    doc_type = "doc"
else:  # neither a pdf nor a doc file
    doc_type = "xxx"
    print("Unrecognized document format. Program designed for PDF or DOCX.")
    quit()

raw = parser.from_file(file_path)  # raw content from the file (stored as a list)
nice_text = str(raw)  # convert that raw content into one long string
print("nice_text done")
nice_text = nice_text.replace("\\uf0b7", "\u2022")  # bullets misrepresented, not sure why
# nice_text=nice_text.replace(" \\","\\")

# iterate over (i, 0) to enter text lines
lineitems_array = [""] * len(nice_text)  # create an array/list to store the line items
k = 0  # current position in lineitems array/list
unicode_to_keep = []
unicode_to_keep.append("2019")  # apostrophe
unicode_to_keep.append("0027")  # apostrophe
unicode_to_keep.append("201c") #quotes
unicode_to_keep.append("201d")  # quotes

for j in range(len(nice_text)):  # for each letter position in the long string of content
    lineitems_array[k] += nice_text[j]  # add the letter/character to current line item
    if j < (len(nice_text) - 3):  # required to stay in the index range (looking 3 letters ahead for PDFs)
        if nice_text[j + 1] == "\\":  # if next letter is a backslash
            if nice_text[j + 2] == "n" or nice_text[j + 2] == "t":  # \n = new line ... \t = new table entry
                if file_ext.upper().find("PDF") > -1:  # because every line on a PDF registers as a new line "\n"
                    new_line = False
                    if nice_text[j + 3].isnumeric():  # first character of new line is a number
                        new_line = True  # Likely to be a new numbered item
                    elif (nice_text[j + 3].isupper() and nice_text[j + 4] == "."):  # capital letter followed by "."
                        new_line = True  # likely to be a new lettered item
                    elif nice_text[j + 3] == "\\" and nice_text[j + 4] == "n":
                        new_line = True
                    if new_line:  # something indicates a new line should start
                        k += 1  # new array/list item
                        j += 2  # skip past the new line ("\n")
                elif file_ext.upper().find("DOC") > -1:  # only actual new lines register as new lines "\n"
                    k += 1  # new array/list item
                    j += 2  # skip past the new line ("\n")
                else:
                    k += 1
                    j += 2
            elif nice_text[j + 2] == "u":
                k += 1
        elif nice_text[j].isnumeric():
            if nice_text[j - 3] == "." and nice_text[j - 4] == "." and nice_text[j - 5] == ".":
                if not nice_text[j + 1].isnumeric():
                    k += 1
        elif nice_text[j] == " ":
            if nice_text[j + 1].isupper() and not nice_text[j + 1].isnumeric():
                if nice_text[j + 2] == "." and nice_text[j + 3] == " ":
                    k += 1
            else:
                try:
                    if str(codecs.encode(nice_text[j + 1], 'unicode_escape')).find("\\u") > -1:  # unicode (bullet?)
                        for item in unicode_to_keep:
                            if str(codecs.encode(nice_text[j + 1], 'unicode_escape')).find(item) > -1:
                                break
                        else:
                            k += 1  # new array/list item
                except Exception:  # required
                    pass
        else:
            try:
                if str(codecs.encode(nice_text[j + 1], 'unicode_escape')).find("\\u") > -1:  # unicode (bullet?)
                    for item in unicode_to_keep:
                        if str(codecs.encode(nice_text[j + 1], 'unicode_escape')).find(item) > -1:
                            break
                    else:
                        k += 1  # new array/list item
            except Exception:  # required
                pass

for i in range(len(lineitems_array) - 1):  # for every line item
    lineitems_array[i] = str(lineitems_array[i]).replace("\\n", "").strip()  # remove line breaks
    lineitems_array[i] = str(lineitems_array[i]).replace("\\t", "").strip()  # remove table breaks
    if str(lineitems_array[i]).find("\\u") > -1:
        lineitems_array[i] = codecs.decode(lineitems_array[i], 'unicode-escape')

for i in range(len(lineitems_array) - 1, 0, -1):
    if lineitems_array[i].upper().find("METADATA") > -1:
        lineitems_array[i] = " "
    elif lineitems_array[i].upper().find("PAGE") > -1:
        if len(lineitems_array[i]) > 10:
            tmp_str = lineitems_array[i][:10].upper()
            if tmp_str.find("PAGE") == 0:  # "page" is after 10 or more characters
                tmp_str = tmp_str.replace("OF", " ")
                for k in range(4, len(tmp_str)):
                    if not tmp_str[k].isnumeric() and tmp_str[k] != " ":
                        break
                else:
                    lineitems_array[i] = " "
        else:
            lineitems_array[i] = " "
    elif lineitems_array.count(lineitems_array[i]) > 1:
        lineitems_array[i] = " "

lineitems_array = list(filter(lambda x: len(x) > 3, lineitems_array))  # remove line items with 3 or fewer char's

content_array = lineitems_array
last_sec = ""
cap_secs = False
not_all_caps = False
test_num = int(len(lineitems_array) / 7)
for i in range(7):
    if not lineitems_array[test_num * (i)].isupper():
        not_all_caps = True
section_name_array = [""] * len(lineitems_array)
section_num_array = [""] * len(lineitems_array)

for i in range(len(lineitems_array) - 1):
    toc_bullets = False
    if lineitems_array[i].find(".....") > 0:
        toc_bullets = True
    try:
        if codecs.encode(lineitems_array[i], 'unicode_escape').find("\\u") == 0:
            toc_bullets = True
    except Exception:
        pass
    new_sec = False
    if toc_bullets:  # tab of cont / bullts
        section_num_array[i] = ""
        content_array[i] = lineitems_array[i]
    elif 0 <= lineitems_array[i].find(".") < 5:  # Period in first few characters
        new_sec = True  # section number/letter followed by period (maybe)
    elif 0 <= lineitems_array[i].find(":") < 5:  # colon in first few characters
        new_sec = True  # section number/letter followed by period (maybe)
    elif lineitems_array[i][0].isnumeric():  # first character is a number
        if lineitems_array[i][1] == " " or lineitems_array[i][1] == ".":  # number is followed by space or "."
            new_sec = True
    else:  # no section designation
        section_num_array[i] = ""
        content_array[i] = lineitems_array[i]
    if new_sec:
        let_num = 0
        let_desc = ""
        while let_desc != " " and let_num < len(lineitems_array[i]):
            let_desc = lineitems_array[i][let_num]
            let_num += 1
        section_num_array[i] = lineitems_array[i][:let_num].strip()
        content_array[i] = lineitems_array[i][let_num:].strip()
        if cap_secs:
            if content_array[i].isupper():
                last_sec = content_array[i]
            elif len(content_array[i].split()) > 1:
                number_and_section = False
                if content_array[i][0].isnumeric():
                    for k in range(len(content_array[i].split()) - 1):
                        if content_array[i].split()[k].isupper():
                            number_and_section = True
                if content_array[i].split()[0].isupper() or number_and_section:
                    k = 0
                    if content_array[i].split()[0].isnumeric():
                        while not content_array[i].split()[k].isupper():
                            k += 1
                    tmp_sec = ""
                    while content_array[i].split()[k].isupper():
                        tmp_sec += content_array[i].split()[k] + " "
                        k += 1
                    if len(tmp_sec.strip()) > 1:  # to avoid having "A" as a section
                        last_sec = tmp_sec
        else:
            if not_all_caps:
                if len(content_array[i].split()) == 1:
                    if not any(let.isnumeric() for let in content_array[i]):
                        last_sec = content_array[i]
                        if last_sec == last_sec.upper():
                            cap_secs = True
                else:
                    if len(content_array[i].split()) > 0:
                        if content_array[i].split()[0].isupper() or content_array[i].split()[0].isnumeric():
                            for k in range(len(content_array[i].split()) - 1):
                                if content_array[i].split()[k].islower():
                                    break
                                elif content_array[i].split()[k].isupper():
                                    cap_secs = True
                                    last_sec = content_array[i].split()[k]
                                    break
            else:  # document is all caps
                if len(content_array[i].split()) == 1:
                    last_sec = content_array[i].split()[0]
    section_name_array[i] = last_sec

xlfile = Workbook(r'C:\users\englandt\desktop\URS_Converted.xlsx')
xlsheet = xlfile.add_worksheet()  # add sheet
xlsheet.hide_gridlines(2)
sheet_format = xlfile.add_format()
sheet_format.set_border()
sheet_format.set_align("vcenter")
section_format = xlfile.add_format()
section_format.set_align("center")
section_format.set_align("vcenter")
section_format.set_text_wrap()
section_format.set_border()
title_format = xlfile.add_format()
title_format.set_border()
title_format.set_align("vcenter")
title_format.set_bold()
marker_format = xlfile.add_format()
marker_format.set_border()
marker_format.set_align("vcenter")
marker_format.set_align("center")
marker_format.set_bold()
lineitem_format = xlfile.add_format()
lineitem_format.set_border()
lineitem_format.set_align("vcenter")
lineitem_format.set_text_wrap()
note_format = xlfile.add_format()
note_format.set_align("vcenter")
note_format.set_text_wrap()
note_format.set_border()
note_head_format = xlfile.add_format()
note_head_format.set_bold()
note_head_format.set_align("center")
note_head_format.set_align("vcenter")
note_head_format.set_border()

max_rows = len(lineitems_array)

for i in range(len(lineitems_array)):  # for all line items
    xlsheet.write(i, 0, section_num_array[i])
    xlsheet.write(i, 1, section_name_array[i])
    xlsheet.write(i, 2, content_array[i])

xlsheet.set_column(0, 1, None, section_format)
xlsheet.set_column(1, 1, 30, section_format, {'hidden': True})
xlsheet.set_column(2, 2, 100, lineitem_format)
xlsheet.set_column(3, 5, None, marker_format)
xlsheet.set_column(6, 7, 40, note_format)

xlsheet.merge_range('A1:C1', "URS Converted", title_format)
xlsheet.write(0, 3, "Accept")
xlsheet.write(0, 4, "Reject")
xlsheet.write(0, 5, "Quotable")
xlsheet.write(0, 6, "PSA Notes", note_head_format)
xlsheet.write(0, 7, "Customer Notes", note_head_format)

red_format = xlfile.add_format({'bg_color': '#FFC7CE',
                                'font_color': '#9C0006'})
yell_format = xlfile.add_format({'bg_color': '#FFEB9C',
                                 'font_color': '#9C6500'})
green_format = xlfile.add_format({'bg_color': '#C6EFCE',
                                  'font_color': '#006100'})
xlsheet.conditional_format('D2:D' + str(max_rows + 50), {'type': 'cell',
                                                         'criteria': 'greater than',
                                                         'value': 0,
                                                         'format': green_format})
xlsheet.conditional_format('E2:E' + str(max_rows + 50), {'type': 'cell',
                                                         'criteria': 'greater than',
                                                         'value': 0,
                                                         'format': red_format})
xlsheet.conditional_format('F2:F' + str(max_rows + 50), {'type': 'cell',
                                                         'criteria': 'greater than',
                                                         'value': 0,
                                                         'format': yell_format})

xlsheet.freeze_panes(1, 0)
print ("100%")
xlfile.close()