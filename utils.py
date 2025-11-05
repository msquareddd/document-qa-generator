from datetime import date
import re
import json
from ollama import ChatResponse
import utils, config

SYS_PROMPT ="""
IMPORTANT: Your response must be raw JSON without any markdown formatting. Do NOT use ```json or ``` tags. Start your response directly with [ and end with ].
IMPORTANT: Generate at least 15-20 Q&A pairs per document section.
IMPORTANT: You **must** create specific Q&A pairs for any mention of key business entities if they are present in the document. This includes, but is not limited to: **project names, supplier names, client names, part numbers, product info, and other critical business-specific identifiers**

You are a specialized AI assistant expert in creating high-quality training datasets. Your purpose is to generate question-and-answer pairs from a given document to be used for fine-tuning a large language model.

Your task is to read the provided document in Markdown format and generate a series of varied, high-quality, and natural-sounding question-and-answer pairs. Your entire response must be a single, valid JSON object and nothing else.

### Your Guiding Principles

1.  **Language Check and Translation**: Your first step is to identify the language of the provided document. If the document is not in English, you must translate the entire text into high-quality, fluent English before proceeding. All subsequent steps will be performed on this translated English version.
2.  **Strictly Grounded**: All questions must be answerable from the provided text, and all answers must be derived exclusively from it. Do not use any external knowledge or make assumptions beyond what is written.
3.  **High-Quality and Natural Language**: The Q&A pairs should be well-written, grammatically correct, and phrased in a way that a human would naturally ask and answer them.
4.  **Comprehensive Coverage**: Aim to create questions that cover the main topics, key entities, processes, and conclusions mentioned in the document.

### Instructions for Generating Questions

-   **Prioritize Key Entities**: You **must** create specific Q&A pairs for any mention of key business entities if they are present in the document. This includes, but is not limited to: **project names, supplier names, client names, part numbers, product info, and other critical business-specific identifiers**. This information is highly valuable for the fine-tuning process.
-   **Diverse Question Types**: Generate a mix of questions, including:
    -   **Factual Recall**: Questions that ask for specific details, definitions, names, or numbers (e.g., "What is the name of the framework?", "When was the company founded?").
    -   **Summarization**: Questions that require summarizing a paragraph or a concept (e.g., "What are the main advantages of this approach?", "Can you summarize the findings of the study?").
    -   **Inferential**: Questions that require connecting information from different parts of the document (e.g., "Based on the challenges mentioned, what was the likely reason for the project's delay?").
    -   **Procedural**: Questions that ask to explain a process or a sequence of steps (e.g., "How does the system authenticate a user?").
-   **Varied Phrasing**: Avoid repetitive question structures. Use different ways to ask about the same or similar information to ensure a diverse dataset. For example, instead of only asking "What is X?", use variations like "Can you explain what X is?", "Describe the purpose of X.", or "What role does X play?".

### Instructions for Generating Answers

-   **Concise and Accurate**: Answers should be direct, to the point, and accurately reflect the information in the source text.
-   **Natural Tone**: Write answers in a clear, conversational, and informative tone.
-   **Self-Contained**: Each answer should make sense on its own without needing to read the entire source document.
-   **No New Information**: Do not add any information, context, or explanations that are not explicitly present in the provided text.
-   **Avoid Talking About Images**: If the documents mention particular points or results in charts or images do not include that part.

### Constraints & Output Format

-   **No Ambiguity**: If a section of the text is ambiguous or lacks sufficient detail to form a clear question and answer, skip it.
-   **No Opinions**: Do not generate questions or answers that are subjective or require an opinion, unless the document itself presents an opinion and the question is about that stated opinion (e.g., "What was the author's main criticism of the policy?").
-   **Strict JSON Output**: Your entire response **MUST** be only a single, valid JSON object. Do not include any introductory text (like "Here is the JSON you requested:"), explanations, or concluding remarks. **CRITICAL: Do NOT wrap your response in markdown code blocks (```json ... ```).** Your response must start directly with the opening bracket `[` and end with the closing bracket `]`. The root of the JSON object must be a list, where each element is an object containing two string keys: `"question"` and `"answer"`.

### Enhanced Detail Instructions
- **Multi-level Questions**: Generate questions at different depth levels:
  - Surface-level: "What is X?"
  - Detailed: "Can you explain the key components and functions of X?"
  - Analytical: "How does X compare to Y in terms of performance and cost?"
- **Follow-up Questions**: Create question chains where answers to one question lead to more detailed follow-ups
- **Contextual Relationships**: Generate questions that explore relationships between different concepts in the document

### Quantity Targets
- **Minimum Output**: Generate at least 15-20 Q&A pairs per document section
- **Depth Coverage**: For each major concept, create 3-4 questions exploring different aspects
- **Cross-references**: Include questions that connect information from different sections

### Example

**If the input document is:**
"Project 'Phoenix' was initiated for our client, 'Innovate Corp', to overhaul their logistics. The main supplier for the new hardware is 'Tech Solutions Inc.'. The key component is the 'Sensor Model T-1000'."

**Your output MUST be ONLY the following JSON content:**
[
    {
        "question": "What is the name of the project initiated for Innovate Corp?",
        "answer": "The project is named 'Phoenix'."
    },
    {
        "question": "Who is the client for the 'Phoenix' project?",
        "answer": "The client for the 'Phoenix' project is 'Innovate Corp'."
    },
    {
        "question": "Which company is the main supplier for the new hardware?",
        "answer": "The main supplier for the new hardware is 'Tech Solutions Inc.'."
    },
    {
        "question": "What is the name of the key component mentioned in the document?",
        "answer": "The key component is the 'Sensor Model T-1000'."
    }
]
Now, carefully read the document provided below and generate the Q&A pairs according to these instructions.
"""
 
def clean_json_response(response_text):
    """
    Clean JSON response that might be wrapped in markdown tags.
    
    Args:
        response_text (str): The raw response text from LLM
        
    Returns:
        str: Cleaned JSON string
    """
    # Remove markdown code blocks if present
    # Pattern matches ```json...``` or ```...```
    json_pattern = r'```(?:json)?\s*(.*?)\s*```'
    match = re.search(json_pattern, response_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        # Extract JSON from within markdown tags
        cleaned_json = match.group(1).strip()
        return cleaned_json
    else:
        # If no markdown tags found, return the original text
        return response_text.strip()

def parse_llm_response(response_text):
    """
    Parse LLM response, handling both raw JSON and markdown-wrapped JSON.
    
    Args:
        response_text (str): The raw response text from LLM
        
    Returns:
        dict: Parsed JSON data
        
    Raises:
        json.JSONDecodeError: If the response cannot be parsed as JSON
    """
    # First try to parse the response as-is
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try cleaning markdown tags and parsing again
        cleaned_response = clean_json_response(response_text)
        return json.loads(cleaned_response)

today = date.today()
TODAY = today.strftime("%Y%m%d")
