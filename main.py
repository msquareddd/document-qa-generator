
import sys
from pathlib import Path
from config import config
from processor import Processor

# Set console encoding for Windows to handle Unicode characters
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Create processor instance
processor = Processor()

# Process all documents in the configured folder
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Shuffling options (set to False if you want to maintain original order)
shuffle_individual_qa = True  # Shuffle Q&A pairs within each document
shuffle_combined_qa = True   # Shuffle Q&A pairs in the combined file

print(f"Processing documents from: {config.folder_path}")
print(f"Output will be saved to: {output_dir}")
print(f"Shuffle individual Q&A pairs: {shuffle_individual_qa}")
print(f"Shuffle combined Q&A pairs: {shuffle_combined_qa}")

try:
    # Process all documents in the folder
    results = processor.process_multiple_documents(
        config.folder_path,
        output_dir,
        shuffle_qa=shuffle_individual_qa,
        shuffle_combined=shuffle_combined_qa
    )
    
    if results:
        print(f"\nSuccessfully processed {len(results)} documents")
        print("All processing completed!")
    else:
        print("No documents were processed")
        
except Exception as e:
    print(f"Error during processing: {e}")
    sys.exit(1)