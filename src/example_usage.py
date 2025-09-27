#!/usr/bin/env python3
"""
Example usage of the Medical MetaPrompt system
Demonstrates how to use the system to generate Epocrates-style guidelines
"""

import os
import sys
from pathlib import Path
from medical_metaprompt import MedicalMetaPrompt
from dotenv import load_dotenv

load_dotenv()


def create_sample_pdf_content():
    """Create a sample PDF content for demonstration purposes."""
    return """
    Type 2 Diabetes Management Guidelines
    
    Executive Summary:
    Type 2 diabetes is a chronic metabolic disorder characterized by insulin resistance and relative insulin deficiency. 
    Management focuses on glycemic control, cardiovascular risk reduction, and prevention of complications.
    
    Diagnostic Criteria:
    - Fasting plasma glucose ≥126 mg/dL (7.0 mmol/L)
    - 2-hour plasma glucose ≥200 mg/dL (11.1 mmol/L) during OGTT
    - HbA1c ≥6.5% (48 mmol/mol)
    - Random plasma glucose ≥200 mg/dL (11.1 mmol/L) with symptoms
    
    Treatment Algorithm:
    1. First-line: Metformin 500-2000 mg daily
    2. Second-line: Add SGLT2 inhibitor or GLP-1 receptor agonist
    3. Third-line: Add basal insulin or consider triple therapy
    
    Monitoring:
    - HbA1c every 3-6 months
    - Blood pressure <130/80 mmHg
    - LDL cholesterol <100 mg/dL
    - Annual eye exam, foot exam, and urine microalbumin
    
    Complications:
    - Microvascular: Retinopathy, nephropathy, neuropathy
    - Macrovascular: Cardiovascular disease, stroke, peripheral arterial disease
    
    Special Populations:
    - Elderly: Consider less stringent HbA1c targets (7.5-8.0%)
    - Pregnancy: Insulin therapy preferred, avoid oral agents
    - CKD: Adjust metformin dosing, consider SGLT2 inhibitors
    """


def example_1_basic_guideline_generation():
    """Example 1: Generate basic guidelines without PDF input."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Guideline Generation (No PDF)")
    print("=" * 80)
    
    try:
        medical_mp = MedicalMetaPrompt()
        
        # Generate guidelines for hypertension
        task = "Create an Epocrates-style clinical guideline for hypertension based on current medical standards"
        variables = "CONDITION\nADDITIONAL_INFO"
        
        prompt_template, extracted_vars = medical_mp(task, variables)
        
        print("Generated Prompt Template:")
        print("-" * 40)
        print(prompt_template)
        print("\nExtracted Variables:")
        print(extracted_vars)
        
    except Exception as e:
        print(f"Error: {e}")


def example_2_pdf_based_guidelines():
    """Example 2: Generate guidelines from PDF content."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: PDF-Based Guideline Generation")
    print("=" * 80)
    
    try:
        medical_mp = MedicalMetaPrompt()
        
        # Create a temporary PDF content file for demonstration
        sample_content = create_sample_pdf_content()
        
        # Save sample content to a temporary file
        temp_file = "/tmp/sample_diabetes_guidelines.txt"
        with open(temp_file, 'w') as f:
            f.write(sample_content)
        
        print(f"Using sample content from: {temp_file}")
        print("Sample content preview:")
        print("-" * 40)
        print(sample_content[:200] + "...")
        
        # Generate guidelines using the sample content
        task = "Create an Epocrates-style clinical guideline for Type 2 Diabetes based on PDF content and current medical standards"
        variables = "CONDITION\nPDF_CONTENT\nADDITIONAL_INFO"
        
        # Simulate PDF content by reading the text file
        pdf_content = medical_mp.extract_text_from_pdf(temp_file) if os.path.exists(temp_file) else sample_content
        
        prompt_template, extracted_vars = medical_mp(task, variables, pdf_path=temp_file)
        
        print("\nGenerated Prompt Template:")
        print("-" * 40)
        print(prompt_template)
        
        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        print(f"Error: {e}")


