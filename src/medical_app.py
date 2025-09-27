#!/usr/bin/env python3
"""
Medical MetaPrompt Application
A specialized system for reading PDFs and generating up-to-date Epocrates-style guidelines for physicians.
"""

import os
import sys
import argparse
from pathlib import Path
from medical_metaprompt import MedicalMetaPrompt
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Epocrates-style medical guidelines from PDF documents"
    )
    parser.add_argument(
        "--condition", 
        required=True, 
        help="Medical condition to create guidelines for (e.g., 'Type 2 Diabetes', 'Hypertension')"
    )
    parser.add_argument(
        "--pdf", 
        help="Path to PDF document containing medical literature"
    )
    parser.add_argument(
        "--additional-info", 
        help="Additional medical information or context"
    )
    parser.add_argument(
        "--output", 
        help="Output file path for the generated guidelines (default: prints to console)"
    )
    parser.add_argument(
        "--extract-only", 
        action="store_true",
        help="Only extract structured information from PDF without generating full guidelines"
    )

    args = parser.parse_args()

    # Initialize the medical metaprompt system
    try:
        medical_mp = MedicalMetaPrompt()
    except Exception as e:
        print(f"Error initializing Medical MetaPrompt: {e}")
        print("Make sure you have the required environment variables set (REGION_NAME, AWS credentials)")
        sys.exit(1)

    # Validate PDF file if provided
    if args.pdf and not os.path.exists(args.pdf):
        print(f"Error: PDF file '{args.pdf}' not found")
        sys.exit(1)

    try:
        if args.extract_only:
            # Extract structured information from PDF
            if not args.pdf:
                print("Error: PDF file required for extraction mode")
                sys.exit(1)
            
            task = f"Extract key clinical information from medical PDF focusing on {args.condition}"
            variables = "PDF_CONTENT\nEXTRACTION_FOCUS"
            
            prompt_template, extracted_vars = medical_mp(
                task, 
                variables, 
                pdf_path=args.pdf
            )
            
            # Create a simple extraction prompt
            extraction_prompt = f"""
            <PDF_CONTENT>
            {medical_mp.extract_text_from_pdf(args.pdf)}
            </PDF_CONTENT>
            
            <EXTRACTION_FOCUS>
            {args.condition}
            </EXTRACTION_FOCUS>
            
            {prompt_template}
            """
            
        else:
            # Generate full Epocrates-style guidelines
            task = f"Create an Epocrates-style clinical guideline for {args.condition} based on PDF content and current medical standards"
            variables = "CONDITION\nPDF_CONTENT\nADDITIONAL_INFO"
            
            prompt_template, extracted_vars = medical_mp(
                task, 
                variables, 
                pdf_path=args.pdf
            )
            
            # Create the full guideline prompt
            guideline_prompt = f"""
            <CONDITION>
            {args.condition}
            </CONDITION>
            
            <PDF_CONTENT>
            {medical_mp.extract_text_from_pdf(args.pdf) if args.pdf else "No PDF content provided"}
            </PDF_CONTENT>
            
            <ADDITIONAL_INFO>
            {args.additional_info or "No additional information provided"}
            </ADDITIONAL_INFO>
            
            {prompt_template}
            """

        # Output the generated prompt
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(guideline_prompt if not args.extract_only else extraction_prompt)
            print(f"Generated {'guidelines' if not args.extract_only else 'extraction'} saved to: {args.output}")
        else:
            print("=" * 80)
            print(f"GENERATED {'GUIDELINES' if not args.extract_only else 'EXTRACTION'} FOR: {args.condition.upper()}")
            print("=" * 80)
            print(guideline_prompt if not args.extract_only else extraction_prompt)

    except Exception as e:
        print(f"Error generating guidelines: {e}")
        sys.exit(1)


def interactive_mode():
    """Interactive mode for generating guidelines."""
    print("Medical MetaPrompt - Interactive Mode")
    print("=" * 50)
    
    try:
        medical_mp = MedicalMetaPrompt()
    except Exception as e:
        print(f"Error initializing Medical MetaPrompt: {e}")
        return

    while True:
        print("\nOptions:")
        print("1. Generate guidelines from PDF")
        print("2. Extract information from PDF")
        print("3. Generate guidelines without PDF")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "4":
            break
        elif choice == "1":
            condition = input("Enter medical condition: ").strip()
            pdf_path = input("Enter PDF file path (or press Enter to skip): ").strip()
            additional_info = input("Enter additional information (or press Enter to skip): ").strip()
            
            if pdf_path and not os.path.exists(pdf_path):
                print(f"Error: PDF file '{pdf_path}' not found")
                continue
                
            try:
                task = f"Create an Epocrates-style clinical guideline for {condition} based on PDF content and current medical standards"
                variables = "CONDITION\nPDF_CONTENT\nADDITIONAL_INFO"
                
                prompt_template, extracted_vars = medical_mp(
                    task, 
                    variables, 
                    pdf_path=pdf_path if pdf_path else None
                )
                
                print("\n" + "=" * 80)
                print(f"GENERATED GUIDELINES FOR: {condition.upper()}")
                print("=" * 80)
                print(prompt_template)
                
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "2":
            condition = input("Enter medical condition to focus extraction on: ").strip()
            pdf_path = input("Enter PDF file path: ").strip()
            
            if not os.path.exists(pdf_path):
                print(f"Error: PDF file '{pdf_path}' not found")
                continue
                
            try:
                task = f"Extract key clinical information from medical PDF focusing on {condition}"
                variables = "PDF_CONTENT\nEXTRACTION_FOCUS"
                
                prompt_template, extracted_vars = medical_mp(
                    task, 
                    variables, 
                    pdf_path=pdf_path
                )
                
                print("\n" + "=" * 80)
                print(f"EXTRACTED INFORMATION FOR: {condition.upper()}")
                print("=" * 80)
                print(prompt_template)
                
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "3":
            condition = input("Enter medical condition: ").strip()
            additional_info = input("Enter additional information (or press Enter to skip): ").strip()
            
            try:
                task = f"Create an Epocrates-style clinical guideline for {condition} based on current medical standards"
                variables = "CONDITION\nADDITIONAL_INFO"
                
                prompt_template, extracted_vars = medical_mp(
                    task, 
                    variables
                )
                
                print("\n" + "=" * 80)
                print(f"GENERATED GUIDELINES FOR: {condition.upper()}")
                print("=" * 80)
                print(prompt_template)
                
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run in interactive mode
        interactive_mode()
    else:
        # Run with command line arguments
        main()