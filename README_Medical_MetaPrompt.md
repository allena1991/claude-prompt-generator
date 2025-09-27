# Medical MetaPrompt System

A specialized AI system that reads PDF documents and generates up-to-date Epocrates-style clinical guidelines for physicians. This system combines PDF processing, web search capabilities, and advanced prompt engineering to create comprehensive, evidence-based medical guidelines.

## Features

- **PDF Processing**: Extract text content from medical literature PDFs
- **Epocrates-Style Guidelines**: Generate structured, physician-friendly clinical guidelines
- **Web Search Integration**: Access current medical information and guidelines
- **Information Extraction**: Extract structured clinical data from medical documents
- **Interactive Mode**: User-friendly command-line interface
- **AWS Bedrock Integration**: Powered by Claude AI for high-quality medical content generation

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up AWS credentials and region:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export REGION_NAME=us-east-1
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Generate guidelines for a condition
python medical_app.py --condition "Type 2 Diabetes"

# Generate guidelines from PDF
python medical_app.py --condition "Hypertension" --pdf path/to/guidelines.pdf

# Extract information from PDF
python medical_app.py --condition "Diabetes" --pdf path/to/study.pdf --extract-only

# Save output to file
python medical_app.py --condition "COPD" --pdf path/to/guidelines.pdf --output guidelines.txt
```

#### Interactive Mode
```bash
# Run without arguments for interactive mode
python medical_app.py
```

### Programmatic Usage

```python
from medical_metaprompt import MedicalMetaPrompt

# Initialize the system
medical_mp = MedicalMetaPrompt()

# Generate guidelines
task = "Create an Epocrates-style clinical guideline for hypertension"
variables = "CONDITION\nADDITIONAL_INFO"
prompt_template, extracted_vars = medical_mp(task, variables)

# Process PDF
pdf_content = medical_mp.extract_text_from_pdf("path/to/medical_paper.pdf")

# Search for current information
search_results = medical_mp.search_medical_updates("Type 2 Diabetes", "metformin")
```

## Generated Guideline Structure

The system generates guidelines in the following Epocrates-style format:

### Quick Reference
- Primary Treatment
- First-line Medications
- Key Monitoring
- Red Flags

### Diagnosis
- Criteria
- Differential Diagnosis

### Treatment Algorithm
- Step-by-step treatment approach
- Dosing guidelines
- Monitoring requirements

### Medications
- First-line and second-line options
- Dosing, contraindications, side effects
- Monitoring requirements

### Special Populations
- Pediatric considerations
- Geriatric considerations
- Pregnancy/lactation

### Complications & Management
- Acute and chronic complications
- Prevention strategies

### Patient Education
- Key points for patients
- Lifestyle modifications

## Examples

### Example 1: Basic Guideline Generation
```python
from medical_metaprompt import MedicalMetaPrompt

medical_mp = MedicalMetaPrompt()
task = "Create an Epocrates-style clinical guideline for hypertension"
variables = "CONDITION\nADDITIONAL_INFO"
prompt_template, extracted_vars = medical_mp(task, variables)
```

### Example 2: PDF-Based Guidelines
```python
# Generate guidelines from a medical PDF
task = "Create an Epocrates-style clinical guideline for Type 2 Diabetes based on PDF content"
variables = "CONDITION\nPDF_CONTENT\nADDITIONAL_INFO"
prompt_template, extracted_vars = medical_mp(task, variables, pdf_path="diabetes_guidelines.pdf")
```

### Example 3: Information Extraction
```python
# Extract structured information from PDF
task = "Extract key clinical information from medical PDF focusing on diabetes management"
variables = "PDF_CONTENT\nEXTRACTION_FOCUS"
prompt_template, extracted_vars = medical_mp(task, variables, pdf_path="research_paper.pdf")
```

## File Structure

```
src/
├── medical_metaprompt.py      # Main Medical MetaPrompt class
├── medical_metaprompt.txt     # Specialized prompt templates
├── medical_app.py            # Command-line application
├── example_usage.py          # Usage examples and demonstrations
└── metaprompt.py             # Original MetaPrompt system
```

## Requirements

- Python 3.7+
- AWS Bedrock access
- Required packages (see requirements.txt):
  - boto3
  - PyPDF2
  - requests
  - beautifulsoup4
  - python-dotenv

## Configuration

### Environment Variables
- `REGION_NAME`: AWS region for Bedrock service
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

### Model Configuration
The system uses Claude 3 Haiku by default. You can modify the model in `medical_metaprompt.py`:
```python
modelId = "anthropic.claude-3-haiku-20240307-v1:0"
```

## Medical Disclaimer

⚠️ **Important Medical Disclaimer**: This system is designed to assist healthcare professionals and should not be used as a substitute for professional medical judgment. Always verify information against current medical guidelines and consult with qualified healthcare professionals for patient care decisions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the examples in `example_usage.py`
2. Review the command-line help: `python medical_app.py --help`
3. Open an issue on GitHub

## Roadmap

- [ ] Integration with medical databases (PubMed, UpToDate)
- [ ] Support for additional file formats (DOCX, HTML)
- [ ] Batch processing capabilities
- [ ] Custom guideline templates
- [ ] Integration with EMR systems
- [ ] Multi-language support