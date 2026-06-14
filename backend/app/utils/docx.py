import zipfile
import xml.etree.ElementTree as ET
import os

def parse_docx_text(file_path: str) -> str:
    """
    Parses a Microsoft Word .docx file and extracts all text paragraphs.
    Uses standard library zipfile and xml parsing to avoid external library reliance.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DOCX file not found at: {file_path}")
        
    namespace = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    p_tag = namespace + 'p'
    t_tag = namespace + 't'
    br_tag = namespace + 'br'
    
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
    except Exception as e:
        raise OSError(f"Failed to read/parse zip elements in DOCX file: {e}")

    body_tag = namespace + 'body'
    body = root.find(body_tag)
    if body is None:
        raise ValueError("Invalid document.xml: Could not find body tag.")
        
    paragraphs = []
    for elem in body.iter(p_tag):
        text_runs = []
        for child in elem.iter():
            if child.tag == t_tag:
                text_runs.append(child.text or '')
            elif child.tag == br_tag:
                text_runs.append('\n')
        text = ''.join(text_runs).strip()
        if text:
            paragraphs.append(text)
            
    return '\n\n'.join(paragraphs)

if __name__ == "__main__":
    # Test on the challenge JD doc
    default_jd_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/job_description.docx"))
    try:
        text = parse_docx_text(default_jd_path)
        print("Successfully parsed DOCX!")
        print(f"Total Character Count: {len(text)}")
        print("\nFirst 400 Characters:")
        print(text[:400] + "...")
    except Exception as e:
        print(f"Error: {e}")
