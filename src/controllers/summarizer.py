import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for summarization
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="google/gemini-2.5-flash",
    temperature=0.0,
)


def create_summarization_prompt(style_instruction: str = "") -> str:
    """Create a prompt string for legal document summarization."""
    base_prompt = """You are an expert legal document summarizer. Your task is to create clear, concise summaries of legal documents while preserving all essential information.

Guidelines:
- Maintain the original meaning and legal context
- Preserve key facts, dates, parties involved, and legal terms
- Keep the summary professional and objective
- Highlight the main purpose and key provisions
- Remove redundant information while keeping critical details
- Format the summary in clear paragraphs

Focus on extracting:
1. Main subject/purpose of the document
2. Key parties involved
3. Important dates and deadlines
4. Critical terms and conditions
5. Rights and obligations of parties
6. Any penalties or consequences mentioned"""
    
    if style_instruction:
        base_prompt += f"\n\n{style_instruction}"
    
    return base_prompt + "\n\nPlease summarize the following legal document:\n\n{document_text}"


def summarize_text(
    text: str, 
    max_length: Optional[int] = None,
    style: str = "concise"
    ) -> str:
    """
    Summarize legal text using LLM.
    
    Args:
        text (str): The text to summarize
        max_length (int, optional): Maximum length of summary in words
        style (str): Summary style - "concise", "detailed", or "executive"
    
    Returns:
        str: The summarized text
    """
    if not text or not text.strip():
        return "No text provided for summarization."
    
    # Adjust prompt based on style
    style_prompts = {
        "concise": "Create a brief, focused summary (2-3 paragraphs).",
        "detailed": "Create a comprehensive summary covering all key points (4-6 paragraphs).",
        "executive": "Create a high-level executive summary highlighting only the most critical information (1-2 paragraphs)."
    }
    
    # Add style-specific instruction
    style_instruction = style_prompts.get(style, style_prompts["concise"])
    
    # Add length constraint if specified
    if max_length:
        style_instruction += f" Keep the summary under {max_length} words."
    
    # Create the prompt with style instruction
    prompt_template = create_summarization_prompt(style_instruction)
    
    # Format the prompt with the document text
    formatted_prompt = prompt_template.format(document_text=text)
    
    try:
        result = llm.invoke(formatted_prompt)
        return result.content.strip() if hasattr(result, 'content') else str(result).strip()
    except Exception as e:
        return f"Error summarizing text: {str(e)}"


def summarize_legal_document(
    text: str,
    document_type: str = "general",
    focus_areas: Optional[list] = None
    ) -> Dict[str, Any]:
    """
    Specialized summarization for legal documents with structured output.
    
    Args:
        text (str): The legal document text
        document_type (str): Type of legal document (contract, agreement, terms, etc.)
        focus_areas (list): Specific areas to focus on in the summary
    
    Returns:
        dict: Structured summary with key components
    """
    if not text or not text.strip():
        return {"error": "No text provided"}
    
    # Create a simple prompt string instead of ChatPromptTemplate to avoid variable parsing issues
    system_prompt = """You are an expert legal document analyzer. Create a structured summary of this legal document.

Provide your response in the following JSON format:
{{
    "document_type": "type of document identified",
    "parties_involved": ["party1", "party2", ...],
    "effective_date": "date if mentioned",
    "key_purpose": "main purpose of the document",
    "main_provisions": ["provision1", "provision2", ...],
    "key_terms": ["term1", "term2", ...],
    "obligations": ["obligation1", "obligation2", ...],
    "rights": ["right1", "right2", ...],
    "duration": "term/length if specified",
    "governing_law": "jurisdiction if mentioned",
    "summary": "comprehensive summary text"
}}"""
    
    user_prompt = "Analyze this legal document:\n\n{document_text}"
    
    # Combine prompts
    full_prompt = system_prompt + "\n\n" + user_prompt
    
    # Format the prompt with the document text
    formatted_prompt = full_prompt.format(document_text=text)
    
    try:
        result = llm.invoke(formatted_prompt)
        result_content = result.content if hasattr(result, 'content') else str(result)
        
        # Try to parse as JSON, fallback to text if parsing fails
        try:
            import json
            parsed_result = json.loads(result_content)
            return parsed_result
        except json.JSONDecodeError:
            return {"summary": result_content, "raw_response": result_content}
    except Exception as e:
        return {"error": f"Error analyzing document: {str(e)}"}