def example_3_information_extraction():
    """Example 3: Extract structured information from medical content."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Information Extraction")
    print("=" * 80)
    
    try:
        medical_mp = MedicalMetaPrompt()
        
        # Create sample content
        sample_content = create_sample_pdf_content()
        temp_file = "/tmp/sample_diabetes_guidelines.txt"
        with open(temp_file, 'w') as f:
            f.write(sample_content)
        
        # Extract information
        task = "Extract key clinical information from medical PDF focusing on Type 2 Diabetes"
        variables = "PDF_CONTENT\nEXTRACTION_FOCUS"
        
        prompt_template, extracted_vars = medical_mp(task, variables, pdf_path=temp_file)
        
        print("Generated Extraction Template:")
        print("-" * 40)
        print(prompt_template)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        print(f"Error: {e}")


def example_4_web_search_integration():
    """Example 4: Demonstrate web search integration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Web Search Integration")
    print("=" * 80)
    
    try:
        medical_mp = MedicalMetaPrompt()
        
        # Search for current diabetes guidelines
        search_results = medical_mp.search_medical_updates("Type 2 Diabetes", "metformin")
        
        print("Web Search Results:")
        print("-" * 40)
        print(f"Search Terms: {search_results['search_terms']}")
        print(f"Last Updated: {search_results['last_updated']}")
        print(f"Note: {search_results['note']}")
        
        if 'results' in search_results:
            print(f"\nFound {len(search_results['results'])} results:")
            for i, result in enumerate(search_results['results'][:3], 1):
                print(f"{i}. {result['title']}")
                print(f"   Link: {result['link']}")
                print(f"   Snippet: {result['snippet'][:100]}...")
                print()
        
    except Exception as e:
        print(f"Error: {e}")


def example_5_complete_workflow():
    """Example 5: Complete workflow demonstration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Complete Workflow")
    print("=" * 80)
    
    try:
        medical_mp = MedicalMetaPrompt()
        
        # Step 1: Search for current information
        print("Step 1: Searching for current medical information...")
        search_results = medical_mp.search_medical_updates("Hypertension")
        print(f"✓ Found {len(search_results.get('results', []))} current sources")
        
        # Step 2: Generate guidelines
        print("\nStep 2: Generating Epocrates-style guidelines...")
        task = "Create an Epocrates-style clinical guideline for hypertension based on current medical standards"
        variables = "CONDITION\nADDITIONAL_INFO"
        
        prompt_template, extracted_vars = medical_mp(task, variables)
        print("✓ Generated guideline template")
        
        # Step 3: Show the final prompt that would be used
        print("\nStep 3: Final prompt for AI processing:")
        print("-" * 40)
        
        final_prompt = f"""
        <CONDITION>
        Hypertension
        </CONDITION>
        
        <ADDITIONAL_INFO>
        Current search results: {search_results.get('note', 'No additional info')}
        Last updated: {search_results.get('last_updated', 'Unknown')}
        </ADDITIONAL_INFO>
        
        {prompt_template}
        """
        
        print(final_prompt[:500] + "..." if len(final_prompt) > 500 else final_prompt)
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("Medical MetaPrompt System - Example Usage")
    print("=" * 80)
    print("This script demonstrates various ways to use the Medical MetaPrompt system")
    print("to generate Epocrates-style guidelines for physicians.")
    print()
    
    # Check if required environment variables are set
    if not os.getenv("REGION_NAME"):
        print("Warning: REGION_NAME environment variable not set. Some features may not work.")
        print("Please set your AWS region: export REGION_NAME=us-east-1")
        print()
    
    try:
        example_1_basic_guideline_generation()
        example_2_pdf_based_guidelines()
        example_3_information_extraction()
        example_4_web_search_integration()
        example_5_complete_workflow()
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        print("\nTo use the system:")
        print("1. Set up your AWS credentials and REGION_NAME")
        print("2. Run: python medical_app.py --condition 'Your Condition' --pdf path/to/file.pdf")
        print("3. Or run: python medical_app.py (for interactive mode)")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("\nMake sure you have:")
        print("1. Installed all requirements: pip install -r requirements.txt")
        print("2. Set up AWS credentials")
        print("3. Set REGION_NAME environment variable")


if __name__ == "__main__":
    main()