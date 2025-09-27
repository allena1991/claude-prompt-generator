import json
import os
import re
import PyPDF2
import pdfplumber
from io import BytesIO
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()


class MedicalMetaPrompt:
    def __init__(self):
        # Get the directory where the current script is located
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the full path to the medical metaprompt file
        prompt_guide_path = os.path.join(current_script_path, "medical_metaprompt.txt")
        
        # Open the file using the full path
        with open(prompt_guide_path, "r") as f:
            self.metaprompt = f.read()
        
        region_name = os.getenv("REGION_NAME")
        session = boto3.Session()
        retry_config = Config(
            region_name=region_name,
            retries={
                "max_attempts": 5,
                "mode": "standard",
            },
        )
        service_name = "bedrock-runtime"
        self.bedrock_client = session.client(
            service_name=service_name, config=retry_config
        )
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF using multiple methods for better accuracy
        """
        text = ""
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
                raise Exception(f"Could not extract text from PDF: {e2}")
        
        return text.strip()
    
    def clean_medical_text(self, text):
        """
        Clean and preprocess medical text for better processing
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
        
        return text.strip()
    
    def __call__(self, task, variables, pdf_path=None):
        """
        Generate medical metaprompt with optional PDF processing
        """
        # If PDF path is provided, extract text and add it as a variable
        if pdf_path and os.path.exists(pdf_path):
            pdf_text = self.extract_text_from_pdf(pdf_path)
            pdf_text = self.clean_medical_text(pdf_text)
            
            # Add PDF text to variables
            if "PDF_TEXT" not in variables:
                variables = variables + "\nPDF_TEXT"
            
            # Store PDF text for later use
            self.pdf_text = pdf_text
        
        variables = variables.split("\n")
        variables = [variable for variable in variables if len(variable)]
        
        variable_string = ""
        for variable in variables:
            variable_string += "\n{$" + variable.upper() + "}"
        
        prompt = self.metaprompt.replace("{{TASK}}", task)
        assistant_partial = "<Inputs>"
        if variable_string:
            assistant_partial += (
                variable_string + "\n</Inputs>\n<Instructions Structure>"
            )
        
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": assistant_partial},
        ]
        
        body = json.dumps(
            {
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.0,
                "anthropic_version": "bedrock-2023-05-31",
            }
        )
        
        modelId = "anthropic.claude-3-haiku-20240307-v1:0"
        accept = "application/json"
        contentType = "application/json"
        
        response = self.bedrock_client.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())
        message = response_body["content"][0]["text"]
        
        extracted_prompt_template = self.extract_prompt(message)
        variables = self.extract_variables(message)
        
        return extracted_prompt_template.strip(), "\n".join(variables)
    
    def generate_clinical_guidelines(self, pdf_path, condition_or_medication=None):
        """
        Generate Epocrates-style clinical guidelines from a PDF
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        pdf_text = self.clean_medical_text(pdf_text)
        
        # Determine if this is about a medication or condition
        if condition_or_medication is None:
            # Try to auto-detect based on content
            medication_keywords = ['dosage', 'mg', 'tablet', 'capsule', 'injection', 'contraindication', 'adverse effect']
            condition_keywords = ['diagnosis', 'symptom', 'treatment', 'therapy', 'management', 'prognosis']
            
            med_score = sum(1 for keyword in medication_keywords if keyword.lower() in pdf_text.lower())
            cond_score = sum(1 for keyword in condition_keywords if keyword.lower() in pdf_text.lower())
            
            if med_score > cond_score:
                task_type = "medication"
            else:
                task_type = "condition"
        else:
            # User specified the type
            task_type = "medication" if any(word in condition_or_medication.lower() for word in ['drug', 'medication', 'pill', 'tablet']) else "condition"
        
        # Generate appropriate metaprompt based on type
        if task_type == "medication":
            task = "Extract key medication information from clinical text and format as structured drug monograph for physician reference"
            variables = "PDF_TEXT\nMEDICATION_NAME"
        else:
            task = "Create clinical practice guidelines from medical literature for physician reference"
            variables = "PDF_TEXT\nCONDITION"
        
        # Generate the metaprompt
        prompt_template, extracted_vars = self.__call__(task, variables)
        
        # Apply the generated prompt to the PDF text
        final_prompt = prompt_template.replace("{$PDF_TEXT}", pdf_text)
        if condition_or_medication:
            if task_type == "medication":
                final_prompt = final_prompt.replace("{$MEDICATION_NAME}", condition_or_medication)
            else:
                final_prompt = final_prompt.replace("{$CONDITION}", condition_or_medication)
        
        # Execute the final prompt
        messages = [{"role": "user", "content": final_prompt}]
        
        body = json.dumps(
            {
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.1,
                "anthropic_version": "bedrock-2023-05-31",
            }
        )
        
        response = self.bedrock_client.invoke_model(
            body=body, 
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Use Sonnet for better medical reasoning
            accept="application/json", 
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        guidelines = response_body["content"][0]["text"]
        
        return {
            "guidelines": guidelines,
            "source_text_length": len(pdf_text),
            "task_type": task_type,
            "prompt_template": prompt_template
        }
    
    def generate_epocrates_style_guidelines(self, pdf_path, condition_or_medication=None):
        """
        Generate Epocrates-style clinical guidelines directly using the specialized template
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text from PDF
        pdf_text = self.extract_text_from_pdf(pdf_path)
        pdf_text = self.clean_medical_text(pdf_text)
        
        # Load the Epocrates-specific template
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        epocrates_template_path = os.path.join(current_script_path, "epocrates_metaprompt.txt")
        
        with open(epocrates_template_path, "r") as f:
            epocrates_template = f.read()
        
        # Replace variables in template
        final_prompt = epocrates_template.replace("{PDF_TEXT}", pdf_text)
        if condition_or_medication:
            final_prompt = final_prompt.replace("{CONDITION_OR_MEDICATION}", condition_or_medication)
        else:
            final_prompt = final_prompt.replace("{CONDITION_OR_MEDICATION}", "Not specified - please analyze the content and determine the primary focus")
        
        # Execute the prompt
        messages = [{"role": "user", "content": final_prompt}]
        
        body = json.dumps(
            {
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.0,  # Use 0 temperature for consistent medical formatting
                "anthropic_version": "bedrock-2023-05-31",
            }
        )
        
        response = self.bedrock_client.invoke_model(
            body=body, 
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json", 
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        guidelines = response_body["content"][0]["text"]
        
        return {
            "guidelines": guidelines,
            "source_text_length": len(pdf_text),
            "template_used": "epocrates_direct",
            "extracted_text": pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
        }
    
    def extract_between_tags(self, tag: str, string: str, strip: bool = False) -> list[str]:
        ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        return ext_list
    
    def remove_empty_tags(self, text):
        return re.sub(r"\n<(\w+)>\s*</\1>\n", "", text, flags=re.DOTALL)
    
    def extract_prompt(self, metaprompt_response):
        between_tags = self.extract_between_tags("Instructions", metaprompt_response)[0]
        return (
            between_tags[:1000]
            + self.remove_empty_tags(
                self.remove_empty_tags(between_tags[1000:]).strip()
            ).strip()
        )
    
    def extract_variables(self, prompt):
        pattern = r"{([^}]+)}"
        variables = re.findall(pattern, prompt)
        return set(variables)


# Example usage and testing
if __name__ == "__main__":
    medical_meta = MedicalMetaPrompt()
    
    # Example: Generate metaprompt for medication information
    task = "Extract medication dosing and safety information from clinical documents"
    variables = "CLINICAL_TEXT\nMEDICATION_NAME"
    
    try:
        prompt_template, vars_list = medical_meta(task, variables)
        print("Generated Medical Metaprompt:")
        print("=" * 50)
        print(prompt_template)
        print("\n" + "=" * 50)
        print("Variables:", vars_list)
    except Exception as e:
        print(f"Error: {e}")