def chunk_text_for_summarization(text: str, max_chunk_size: int = 3000) -> list:
    """
    Split large text into chunks for better summarization.
    
    Args:
        text (str): Text to chunk
        max_chunk_size (int): Maximum size of each chunk in characters
    
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    sentences = text.split('. ')
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def summarize_long_document(
    text: str,
    chunk_size: int = 3000,
    final_summary_length: Optional[int] = 500
    ) -> str:
    """
    Summarize very long documents by chunking and then creating a final summary.
    
    Args:
        text (str): Long document text
        chunk_size (int): Size of chunks for initial summarization
        final_summary_length (int): Target length for final summary
    
    Returns:
        str: Final comprehensive summary
    """
    if not text or not text.strip():
        return "No text provided for summarization."
    
    # Split into chunks
    chunks = chunk_text_for_summarization(text, chunk_size)
    
    if len(chunks) == 1:
        return summarize_text(chunks[0], max_length=final_summary_length)
    
    # Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        chunk_summary = summarize_text(
            chunk, 
            style="concise",
            max_length=200
        )
        chunk_summaries.append(f"Section {i+1}: {chunk_summary}")
    
    # Combine chunk summaries
    combined_summary = "\n\n".join(chunk_summaries)
    
    # Create final summary
    final_prompt = f"Combine these section summaries into one coherent document summary:\n\n{combined_summary}"
    
    return summarize_text(
        final_prompt, 
        max_length=final_summary_length,
        style="executive"
    )


# Example usage functions
def get_available_styles() -> list:
    """Return list of available summarization styles."""
    return ["concise", "detailed", "executive"]


def get_document_types() -> list:
    """Return list of supported document types."""
    return ["contract", "agreement", "terms_and_conditions", "policy", "general"]


if __name__ == "__main__":
    # Test the summarization functionality
    sample_text = """
    THIS SOFTWARE LICENSE AGREEMENT is made and entered into as of January 1, 2024, by and between 
    TECH SOLUTIONS INC., a Delaware corporation with its principal place of business at 123 Tech Street, 
    San Francisco, CA 94105 ("Licensor"), and CLIENT COMPANY LLC, a California limited liability company 
    with its principal place of business at 456 Business Ave, Los Angeles, CA 90001 ("Licensee").
    
    WHEREAS, Licensor has developed certain proprietary software; and
    WHEREAS, Licensee desires to obtain a license to use such software;
    
    NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:
    
    1. GRANT OF LICENSE. Licensor hereby grants to Licensee a non-exclusive, non-transferable license 
    to use the Software for internal business purposes only.
    
    2. TERM. This Agreement shall commence on the Effective Date and continue for a period of two (2) years, 
    unless terminated earlier in accordance with Section 6.
    
    3. FEES. Licensee shall pay Licensor a license fee of $50,000 annually, payable in advance on the 
    first day of each calendar year during the Term.
    
    4. CONFIDENTIALITY. Each party agrees to maintain in confidence any proprietary information 
    disclosed by the other party.
    
    5. WARRANTIES. Licensor warrants that the Software will perform substantially in accordance with 
    the documentation for a period of ninety (90) days following delivery.
    
    6. TERMINATION. This Agreement may be terminated by either party upon thirty (30) days' written 
    notice if the other party materially breaches this Agreement.
    
    IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.
    """
    
    print("=== Concise Summary ===")
    print(summarize_text(sample_text, style="concise"))
    print("\n=== Detailed Summary ===")
    print(summarize_text(sample_text, style="detailed"))
    print("\n=== Structured Analysis ===")
    print(summarize_legal_document(sample_text))