import gradio as gr
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import random
import re
import warnings
warnings.filterwarnings("ignore")

class BatchHumanizer:
    def __init__(self):
        try:
            self.model_name = "Vamsi/T5_Paraphrase_Paws"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=False)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            print("✅ Batch Humanizer model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.tokenizer = None
            self.model = None
    
    def humanize_single_text(self, text, strength="medium"):
        """Humanize a single piece of text"""
        if not self.model or not self.tokenizer:
            return self.fallback_humanize(text)
        
        try:
            # Paraphrase using T5
            input_text = f"paraphrase: {text}"
            input_ids = self.tokenizer.encode(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            # Adjust parameters based on strength
            if strength == "light":
                temp, top_p = 1.1, 0.9
            elif strength == "heavy":
                temp, top_p = 1.5, 0.95
            else:  # medium
                temp, top_p = 1.3, 0.92
            
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=input_ids,
                    max_length=min(len(text.split()) + 50, 512),
                    num_beams=5,
                    temperature=temp,
                    top_p=top_p,
                    do_sample=True,
                    early_stopping=True,
                    repetition_penalty=1.2
                )
            
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Additional humanization
            if strength in ["medium", "heavy"]:
                result = self.add_natural_variations(result)
            
            return self.clean_text(result) if result and len(result) > 10 else text
            
        except Exception as e:
            print(f"Error humanizing text: {e}")
            return self.fallback_humanize(text)
    
    def fallback_humanize(self, text):
        """Simple fallback humanization without model"""
        # Basic word replacements
        replacements = {
            "utilize": "use", "demonstrate": "show", "facilitate": "help",
            "optimize": "improve", "implement": "apply", "generate": "create",
            "therefore": "thus", "however": "yet", "furthermore": "also"
        }
        
        result = text
        for old, new in replacements.items():
            result = re.sub(r'\b' + old + r'\b', new, result, flags=re.IGNORECASE)
        
        return result
    
    def add_natural_variations(self, text):
        """Add natural language variations"""
        # Academic connectors
        connectors = [
            "Moreover", "Furthermore", "Additionally", "In contrast",
            "Similarly", "Consequently", "Nevertheless", "Notably"
        ]
        
        sentences = text.split('.')
        varied = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Sometimes add connectors
            if i > 0 and random.random() < 0.2:
                connector = random.choice(connectors)
                sentence = f"{connector}, {sentence.lower()}"
            
            varied.append(sentence)
        
        return '. '.join(varied) + '.' if varied else text
    
    def clean_text(self, text):
        """Clean and format text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        
        # Capitalize sentences
        sentences = text.split('. ')
        formatted = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                formatted.append(sentence)
        
        result = '. '.join(formatted)
        if not result.endswith(('.', '!', '?')):
            result += '.'
            
        return result

# Initialize humanizer
batch_humanizer = BatchHumanizer()

def process_text_input(text_input, strength):
    """Process single text input"""
    if not text_input or not text_input.strip():
        return "Please enter some text to humanize."
    
    return batch_humanizer.humanize_single_text(text_input, strength.lower())

def process_file_upload(file, strength):
    """Process uploaded file"""
    if file is None:
        return "Please upload a file.", None
    
    try:
        # Read the file
        if file.name.endswith('.txt'):
            with open(file.name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into paragraphs or sentences for processing
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            humanized_paragraphs = []
            for para in paragraphs:
                if len(para) > 50:  # Only process substantial paragraphs
                    humanized = batch_humanizer.humanize_single_text(para, strength.lower())
                    humanized_paragraphs.append(humanized)
                else:
                    humanized_paragraphs.append(para)
            
            result = '\n\n'.join(humanized_paragraphs)
            
            # Save to new file
            output_filename = file.name.replace('.txt', '_humanized.txt')
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(result)
            
            return result, output_filename
            
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file.name)
            
            # Assume the text column is named 'text' or the first column
            text_column = 'text' if 'text' in df.columns else df.columns[0]
            
            # Humanize each text entry
            df['humanized'] = df[text_column].apply(
                lambda x: batch_humanizer.humanize_single_text(str(x), strength.lower()) if pd.notna(x) else x
            )
            
            # Save to new CSV
            output_filename = file.name.replace('.csv', '_humanized.csv')
            df.to_csv(output_filename, index=False)
            
            return f"Processed {len(df)} entries. Check the 'humanized' column.", output_filename
        
        else:
            return "Unsupported file format. Please upload .txt or .csv files.", None
            
    except Exception as e:
        return f"Error processing file: {str(e)}", None

# Create Gradio interface with tabs
with gr.Blocks(theme="soft", title="AI Text Humanizer Pro") as demo:
    gr.Markdown("""
    # 🤖➡️👨 AI Text Humanizer Pro
    
    **Advanced tool to transform robotic AI-generated text into natural, human-like writing**
    
    Perfect for:
    - 📝 Academic papers and essays
    - 📊 Research reports  
    - 📄 Business documents
    - 💼 Professional content
    - 🔍 Bypassing AI detection tools
    """)
    
    with gr.Tabs():
        # Single Text Tab
        with gr.TabItem("Single Text"):
            gr.Markdown("### Humanize Individual Text")
            
            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        lines=12,
                        placeholder="Paste your AI-generated text here...",
                        label="Input Text",
                        info="Enter the text you want to humanize"
                    )
                    
                    strength_single = gr.Radio(
                        choices=["Light", "Medium", "Heavy"],
                        value="Medium",
                        label="Humanization Strength"
                    )
                    
                    process_btn = gr.Button("🚀 Humanize Text", variant="primary")
                
                with gr.Column(scale=2):
                    text_output = gr.Textbox(
                        lines=12,
                        label="Humanized Output"
                    )
            
            # Examples
            gr.Examples(
                examples=[
                    ["The implementation of artificial intelligence algorithms demonstrates significant improvements in computational efficiency and accuracy metrics across various benchmark datasets.", "Medium"],
                    ["Machine learning models exhibit superior performance characteristics when evaluated against traditional statistical approaches in predictive analytics applications.", "Heavy"],
                    ["The research methodology utilized in this study involves comprehensive data collection and analysis procedures to ensure robust and reliable results.", "Light"]
                ],
                inputs=[text_input, strength_single],
                outputs=text_output,
                fn=process_text_input
            )
        
        # Batch Processing Tab
        with gr.TabItem("Batch Processing"):
            gr.Markdown("### Process Files in Batch")
            gr.Markdown("Upload .txt or .csv files to humanize multiple texts at once")
            
            with gr.Row():
                with gr.Column():
                    file_input = gr.File(
                        label="Upload File (.txt or .csv)",
                        file_types=[".txt", ".csv"]
                    )
                    
                    strength_batch = gr.Radio(
                        choices=["Light", "Medium", "Heavy"],
                        value="Medium",
                        label="Humanization Strength"
                    )
                    
                    process_file_btn = gr.Button("🔄 Process File", variant="primary")
                
                with gr.Column():
                    file_output = gr.Textbox(
                        lines=10,
                        label="Processing Results"
                    )
                    
                    download_file = gr.File(
                        label="Download Processed File",
                        visible=False
                    )
        
        # Settings Tab
        with gr.TabItem("Settings & Info"):
            gr.Markdown("""
            ### How it works:
            
            1. **Light Humanization**: Basic paraphrasing with minimal changes
            2. **Medium Humanization**: Paraphrasing + vocabulary variations  
            3. **Heavy Humanization**: All techniques + sentence structure changes
            
            ### Features:
            - ✅ Advanced T5-based paraphrasing
            - ✅ Natural vocabulary diversification
            - ✅ Sentence structure optimization
            - ✅ Academic tone preservation
            - ✅ Batch file processing
            - ✅ Multiple output formats
            
            ### Supported Formats:
            - **Text files (.txt)**: Processes paragraph by paragraph
            - **CSV files (.csv)**: Adds 'humanized' column with processed text
            
            ### Tips for best results:
            - Use complete sentences and paragraphs
            - Avoid very short fragments
            - Choose appropriate humanization strength
            - Review output for context accuracy
            """)
    
    # Event handlers
    process_btn.click(
        fn=process_text_input,
        inputs=[text_input, strength_single],
        outputs=text_output
    )
    
    process_file_btn.click(
        fn=process_file_upload,
        inputs=[file_input, strength_batch],
        outputs=[file_output, download_file]
    )

if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7862,
        debug=True
    )
