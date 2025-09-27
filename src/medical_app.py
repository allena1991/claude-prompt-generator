import gradio as gr
import os
import tempfile
from medical_metaprompt import MedicalMetaPrompt

# Initialize the medical metaprompt system
medical_meta = MedicalMetaPrompt()

def process_pdf_for_guidelines(pdf_file, condition_medication, task_description=""):
    """
    Process uploaded PDF and generate Epocrates-style clinical guidelines
    """
    if pdf_file is None:
        return "Please upload a PDF file.", "", "", ""
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file)
            tmp_path = tmp_file.name
        
        # Generate clinical guidelines using direct Epocrates-style template
        result = medical_meta.generate_epocrates_style_guidelines(
            pdf_path=tmp_path,
            condition_or_medication=condition_medication
        )
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        guidelines = result["guidelines"]
        template_used = result["template_used"]
        source_length = result["source_text_length"]
        extracted_sample = result["extracted_text"]
        
        # Format the output
        summary = f"""
**Processing Summary:**
- Template Used: {template_used.replace('_', ' ').title()}
- Source Text Length: {source_length:,} characters
- Target Format: Epocrates-style clinical guidelines
- Processing Status: Complete
        """.strip()
        
        return guidelines, summary, extracted_sample, "Processing completed successfully!"
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        error_msg = f"Error processing PDF: {str(e)}"
        return error_msg, "", "", error_msg

def generate_custom_medical_prompt(task, variables):
    """
    Generate custom medical metaprompt
    """
    try:
        prompt_template, extracted_vars = medical_meta(task, variables)
        
        vars_summary = f"Extracted Variables: {', '.join(extracted_vars)}"
        
        return prompt_template, vars_summary, "Custom metaprompt generated successfully!"
        
    except Exception as e:
        error_msg = f"Error generating metaprompt: {str(e)}"
        return error_msg, "", error_msg

# Create Gradio interface
with gr.Blocks(title="Medical MetaPrompt - Epocrates Style Guidelines Generator", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🏥 Medical MetaPrompt Generator
    
    Generate up-to-date, Epocrates-style clinical guidelines from PDF documents using AI-powered metaprompts.
    
    ## Features:
    - 📄 **PDF Processing**: Extract text from medical literature, drug monographs, and clinical guidelines
    - 🎯 **Smart Detection**: Automatically detects whether content is about medications or medical conditions  
    - 📋 **Structured Output**: Generates concise, physician-friendly guidelines in Epocrates format
    - 🔧 **Custom Prompts**: Create specialized metaprompts for specific medical tasks
    """)
    
    with gr.Tabs():
        # Main PDF Processing Tab
        with gr.TabItem("📄 PDF to Clinical Guidelines"):
            gr.Markdown("### Upload a medical PDF and generate structured clinical guidelines")
            
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(
                        label="Upload Medical PDF",
                        file_types=[".pdf"],
                        type="binary"
                    )
                    
                    condition_med_input = gr.Textbox(
                        label="Condition or Medication Name (optional)",
                        placeholder="e.g., 'Hypertension' or 'Metformin'",
                        info="Leave blank for auto-detection"
                    )
                    
                    process_btn = gr.Button("🔄 Generate Guidelines", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    status_output = gr.Textbox(
                        label="Status",
                        interactive=False,
                        max_lines=2
                    )
                    
                    summary_output = gr.Markdown(label="Processing Summary")
            
            with gr.Row():
                guidelines_output = gr.Textbox(
                    label="Generated Clinical Guidelines",
                    lines=20,
                    max_lines=30,
                    interactive=False,
                    show_copy_button=True
                )
            
            with gr.Accordion("🔍 View Generated Prompt Template", open=False):
                prompt_template_output = gr.Textbox(
                    label="Metaprompt Template Used",
                    lines=15,
                    interactive=False,
                    show_copy_button=True
                )
        
        # Custom Metaprompt Generation Tab
        with gr.TabItem("🔧 Custom Medical Metaprompt"):
            gr.Markdown("### Create specialized metaprompts for specific medical tasks")
            
            with gr.Row():
                with gr.Column():
                    custom_task_input = gr.Textbox(
                        label="Medical Task Description",
                        placeholder="e.g., 'Extract contraindications and drug interactions from pharmaceutical literature'",
                        lines=3
                    )
                    
                    custom_variables_input = gr.Textbox(
                        label="Input Variables (one per line)",
                        placeholder="DRUG_INFORMATION\nPATIENT_PROFILE\nCLINICAL_CONTEXT",
                        lines=5
                    )
                    
                    generate_custom_btn = gr.Button("⚡ Generate Custom Metaprompt", variant="primary")
                
                with gr.Column():
                    custom_status = gr.Textbox(
                        label="Status",
                        interactive=False,
                        max_lines=2
                    )
                    
                    custom_vars_summary = gr.Textbox(
                        label="Variables Summary",
                        interactive=False,
                        max_lines=3
                    )
            
            custom_prompt_output = gr.Textbox(
                label="Generated Custom Metaprompt",
                lines=20,
                interactive=False,
                show_copy_button=True
            )
        
        # Information and Examples Tab
        with gr.TabItem("ℹ️ Information & Examples"):
            gr.Markdown("""
            ## How It Works
            
            This tool uses advanced AI metaprompts to analyze medical PDFs and generate structured clinical guidelines similar to those found in Epocrates, a popular clinical decision support tool used by physicians.
            
            ### Supported Content Types:
            
            **📊 Drug Monographs:**
            - Medication dosing guidelines
            - Contraindications and warnings
            - Drug interactions
            - Adverse effects
            - Monitoring parameters
            
            **🩺 Clinical Guidelines:**
            - Diagnostic criteria
            - Treatment algorithms  
            - Follow-up recommendations
            - Referral criteria
            - Clinical decision rules
            
            ### Example Outputs:
            
            **Drug Information Format:**
            ```
            DRUG NAME: Metformin (Glucophage)
            
            INDICATIONS:
            - Type 2 diabetes mellitus
            - Polycystic ovary syndrome (off-label)
            
            CONTRAINDICATIONS:
            - eGFR <30 mL/min/1.73m²
            - Severe hepatic impairment
            - Acute heart failure
            
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
            
            **Clinical Guideline Format:**
            ```
            CONDITION: Hypertension
            
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
            
            ### Tips for Best Results:
            
            1. **Clear PDFs**: Use high-quality, text-based PDFs rather than scanned images
            2. **Relevant Content**: Focus on clinical or pharmaceutical literature
            3. **Specific Names**: Provide specific medication or condition names when known
            4. **Recent Guidelines**: Use current medical literature for up-to-date recommendations
            
            ### Technical Requirements:
            
            - PDF files must be readable (not password-protected)
            - Maximum file size: 100MB
            - Supports both medication monographs and clinical guidelines
            - Requires AWS Bedrock access for AI processing
            """)
    
    # Event handlers
    process_btn.click(
        fn=process_pdf_for_guidelines,
        inputs=[pdf_input, condition_med_input],
        outputs=[guidelines_output, summary_output, prompt_template_output, status_output]
    )
    
    generate_custom_btn.click(
        fn=generate_custom_medical_prompt,
        inputs=[custom_task_input, custom_variables_input],
        outputs=[custom_prompt_output, custom_vars_summary, custom_status]
    )

# Launch the application
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )