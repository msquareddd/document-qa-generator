import json
import ollama
from ollama import ChatResponse
import utils
from config import config
from docling.document_converter import DocumentConverter
from pathlib import Path
import os
import random


class Processor:
    """
    A class to process documents by converting them to markdown and generating Q&A pairs using LLM.
    """
    
    def __init__(self):
        """Initialize the Processor with document converter and Ollama client."""
        self.converter = DocumentConverter()
        self.client = ollama.Client(host=config.ollama_host)

    def md_converter(self, doc_path):
        """
        Convert a document to markdown format.
        
        Args:
            doc_path (str or Path): Path to the document to convert
            
        Returns:
            str: The document content in markdown format
            
        Raises:
            Exception: If document conversion fails
        """
        try:
            result = self.converter.convert(doc_path)
            return result.document.export_to_markdown()
        except Exception as e:
            print(f"Error converting document: {e}")
            raise

    def llm_qa_generator(self, doc_md):
        """
        Generate Q&A pairs from markdown document content using LLM.
        
        Args:
            doc_md (str): The document content in markdown format
            
        Returns:
            str: The LLM response containing Q&A pairs in JSON format
            
        Raises:
            Exception: If LLM processing fails
        """
        try:
            response: ChatResponse = self.client.chat(
                model=str(config.ollama_model),
                messages=[
                    {
                        "role": "system",
                        "content": utils.SYS_PROMPT
                    },
                    {
                        'role': 'user',
                        'content': doc_md,
                    },
                ],
                options={
                    'temperature': config.temperature,  # Increase for more creative/detailed responses
                    'top_p': config.top_p,        # Add for more diverse output
                    'num_predict': config.max_new_tokens,  # Increase to 12K tokens for more content
                    'repeat_penalty': config.repeat_penaly  # Reduce repetition
                }
            )

            # After getting the response
            if hasattr(response, 'prompt_eval_count') and hasattr(response, 'eval_count'):
                print(f"Prompt tokens: {response.prompt_eval_count}")
                print(f"Response tokens: {response.eval_count}")
            
            return response['message']['content']
        except Exception as e:
            print(f"Error generating Q&A pairs: {e}")
            raise
    
    def process_document(self, doc_path, output_dir=None, shuffle_qa=True):
        """
        Process a single document: convert to markdown, generate Q&A pairs, and save results.
        
        Args:
            doc_path (str or Path): Path to the document to process
            output_dir (str or Path, optional): Directory to save the output. Defaults to current directory.
            shuffle_qa (bool): Whether to shuffle the Q&A pairs before saving. Defaults to True.
            
        Returns:
            dict: The processed Q&A data
            
        Raises:
            Exception: If any step in the processing fails
        """
        try:
            # Convert document to markdown
            print(f"Converting document to markdown: {doc_path}")
            doc_md = self.md_converter(doc_path)
            print(f"Successfully converted document to markdown (length: {len(doc_md)} chars)")
            
            # Generate Q&A pairs
            print(f"Generating Q&A pairs using LLM")
            llm_response = self.llm_qa_generator(doc_md)
            print(f"Successfully generated Q&A pairs (response length: {len(llm_response)} chars)")
            
            # Parse the response
            print(f"Parsing LLM response")
            json_data = utils.parse_llm_response(llm_response)
            print(f"Successfully parsed {len(json_data) if isinstance(json_data, list) else 1} Q&A pairs")
            
            # Shuffle Q&A pairs if requested
            if shuffle_qa and isinstance(json_data, list):
                random.shuffle(json_data)
                print("Q&A pairs have been shuffled")
            
            # Determine output file path
            doc_name = Path(doc_path).stem
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"{doc_name}_qa_dataset.json"
            else:
                output_file = Path(f"{doc_name}_qa_dataset.json")
            
            # Save the results
            print(f"Saving results to {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"Results saved to {output_file}")
            return json_data
            
        except Exception as e:
            print(f"Error processing document {doc_path}: {e}")
            raise
    
    def process_multiple_documents(self, folder_path, output_dir=None, shuffle_qa=True, shuffle_combined=True):
        """
        Process all documents in a folder.
        
        Args:
            folder_path (str or Path): Path to the folder containing documents
            output_dir (str or Path, optional): Directory to save the output. Defaults to current directory.
            shuffle_qa (bool): Whether to shuffle Q&A pairs within each document. Defaults to True.
            shuffle_combined (bool): Whether to shuffle Q&A pairs in the combined file. Defaults to True.
            
        Returns:
            list: List of processed Q&A data for all documents
        """
        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise ValueError(f"Folder path does not exist: {folder_path}")
        
        # Get all supported document files
        supported_extensions = ['.docx', '.pptx', '.pdf', '.txt', '.md']
        doc_files = set()  # Use set to avoid duplicates from the start
        
        print(f"Searching for documents in: {folder_path}")
        
        # Use a single glob pattern with case-insensitive matching
        for ext in supported_extensions:
            # On Windows, glob is already case-insensitive, so we only need one pattern
            matches = set(folder_path.glob(f"*{ext}"))
            doc_files.update(matches)
            print(f"Found {len(matches)} files with extension {ext}")
        
        # Convert to sorted list for consistent processing order
        doc_files = sorted(list(doc_files))
        
        if not doc_files:
            print(f"No supported documents found in {folder_path}")
            return []
        
        print(f"Found {len(doc_files)} documents to process:")
        for i, doc_file in enumerate(doc_files):
            print(f"  {i+1}. {doc_file}")
        
        all_results = []
        for i, doc_file in enumerate(doc_files):
            print(f"Processing document {i+1}/{len(doc_files)}: {doc_file}")
            try:
                result = self.process_document(doc_file, output_dir, shuffle_qa)
                print(f"Successfully processed document {i+1}/{len(doc_files)}: {doc_file}")
                all_results.append(result)
            except Exception as e:
                print(f"Failed to process {doc_file}: {e}")
                continue
        
        # Optionally save a combined results file
        if output_dir and all_results:
            output_dir = Path(output_dir)
            combined_file = output_dir / f"{utils.TODAY}_combined_qa_dataset.json"
            
            # Flatten all Q&A pairs into a single list
            combined_qa = []
            for result in all_results:
                if isinstance(result, list):
                    combined_qa.extend(result)
            
            # Shuffle combined Q&A pairs if requested
            if shuffle_combined and combined_qa:
                random.shuffle(combined_qa)
                print("Combined Q&A pairs have been shuffled")
            
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(combined_qa, f, indent=2, ensure_ascii=False)
            
            print(f"Combined results saved to {combined_file}")
        
        return all_results
