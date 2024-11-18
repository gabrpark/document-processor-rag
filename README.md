# Document Processor RAG

A data pipeline that processes Facebook Q&A posts and comments, transforms them into vector embeddings, and stores them in Pinecone for efficient similarity search. This project serves as a proof-of-concept for vectorizing social media content to be used in a chatbot system.

## Overview

This pipeline currently:
1. Reads Q&A content from text files (temporary solution)
2. Processes and chunks the content
3. Generates vector embeddings
4. Stores embeddings in Pinecone
5. Verifies data retrieval using cosine similarity

Future implementations will integrate with AWS DynamoDB/MongoDB for source data and incorporate this pipeline into a larger chatbot system.

## Prerequisites

- Python 3.8+
- Node.js
- Pinecone API key
- OpenAI API key (for embeddings generation)
- AWS credentials (for future DynamoDB integration)
- MongoDB connection string (for future implementation)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/document-processor-rag
cd document-processor-rag

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── processor/
│   │   ├── __init__.py
│   │   ├── chunker.py      # Text chunking functionality
│   │   ├── embedder.py     # Vector embedding generation
│   │   └── uploader.py     # Pinecone upload operations
│   └── database/
│       ├── __init__.py
│       ├── client.py       # Database client configuration
│       └── models.py       # Database models
├── scripts/
│   ├── __init__.py
│   └── process_documents.py  # Main processing script
├── test/                    # Test directory
├── sample.txt              # Sample input file
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── package-lock.json
├── tsconfig.json
├── setup.py
├── LICENSE
└── README.md
```

## Configuration

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
MONGODB_URI=your_mongodb_uri
```

## Usage

### Processing Documents

To process documents and generate embeddings:

```bash
python scripts/process_documents.py --input_file sample.txt
```

### Development

The project is structured into two main components:

1. Processor Module (`src/processor/`)
   - `chunker.py`: Handles document chunking
   - `embedder.py`: Manages embedding generation
   - `uploader.py`: Handles Pinecone uploads
   - `text_to_embeddings.py`: Main script for processing text data
   - `json_to_vector.py`: Main script for processing JSON data
   - `raw_data_to_json.py`: Main script for processing raw data

2. Database Module (`src/database/`)
   - `client.py`: Database connection management
   - `models.py`: Data models and schemas

## Testing

Run the test suite:

```bash
pytest test/
```

## Future Implementation

The following features are planned:

1. Database Integration
   - Replace text file input with DynamoDB/MongoDB connectors
   - Implement real-time data synchronization
   - Add data validation and error handling

2. Pipeline Enhancement
   - Add parallel processing for large datasets
   - Implement batch processing
   - Add logging and monitoring
   - Include data versioning

3. Chatbot Integration
   - Connect with chatbot API
   - Implement feedback loop
   - Add relevance scoring

## License

This project is licensed under the MIT License - see the LICENSE file for details.