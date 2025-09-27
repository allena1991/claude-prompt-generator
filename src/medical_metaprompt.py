import json
import os
import re
import PyPDF2
import requests
from bs4 import BeautifulSoup
from datetime import datetime
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
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def search_medical_updates(self, condition, medication=None):
        """Search for up-to-date medical information using web search."""
        search_terms = f"{condition} treatment guidelines 2024"
        if medication:
            search_terms += f" {medication}"
        
        try:
            # Search for current medical guidelines
            search_url = f"https://www.google.com/search?q={search_terms.replace(' ', '+')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract relevant search results
            results = []
            for result in soup.find_all('div', class_='g')[:5]:  # Top 5 results
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('span', class_='aCOpRe')
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(),
                        'link': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text() if snippet_elem else ''
                    })
            
            return {
                "search_terms": search_terms,
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "results": results,
                "note": "Web search results for current medical guidelines"
            }
        except Exception as e:
            return {
                "search_terms": search_terms,
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "error": f"Search failed: {str(e)}",
                "note": "Using cached or default information"
            }

    def __call__(self, task, variables, pdf_path=None):
        variables = variables.split("\n")
        variables = [variable for variable in variables if len(variable)]

        # Extract PDF content if provided
        pdf_content = ""
        if pdf_path and os.path.exists(pdf_path):
            pdf_content = self.extract_text_from_pdf(pdf_path)
            variables.append("PDF_CONTENT")

        variable_string = ""
        for variable in variables:
            if variable == "PDF_CONTENT":
                variable_string += f"\n<PDF_CONTENT>\n{pdf_content}\n</PDF_CONTENT>"
            else:
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

        def pretty_print(message):
            print(
                "\n\n".join(
                    "\n".join(
                        line.strip()
                        for line in re.findall(
                            r".{1,100}(?:\s+|$)", paragraph.strip("\n")
                        )
                    )
                    for paragraph in re.split(r"\n\n+", message)
                )
            )

        extracted_prompt_template = self.extract_prompt(message)
        variables = self.extract_variables(message)

        return extracted_prompt_template.strip(), "\n".join(variables)

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

    def generate_epocrates_guideline(self, condition, pdf_path=None, additional_info=""):
        """Generate an Epocrates-style medical guideline."""
        task = f"Create an Epocrates-style clinical guideline for {condition} based on PDF content and current medical standards"
        variables = f"CONDITION\nADDITIONAL_INFO"
        
        # Add PDF content if provided
        if pdf_path:
            variables += "\nPDF_CONTENT"
        
        # Add additional information
        if additional_info:
            variables += "\nADDITIONAL_INFO"
        
        return self(task, variables, pdf_path)