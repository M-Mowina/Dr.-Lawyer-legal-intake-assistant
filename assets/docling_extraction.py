import os
import tempfile
from pathlib import Path
from typing import Optional
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
import time


def extract_context_from_docling(file_path: str, cache_enabled: bool = True) -> str:
    """
    Efficiently extracts text content from a given file using Docling with performance optimizations.
    
    Args:
        file_path (str): The path to the file.
        cache_enabled (bool): Whether to enable temporary caching for large files.

    Returns:
        str: The extracted text content, or an error message if extraction fails.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return f"Error: File does not exist: {file_path}"
        
    # Check file size to provide early warning for large files
    file_size = file_path.stat().st_size
    if file_size > 10 * 1024 * 1024:  # 10MB threshold
        print(f"Warning: File is large ({file_size / (1024*1024):.2f} MB), processing may take time...")
    
    try:
        # Configure pipeline with performance optimizations
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # Disable OCR for speed
        pipeline_options.do_table_structure = False  # Disable table structure if not needed
        
        # Configure the converter with optimized settings
        doc_converter = DocumentConverter(
            format_options={
                "pdf": PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        # Record start time
        start_time = time.time()
        
        # Convert document
        result = doc_converter.convert(str(file_path))
        
        # Calculate processing time
        end_time = time.time()
        print(f"Document conversion took {end_time - start_time:.2f} seconds")
        
        # Export to text instead of markdown for better performance if markdown isn't needed
        extracted_text = result.document.export_to_text()
        
        return extracted_text
        
    except Exception as e:
        return f"Error extracting content from {file_path}: {str(e)}"


def extract_context_from_file(file_path: str) -> str:
    """
    Backward compatible function that uses the optimized docling extraction.
    """
    return extract_context_from_docling(file_path, cache_enabled=False)


if __name__ == "__main__":
    print(extract_context_from_file("controllers/terms-and-conditions.pdf"))

