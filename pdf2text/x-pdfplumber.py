import re
from typing import Dict, List, Optional
import pdfplumber
from dataclasses import dataclass

@dataclass
class MonitorSection:
    title: str
    content: str
    level: int
    section_number: Optional[str] = None

class MonitorOfficialExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.sections: List[MonitorSection] = []
        
    def extract(self) -> Dict:
        """Main extraction method that processes the PDF and returns structured content"""
        with pdfplumber.open(self.pdf_path) as pdf:
            # Extract basic metadata
            first_page = pdf.pages[0]
            metadata = self._extract_metadata(first_page)
            
            # Extract full text while preserving some formatting
            full_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                full_text.append(page_text)
            
            self.text = "\n".join(full_text)
            
            # Extract structured sections
            self._parse_sections()
            
            return {
                "metadata": metadata,
                "sections": self.sections,
                "full_text": self.text
            }
    
    def _extract_metadata(self, first_page) -> Dict:
        """Extract metadata from first page"""
        text = first_page.extract_text()
        
        # Extract document number using regex
        number_match = re.search(r"Nr\.\s*(\d+)", text)
        number = number_match.group(1) if number_match else None
        
        # Extract date
        date_pattern = r"(\d{1,2}\s+[a-zA-Z]+\s+\d{4})"
        date_match = re.search(date_pattern, text)
        date = date_match.group(1) if date_match else None
        
        # Extract year
        year_match = re.search(r"Anul\s+(\d+)", text)
        year = year_match.group(1) if year_match else None
        
        return {
            "number": number,
            "date": date,
            "year": year
        }
    
    def _parse_sections(self):
        """Parse the text into structured sections"""
        # Split on major section headers
        section_pattern = r"([A-Z\s]{5,})\n"
        potential_sections = re.split(section_pattern, self.text)
        
        current_level = 0
        for i in range(1, len(potential_sections), 2):
            title = potential_sections[i].strip()
            content = potential_sections[i+1].strip() if i+1 < len(potential_sections) else ""
            
            # Extract section number if present
            section_number = None
            number_match = re.match(r"(\d+\.|\w+\.)\s+", content)
            if number_match:
                section_number = number_match.group(1)
                content = content[len(number_match.group(0)):].strip()
            
            # Determine section level based on formatting
            if title.isupper() and len(title) > 20:
                level = 1
            elif title.isupper():
                level = 2
            else:
                level = 3
                
            section = MonitorSection(
                title=title,
                content=content,
                level=level,
                section_number=section_number
            )
            self.sections.append(section)
    
    def get_hierarchical_structure(self) -> Dict:
        """Returns the document structure as a nested dictionary"""
        structure = {}
        current_path = []
        
        for section in self.sections:
            while len(current_path) >= section.level:
                current_path.pop()
            
            current_path.append(section.title)
            
            # Build nested dict path
            current_dict = structure
            for path_part in current_path[:-1]:
                if path_part not in current_dict:
                    current_dict[path_part] = {}
                current_dict = current_dict[path_part]
            
            current_dict[current_path[-1]] = section.content
            
        return structure

def main(pdf_path: str):
    extractor = MonitorOfficialExtractor(pdf_path)
    result = extractor.extract()
    
    # Print structured output
    print(f"Document Number: {result['metadata']['number']}")
    print(f"Date: {result['metadata']['date']}")
    print("\nDocument Structure:")
    
    for section in result['sections']:
        indent = "  " * (section.level - 1)
        print(f"{indent}{section.title}")
        if section.section_number:
            print(f"{indent}Section number: {section.section_number}")
        if len(section.content) > 100:
            print(f"{indent}Content preview: {section.content[:100]}...")
        else:
            print(f"{indent}Content: {section.content}")
        print()

if __name__ == "__main__":
    # Example usage
    pdf_path = "../../../datadata/mo/_obsolete/small size samples/Monitorul-Oficial--PI--1039--2024.pdf"
    main(pdf_path)