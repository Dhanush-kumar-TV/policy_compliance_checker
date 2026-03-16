import re
import datetime
from pydantic import BaseModel

class DocumentParserInput(BaseModel):
    raw_text: str
    document_id: str

class DocumentParserOutput(BaseModel):
    document_id: str
    sections: list[str]
    full_text: str
    word_count: int
    parsed_at: str

def parse_document(input_data: dict) -> dict:
    # We accept dict and validate with Pydantic, return dict
    parsed_input = DocumentParserInput(**input_data)
    
    text = parsed_input.raw_text
    
    # Extract sections assuming format "## Section Name"
    # Or fallback to looking for lines that might be headers
    sections = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('## '):
            sections.append(line[3:].strip())
        elif line.startswith('# '):
            sections.append(line[2:].strip())
            
    word_count = len(re.findall(r'\b\w+\b', text))
    parsed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    output = DocumentParserOutput(
        document_id=parsed_input.document_id,
        sections=sections,
        full_text=text,
        word_count=word_count,
        parsed_at=parsed_at
    )
    return output.model_dump()
