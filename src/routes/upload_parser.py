from fastapi import APIRouter, File, UploadFile
from fastapi import HTTPException
import tempfile
import os
from pathlib import Path

upload_router = APIRouter(prefix="/api/v1", tags=["test"])

@upload_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Lazy import to avoid slow startup
    from controllers import extract_text, summarize_text

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix if file.filename else '.tmp') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        result = extract_text(temp_file_path)
        summary = summarize_text(result, style = "detailed")
        return {"result": result, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
