# Document Processor for Q&A Generation

A Python application that processes documents (DOCX, PPTX, PDF, TXT, MD) and generates question-answer pairs using local LLM models via Ollama. The generated Q&A pairs are saved in JSON format, suitable for training or fine-tuning language models.

## Features

- Convert various document formats to markdown using Docling
- Generate high-quality Q&A pairs from document content using local LLM models
- Support for multiple document formats: DOCX, PPTX, PDF, TXT, MD
- Batch processing of multiple documents
- Configurable shuffling of Q&A pairs
- Automatic language detection and translation to English
- Comprehensive logging and error handling

## Requirements

- Python 3.8+
- Ollama server running locally
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd doc-processor
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Install and run Ollama:
   - Follow instructions at https://ollama.ai/
   - Pull a model (e.g., `ollama pull llama3.2:latest`)
   - Start the Ollama server: `ollama serve`

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```
# Folder path for documents
FOLDER_PATH=docs

# Default file path for document processing
FILE_PATH=docs/example_document.docx

# Ollama configuration
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

## Usage

### Basic Usage

Run the main script to process all documents in the configured folder:

```bash
python main.py
```

This will:
- Process all supported documents in the folder specified by `FOLDER_PATH`
- Generate Q&A pairs for each document
- Save individual Q&A datasets to the `output` directory
- Create a combined Q&A dataset file with all generated pairs

### Advanced Usage

You can also use the Processor class directly in your Python code:

```python
from processor import Processor
from pathlib import Path

# Create processor instance
processor = Processor()

# Process a single document
result = processor.process_document(
    "path/to/document.docx",
    output_dir="output",
    shuffle_qa=True
)

# Process multiple documents
results = processor.process_multiple_documents(
    "path/to/documents/folder",
    output_dir="output",
    shuffle_qa=True,
    shuffle_combined=True
)
```

## Output Format

The application generates JSON files with the following structure:

```json
[
    {
        "question": "What is the name of the project?",
        "answer": "The project is named 'Phoenix'."
    },
    {
        "question": "Who is the client for the project?",
        "answer": "The client for the project is 'Innovate Corp'."
    }
]
```

For each processed document, it creates:
- An individual file: `{document_name}_qa_dataset.json`
- A combined file: `{YYYYMMDD}_combined_qa_dataset.json` (with all Q&A pairs)

## Project Structure

```
doc-processor/
├── main.py                 # Main entry point
├── processor.py            # Core processing logic
├── config.py               # Configuration management
├── utils.py                # Utility functions and prompts
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── docs/                  # Sample documents folder
├── output/                # Generated Q&A datasets
└── README.md              # This file
```

## How It Works

1. **Document Conversion**: Uses Docling to convert various document formats to markdown
2. **Content Processing**: Sends the markdown content to a local LLM via Ollama
3. **Q&A Generation**: The LLM generates question-answer pairs based on a detailed system prompt
4. **Output Formatting**: Parses and saves the results as structured JSON files

## Customization

### Modifying the Q&A Generation Prompt

Edit the `SYS_PROMPT` variable in [`utils.py`](utils.py:7) to customize how the LLM generates Q&A pairs.

### Supported Document Formats

The application supports these document formats:
- Microsoft Word (.docx)
- Microsoft PowerPoint (.pptx)
- PDF (.pdf)
- Plain text (.txt)
- Markdown (.md)

To add support for additional formats, modify the `supported_extensions` list in [`processor.py`](processor.py:161).

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check the OLLAMA_HOST in your .env file
   - Verify the model is installed: `ollama list`

2. **Document Processing Errors**
   - Check if the document is not corrupted
   - Ensure the document is in a supported format
   - Verify file permissions

3. **Memory Issues**
   - For large documents, consider processing them individually
   - Monitor your system's memory usage during processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Docling](https://github.com/DS4SD/docling) for document conversion
- [Ollama](https://ollama.ai/) for local LLM inference