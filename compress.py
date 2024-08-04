import os
from pypdf import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO

input_folder = 'input'
output_folder = 'output'

def compress_pdf(input_path, output_path, image_quality=90):
    pdf_reader = PdfReader(input_path)
    pdf_writer = PdfWriter()
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)
        
        try:
            xObject = page['/Resources']['/XObject'].get_object()
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj].get_data()
                    
                    img = Image.open(BytesIO(data))
                    img = img.convert("RGB")
                    
                    output = BytesIO()
                    img.save(output, format="JPEG", quality=image_quality)
                    output.seek(0)
                    
                    new_data = output.read()
                    
                    xObject[obj]._data = new_data
        except Exception as e:
            print(f"An error occurred while processing images on page {page_num+1}: {e}")
            pass
    
    # メタデータを削除
    pdf_writer.remove_metadata()
    
    with open(output_path, 'wb') as f:
        pdf_writer.write(f)

def process_directory(input_dir, output_dir, image_quality=90):
    for root, dirs, files in os.walk(input_dir):
        relative_path = os.path.relpath(root, input_dir)
        output_root = os.path.join(output_dir, relative_path)
        
        if not os.path.exists(output_root):
            os.makedirs(output_root)
        
        for file in files:
            if file.endswith('.pdf'):
                input_path = os.path.join(root, file)
                output_path = os.path.join(output_root, file)
                
                compress_pdf(input_path, output_path, image_quality=image_quality)

process_directory(input_folder, output_folder, image_quality=90)
print("PDF compression completed.")