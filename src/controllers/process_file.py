from fastapi import HTTPException, UploadFile
import tempfile
import os
from pathlib import Path

def process_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """Process uploaded file and return extracted text and summary."""
    # Lazy import to avoid slow startup
    from controllers.document_parser import extract_text
    from controllers.summarizer import summarize_text
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix if file.filename else '.tmp') as temp_file:
        content = file.file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Extract text from file
        extracted_text = extract_text(temp_file_path)
        
        # Summarize the extracted text
        summary = summarize_text(extracted_text, style="detailed")
        
        return extracted_text, summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)