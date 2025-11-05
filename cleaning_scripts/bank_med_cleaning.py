import json

def clean_text(text):
    """
    Clean text by replacing special Unicode characters:
    - U+00A0 (non-breaking space) -> regular space
    - U+2019 (right single quotation mark) -> apostrophe
    - U+2013 (en dash) -> hyphen-minus
    """
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2019', "'")
    text = text.replace('\u2013', '-')
    return text.strip()

def organize_bankmed_faq(faq_file, output_file='m_by_bankmed_faq.json'):
    """
    Parse the m by Bankmed FAQ text file into structured JSON.
    Detects questions by '?' at the end of lines, and attaches the following lines as their answers.
    """
    with open(faq_file, 'r', encoding='utf-8') as f:
        lines = [clean_text(line) for line in f.readlines() if line.strip()]

    faq_json = {"m_by_Bankmed": []}
    current_question = None
    current_answer = []

    for line in lines:
        # If line looks like a question
        if line.endswith('?'):
            # Save previous question if exists
            if current_question and current_answer:
                faq_json["m_by_Bankmed"].append({
                    "question": current_question,
                    "answer": ' '.join(current_answer).strip()
                })
            # Start a new question
            current_question = line
            current_answer = []
        else:
            # Otherwise, treat as part of the answer
            if current_question:
                current_answer.append(line)

    # Save last question
    if current_question and current_answer:
        faq_json["m_by_Bankmed"].append({
            "question": current_question,
            "answer": ' '.join(current_answer).strip()
        })

    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(faq_json, f, indent=2, ensure_ascii=False)

    print(f"FAQ organized successfully! Output saved to: {output_file}")
    print(f"Total questions: {len(faq_json['m_by_Bankmed'])}")
    return faq_json


if __name__ == "__main__":
    faq_json = organize_bankmed_faq('data/Bankmed/bank_med_faqs.txt', 'data/Bankmed/m_by_bankmed_faq.json')

    print("\nSample output:")
    for i, qa in enumerate(faq_json["m_by_Bankmed"][:3]):
        print(f"Q{i+1}: {qa['question']}")
        print(f"A{i+1}: {qa['answer']}\n")
