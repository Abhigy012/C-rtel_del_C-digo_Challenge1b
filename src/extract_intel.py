import os
import json
import PyPDF2
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime
import numpy as np

def extract_pdf_text(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
    
    return text

def extract_sections_from_text(text, pdf_name):
    sections = []
    lines = text.split('\n')
    current_section = ""
    current_title = ""
    page_num = 1
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Estimate page breaks (very rough)
        if i > 0 and i % 50 == 0:  # Assume ~50 lines per page
            page_num += 1
        
        # Detect section headings
        is_heading = False
        if line and len(line) < 100:
            if (re.match(r'^\d+\.?\s+[A-Z]', line) or  # Numbered sections
                line.isupper() and len(line.split()) <= 8 or  # All caps
                (line[0].isupper() and len(line.split()) <= 6 and not line.endswith('.'))):
                is_heading = True
        
        if is_heading and current_section:
            # Save previous section
            sections.append({
                "document": pdf_name,
                "page": max(1, page_num - 1),
                "section_title": current_title,
                "content": current_section.strip()
            })
            current_section = ""
            current_title = line
        elif is_heading:
            current_title = line
        else:
            current_section += line + " "
    
    # Add final section
    if current_section:
        sections.append({
            "document": pdf_name,
            "page": page_num,
            "section_title": current_title or "Content",
            "content": current_section.strip()
        })
    
    return sections

def rank_sections_by_relevance(sections, persona, job_to_be_done):
    if not sections:
        return []
    
    # Combine persona and job for query
    query = persona + " " + job_to_be_done
    
    # Prepare texts for TF-IDF
    section_texts = [s["content"] for s in sections]
    all_texts = section_texts + [query]
    
    # Simple TF-IDF similarity
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Compute similarity between query and sections
        query_vector = tfidf_matrix[-1]
        section_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(query_vector, section_vectors)[0]
        
        # Add similarity scores and rank
        for i, section in enumerate(sections):
            section["relevance_score"] = float(similarities[i])
        
        # Sort by relevance
        sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Add importance rank
        for i, section in enumerate(sections):
            section["importance_rank"] = i + 1
            
    except Exception as e:
        print(f"Error in ranking: {e}")
        # Fallback - just number them
        for i, section in enumerate(sections):
            section["importance_rank"] = i + 1
            section["relevance_score"] = 0.5
    
    return sections

def extract_subsections(sections, persona, job_to_be_done):
    subsections = []
    
    for section in sections[:10]:  # Top 10 sections only
        content = section["content"]
        
        # Split content into smaller chunks
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk + sentence) < 200:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Take best chunks as subsections
        for i, chunk in enumerate(chunks[:3]):  # Max 3 subsections per section
            if len(chunk) > 50:  # Only meaningful chunks
                subsections.append({
                    "document": section["document"],
                    "page": section["page"],
                    "refined_text": chunk,
                    "relevance_score": section.get("relevance_score", 0.5) * (1.0 - i*0.1)
                })
    
    # Sort subsections by relevance
    subsections.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return subsections[:20]  # Top 20 subsections

def main():
    input_dir = "/app/input_1b"
    output_dir = "/app/output_1b"
    
    # Clean and create output directory
    if os.path.exists(output_dir):
        import shutil
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    print(f"=== ROUND 1B: PERSONA-DRIVEN INTELLIGENCE ===")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Output directory cleaned and ready for new results.")
    
    # Look for challenge1b_input.json file
    input_json_path = os.path.join(input_dir, "challenge1b_input.json")
    pdfs_dir = os.path.join(input_dir, "PDFs")
    
    if not os.path.exists(input_json_path):
        print("ERROR: challenge1b_input.json not found!")
        return
    
    if not os.path.exists(pdfs_dir):
        print("ERROR: PDFs directory not found!")
        return
    
    # Read input configuration
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            input_config = json.load(f)
    except Exception as e:
        print(f"Error reading input JSON: {e}")
        return
    
    # Extract configuration
    challenge_info = input_config.get("challenge_info", {})
    documents_info = input_config.get("documents", [])
    persona = input_config.get("persona", {}).get("role", "Analyst")
    job_to_be_done = input_config.get("job_to_be_done", {}).get("task", "Analyze documents")
    
    # Validate PDFs exist
    pdf_files = [doc["filename"] for doc in documents_info]
    existing_pdfs = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdfs_dir, pdf_file)
        if os.path.exists(pdf_path):
            existing_pdfs.append(pdf_file)
        else:
            print(f"Warning: {pdf_file} not found in PDFs directory")
    
    if not existing_pdfs:
        print("No PDF files found in PDFs directory!")
        return
    
    print(f"Processing {len(existing_pdfs)} PDFs...")
    print(f"Persona: {persona}")
    print(f"Job: {job_to_be_done}")
    
    # Extract sections from all PDFs
    all_sections = []
    
    for pdf_file in existing_pdfs:
        pdf_path = os.path.join(pdfs_dir, pdf_file)
        print(f"Processing {pdf_file}...")
        
        text = extract_pdf_text(pdf_path)
        sections = extract_sections_from_text(text, pdf_file)
        all_sections.extend(sections)
    
    print(f"Extracted {len(all_sections)} sections total")
    
    # Rank sections by relevance
    ranked_sections = rank_sections_by_relevance(all_sections, persona, job_to_be_done)
    
    # Extract subsections
    subsections = extract_subsections(ranked_sections, persona, job_to_be_done)
    
    # Prepare output in exact Challenge 1B format
    output = {
        "metadata": {
            "input_documents": existing_pdfs,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": s["importance_rank"],
                "page_number": s["page"]
            }
            for s in ranked_sections[:15]  # Top 15 sections
        ],
        "subsection_analysis": [
            {
                "document": s["document"],
                "refined_text": s["refined_text"],
                "page_number": s["page"]
            }
            for s in subsections
        ]
    }
    
    # Save output with Challenge 1B naming
    output_path = os.path.join(output_dir, "challenge1b_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"Saved challenge1b_output.json with {len(ranked_sections[:15])} sections and {len(subsections)} subsections")

if __name__ == "__main__":
    main()
