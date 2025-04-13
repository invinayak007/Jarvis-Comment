import subprocess
import pdfcrowd
import os
import fitz

def write_to_pdf(pdf_str, file, use_pdfcrowd=False):
    client = pdfcrowd.HtmlToPdfClient('invinayak', 'c6d353864a8c5c6888cb4d7ea772a8e5')
        # run the conversion and write the result to a file
    client.setEnablePdfForms(True)
    client.convertStringToFile(pdf_str,file)


def split_pdf(input_path, output_prefix, page_numbers):
    pdf_document = fitz.open(input_path)
    print(page_numbers)
    for page_number in page_numbers:
        print(page_number)
        page_no = int(page_number)
        if 1 <= page_no  <= pdf_document.page_count:
            output_path = f"{output_prefix}_page_{page_no}.pdf"
            pdf_writer = fitz.open()

            pdf_writer.insert_pdf(pdf_document, from_page=page_no - 1, to_page=page_no - 1)

            pdf_writer.save(output_path)
            pdf_writer.close()
            print(f"Page {page_no} saved to {output_path}")
        else:
            print(f"Invalid page number: {page_no}. Skipping.")

    pdf_document.close()

def merge_pdfs(input_prefix, output_path,page_numbers):
    pdf_writer = fitz.open()

    for page_number in page_numbers:
        file_path = f"{input_prefix}_page_{page_number}.pdf"
        try:
            pdf_document = fitz.open(file_path)
            pdf_writer.insert_pdf(pdf_document)
            pdf_document.close()
            print(f"Merged {file_path}")
        except FileNotFoundError:
            break
        os.remove(file_path)

    pdf_writer.save(output_path)
    pdf_writer.close()
    print(f"Merged PDF saved to {output_path}")

def get_part_pdf(input_pdf_file, output_pdf_file, page_numbers_to_split):
    output_prefix = 'output'      # Replace with your desired output prefix
    split_pdf(input_pdf_file, output_prefix, page_numbers_to_split)
    merge_pdfs(output_prefix, output_pdf_file, page_numbers_to_split)
