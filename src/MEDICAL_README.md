# Medical MetaPrompt - Epocrates Style Guidelines Generator

This module extends the Claude Prompt Generator to create up-to-date, Epocrates-style clinical guidelines for physicians by reading and analyzing medical PDFs.

## 🏥 Overview

The Medical MetaPrompt system uses AI-powered metaprompts to:
- Extract text from medical literature PDFs
- Analyze clinical content for medications or medical conditions
- Generate structured, physician-friendly guidelines in Epocrates format
- Support both custom metaprompt generation and direct guideline creation

## 🚀 Quick Start

### Prerequisites

1. **AWS Bedrock Access**: Configure AWS credentials with Bedrock access
2. **Environment Setup**: Copy `.env.example` to `.env` and configure:
   ```
   REGION_NAME=us-east-1
   OPENAI_API_KEY=your_key_here (optional)
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
cd src
python medical_app.py
```

Access the web interface at `http://127.0.0.1:7860`

## 📋 Features

### 1. PDF to Clinical Guidelines
- **Upload**: Medical PDFs (drug monographs, clinical guidelines, research papers)
- **Auto-Detection**: Automatically identifies medication vs. condition content
- **Structured Output**: Generates Epocrates-style clinical references

### 2. Custom Medical Metaprompts
- **Task Definition**: Create specialized prompts for specific medical tasks
- **Variable Management**: Define input variables for reusable templates
- **Template Generation**: Generate structured metaprompts for medical AI tasks

## 🔧 Core Components

### `MedicalMetaPrompt` Class

```python
from medical_metaprompt import MedicalMetaPrompt

# Initialize
medical_meta = MedicalMetaPrompt()

# Generate guidelines from PDF
result = medical_meta.generate_epocrates_style_guidelines(
    pdf_path="medical_document.pdf",
    condition_or_medication="Hypertension"
)

print(result["guidelines"])
```

### Key Methods

- `extract_text_from_pdf()`: Extract text using multiple PDF libraries
- `generate_epocrates_style_guidelines()`: Direct Epocrates-style generation
- `generate_clinical_guidelines()`: Metaprompt-based generation
- `clean_medical_text()`: Preprocess medical text for better AI processing

## 📊 Output Formats

### Drug Information Format
```
METFORMIN (Glucophage)

INDICATIONS:
- Type 2 diabetes mellitus
- Polycystic ovary syndrome (off-label)

CONTRAINDICATIONS:
- eGFR <30 mL/min/1.73m²
- Severe hepatic impairment

DOSING:
- Adult: 500-850 mg BID with meals
- Maximum: 2550 mg/day
- Renal adjustment: Avoid if eGFR <30

ADVERSE EFFECTS:
- Common: GI upset, metallic taste
- Serious: Lactic acidosis (rare)

MONITORING:
- Renal function every 6-12 months
- Vitamin B12 levels annually
```

### Clinical Condition Format
```
HYPERTENSION

DEFINITION:
- BP ≥130/80 mmHg on repeated measurements

DIAGNOSIS:
- Clinical presentation: Often asymptomatic
- Diagnostic criteria: Confirmed elevated BP readings
- Recommended tests: Basic metabolic panel, lipids, ECG

TREATMENT:
- First-line: ACE inhibitor or ARB
- Second-line: Add thiazide diuretic
- Target: <130/80 mmHg

MONITORING:
- BP checks every 1-3 months until controlled
- Annual labs for medication monitoring
```

## 🔍 Technical Details

### PDF Processing
- **Primary**: `pdfplumber` for complex layouts
- **Fallback**: `PyPDF2` for compatibility
- **Text Cleaning**: Removes artifacts, normalizes whitespace

### AI Models
- **Metaprompt Generation**: Claude 3 Haiku (cost-effective)
- **Clinical Guidelines**: Claude 3 Sonnet (higher accuracy)
- **Temperature**: 0.0 for consistent medical formatting

### Safety Features
- Evidence-based information only
- Explicit source attribution
- "Not specified in source" for missing data
- Prioritizes safety information (contraindications, warnings)

## 📁 File Structure

```
src/
├── medical_metaprompt.py      # Core medical metaprompt class
├── medical_metaprompt.txt     # Medical metaprompt templates
├── epocrates_metaprompt.txt   # Direct Epocrates-style template
├── medical_app.py             # Gradio web interface
└── MEDICAL_README.md          # This documentation
```

## 🧪 Testing

### Basic Test
```python
from medical_metaprompt import MedicalMetaPrompt

# Test PDF processing
medical_meta = MedicalMetaPrompt()
result = medical_meta.generate_epocrates_style_guidelines("sample.pdf")
print("Generated Guidelines:")
print(result["guidelines"])
```

### Web Interface Test
1. Start the application: `python medical_app.py`
2. Upload a medical PDF
3. Optional: Specify condition/medication name
4. Click "Generate Guidelines"
5. Review structured output

## 🔒 Compliance & Safety

### Important Disclaimers
- **Not for Clinical Use**: Generated guidelines are for reference only
- **Professional Review**: All outputs should be reviewed by qualified medical professionals
- **Source Verification**: Always verify information against current medical standards
- **Regulatory Compliance**: Ensure compliance with healthcare regulations in your jurisdiction

### Best Practices
- Use current, peer-reviewed medical literature
- Specify condition/medication names for better accuracy
- Review all generated content for clinical accuracy
- Maintain source document traceability

## 🚨 Limitations

- PDF quality affects text extraction accuracy
- AI may not capture nuanced clinical contexts
- Generated content requires professional validation
- Limited to information present in source documents
- Not suitable for emergency or critical care decisions

## 📞 Support

For technical issues or feature requests:
1. Check existing documentation
2. Review error messages and logs
3. Ensure proper AWS Bedrock configuration
4. Verify PDF file format and readability

## 📚 References

- [Epocrates Clinical Decision Support](https://www.epocrates.com/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude AI Model Documentation](https://docs.anthropic.com/claude/)
- [Medical AI Guidelines](https://www.fda.gov/medical-devices/software-medical-device-samd/)