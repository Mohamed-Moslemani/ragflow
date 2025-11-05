import json

def clean_text(text):
    """
    Clean text by replacing special Unicode characters:
    - U+00A0 (non-breaking space) -> regular space
    - U+2019 (right single quotation mark) -> U+0027 (apostrophe)
    - U+2013 (en dash) -> U+002D (hyphen-minus)
    """
    text = text.replace('\u00a0', ' ')  # Non-breaking space to regular space
    text = text.replace('\u2019', '\u0027')  # Right single quote to apostrophe
    text = text.replace('\u2013', '\u002d')  # En dash to hyphen-minus
    return text

def read_keywords(keywords_file):
    """Read keywords from the keywords file."""
    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = [clean_text(line.strip()) for line in f.readlines() if line.strip()]
    return keywords

def organize_faq_by_keywords(faq_file, keywords_file, output_file='faq_organized.json'):
    """
    Read FAQ text file and organize questions under keyword categories.
    When a line matches a keyword, it becomes the main branch.
    Questions following that keyword are added to that branch until the next keyword.
    """
    # Read keywords
    keywords = read_keywords(keywords_file)
    
    # Read FAQ file
    with open(faq_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Initialize the JSON structure
    faq_json = {}
    current_category = None
    current_question = None
    current_answer = []
    
    for line in lines:
        line = clean_text(line.strip())
        
        # Skip empty lines
        if not line:
            # If we have a current question and answer, save it
            if current_question and current_answer:
                if current_category:
                    if current_category not in faq_json:
                        faq_json[current_category] = []
                    faq_json[current_category].append({
                        "question": current_question,
                        "answer": ' '.join(current_answer).strip()
                    })
                current_question = None
                current_answer = []
            continue
        
        # Check if line is a keyword (main branch)
        if line in keywords:
            # Save previous question if exists
            if current_question and current_answer:
                if current_category:
                    if current_category not in faq_json:
                        faq_json[current_category] = []
                    faq_json[current_category].append({
                        "question": current_question,
                        "answer": ' '.join(current_answer).strip()
                    })
            
            # Start new category
            current_category = line
            if current_category not in faq_json:
                faq_json[current_category] = []
            current_question = None
            current_answer = []
        
        # Check if line ends with '?' - it's likely a question
        elif line.endswith('?'):
            # Save previous question if exists
            if current_question and current_answer:
                if current_category:
                    faq_json[current_category].append({
                        "question": current_question,
                        "answer": ' '.join(current_answer).strip()
                    })
            
            # Start new question
            current_question = line
            current_answer = []
        
        # Otherwise, it's part of an answer
        else:
            if current_question:
                current_answer.append(line)
    
    # Don't forget to add the last question
    if current_question and current_answer and current_category:
        faq_json[current_category].append({
            "question": current_question,
            "answer": ' '.join(current_answer).strip()
        })
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(faq_json, f, indent=2, ensure_ascii=False)
    
    print(f"FAQ organized successfully! Output saved to: {output_file}")
    print(f"Total categories: {len(faq_json)}")
    for category, questions in faq_json.items():
        print(f"  - {category}: {len(questions)} questions")
    
    return faq_json

if __name__ == "__main__":
    # Process the FAQ file
    faq_json = organize_faq_by_keywords(
        'bank_of_beirut_faq.txt',
        'bank_of_beirut_faq_keywords.txt',
        'bank_of_beirut_faq_organized.json'
    )
    
    # Print a sample
    print("\nSample output:")
    for category in list(faq_json.keys())[:2]:
        print(f"\n{category}:")
        for i, qa in enumerate(faq_json[category][:2]):
            print(f"  Q{i+1}: {qa['question']}")
            print(f"  A{i+1}: {qa['answer'][:100]}..." if len(qa['answer']) > 100 else f"  A{i+1}: {qa['answer']}")
        