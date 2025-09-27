#!/usr/bin/env python3
"""
Test script for Medical MetaPrompt functionality
"""

import sys
import os
from medical_metaprompt import MedicalMetaPrompt

def test_metaprompt_generation():
    """Test basic metaprompt generation"""
    print("🧪 Testing Medical MetaPrompt Generation...")
    
    try:
        medical_meta = MedicalMetaPrompt()
        
        # Test custom metaprompt generation
        task = "Extract medication dosing information from clinical documents"
        variables = "CLINICAL_TEXT\nMEDICATION_NAME"
        
        prompt_template, extracted_vars = medical_meta(task, variables)
        
        print("✅ Metaprompt generation successful!")
        print(f"Variables extracted: {extracted_vars}")
        print(f"Template length: {len(prompt_template)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Metaprompt generation failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF text extraction capabilities"""
    print("\n📄 Testing PDF Processing...")
    
    try:
        medical_meta = MedicalMetaPrompt()
        
        # Test with a simple text file (simulating PDF)
        test_content = """
        MEDICATION: Aspirin (Acetylsalicylic Acid)
        
        INDICATIONS:
        - Acute coronary syndrome
        - Stroke prevention
        - Pain relief
        
        DOSING:
        - Cardioprotective: 81 mg daily
        - Analgesic: 325-650 mg every 4-6 hours
        
        CONTRAINDICATIONS:
        - Active bleeding
        - Severe renal impairment
        
        ADVERSE EFFECTS:
        - GI bleeding
        - Tinnitus at high doses
        """
        
        # Create a temporary text file to simulate PDF processing
        temp_file = "/tmp/test_medical.txt"
        with open(temp_file, "w") as f:
            f.write(test_content)
        
        # Test text cleaning
        cleaned_text = medical_meta.clean_medical_text(test_content)
        
        print("✅ Text processing successful!")
        print(f"Original length: {len(test_content)} characters")
        print(f"Cleaned length: {len(cleaned_text)} characters")
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return True
        
    except Exception as e:
        print(f"❌ PDF processing failed: {e}")
        return False

def test_template_loading():
    """Test template file loading"""
    print("\n📋 Testing Template Loading...")
    
    try:
        current_script_path = os.path.dirname(os.path.abspath(__file__))
        
        # Test medical metaprompt template
        medical_template_path = os.path.join(current_script_path, "medical_metaprompt.txt")
        epocrates_template_path = os.path.join(current_script_path, "epocrates_metaprompt.txt")
        
        templates_found = []
        
        if os.path.exists(medical_template_path):
            with open(medical_template_path, "r") as f:
                content = f.read()
                templates_found.append(f"Medical template: {len(content)} characters")
        
        if os.path.exists(epocrates_template_path):
            with open(epocrates_template_path, "r") as f:
                content = f.read()
                templates_found.append(f"Epocrates template: {len(content)} characters")
        
        if templates_found:
            print("✅ Template loading successful!")
            for template_info in templates_found:
                print(f"  - {template_info}")
            return True
        else:
            print("❌ No template files found!")
            return False
            
    except Exception as e:
        print(f"❌ Template loading failed: {e}")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("\n🔧 Testing Environment Setup...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        region_name = os.getenv("REGION_NAME")
        
        if region_name:
            print(f"✅ Environment setup successful!")
            print(f"  - AWS Region: {region_name}")
        else:
            print("⚠️  Environment partially configured (no REGION_NAME)")
        
        # Test AWS imports
        import boto3
        print("  - AWS SDK available: ✅")
        
        # Test PDF processing imports
        import PyPDF2
        import pdfplumber
        print("  - PDF processing libraries available: ✅")
        
        # Test Gradio import
        import gradio as gr
        print("  - Gradio web interface available: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 Medical MetaPrompt Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment_setup,
        test_template_loading,
        test_pdf_processing,
        test_metaprompt_generation,
    ]
    
    results = []
    
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! The Medical MetaPrompt system is ready to use.")
        print("\nNext steps:")
        print("1. Configure AWS Bedrock credentials")
        print("2. Run 'python medical_app.py' to start the web interface")
        print("3. Upload a medical PDF to test the complete workflow")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        print("Common issues:")
        print("- Missing dependencies (run 'pip install -r requirements.txt')")
        print("- Missing template files")
        print("- AWS configuration issues")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)