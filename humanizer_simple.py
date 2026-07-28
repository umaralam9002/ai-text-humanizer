import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import random
import re
import warnings
warnings.filterwarnings("ignore")

class SimpleHumanizer:
    def __init__(self):
        # Load a reliable T5 model for paraphrasing
        try:
            self.model_name = "Vamsi/T5_Paraphrase_Paws"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=False)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.tokenizer = None
            self.model = None
    
    def add_variations(self, text):
        """Add simple variations to make text more natural"""
        # Common academic phrase variations
        replacements = {
            "shows that": ["demonstrates that", "indicates that", "reveals that", "suggests that"],
            "results in": ["leads to", "causes", "produces", "generates"],
            "due to": ["because of", "owing to", "as a result of", "on account of"],
            "in order to": ["to", "so as to", "with the aim of", "for the purpose of"],
            "as well as": ["and", "along with", "together with", "in addition to"],
            "therefore": ["thus", "hence", "consequently", "as a result"],
            "however": ["nevertheless", "nonetheless", "on the other hand", "yet"],
            "furthermore": ["moreover", "additionally", "in addition", "what is more"],
            "significant": ["notable", "considerable", "substantial", "important"],
            "important": ["crucial", "vital", "essential", "key"],
            "analyze": ["examine", "investigate", "study", "assess"],
            "demonstrate": ["show", "illustrate", "reveal", "display"],
            "utilize": ["use", "employ", "apply", "implement"]
        }
        
        result = text
        for original, alternatives in replacements.items():
            if original in result.lower():
                replacement = random.choice(alternatives)
                # Replace with case matching
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                result = pattern.sub(replacement, result, count=1)
        
        return result
    
    def vary_sentence_structure(self, text):
        """Simple sentence structure variations"""
        sentences = text.split('.')
        varied = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add some variety to sentence starters
            if random.random() < 0.3:
                starters = ["Notably, ", "Importantly, ", "Significantly, ", "Interestingly, "]
                if not any(sentence.startswith(s.strip()) for s in starters):
                    sentence = random.choice(starters) + sentence.lower()
            
            varied.append(sentence)
        
        return '. '.join(varied) + '.'
    
    def paraphrase_text(self, text):
        """Paraphrase using T5 model"""
        if not self.model or not self.tokenizer:
            return text
        
        try:
            # Split long text into chunks
            max_length = 400
            if len(text) > max_length:
                sentences = text.split('.')
                chunks = []
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) < max_length:
                        current_chunk += sentence + "."
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + "."
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                paraphrased_chunks = []
                for chunk in chunks:
                    para = self._paraphrase_chunk(chunk)
                    paraphrased_chunks.append(para)
                
                return " ".join(paraphrased_chunks)
            else:
                return self._paraphrase_chunk(text)
                
        except Exception as e:
            print(f"Paraphrasing error: {e}")
            return text
    
    def _paraphrase_chunk(self, text):
        """Paraphrase a single chunk"""
        try:
            # Prepare input
            input_text = f"paraphrase: {text}"
            input_ids = self.tokenizer.encode(
                input_text, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True
            )
            
            # Generate paraphrase
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=input_ids,
                    max_length=min(len(text.split()) + 50, 512),
                    num_beams=5,
                    num_return_sequences=1,
                    temperature=1.3,
                    top_k=50,
                    top_p=0.95,
                    do_sample=True,
                    early_stopping=True,
                    repetition_penalty=1.2
                )
            
            # Decode result
            paraphrased = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the result
            paraphrased = paraphrased.strip()
            if paraphrased and len(paraphrased) > 10:
                return paraphrased
            else:
                return text
                
        except Exception as e:
            print(f"Chunk paraphrasing error: {e}")
            return text

# Initialize humanizer
humanizer = SimpleHumanizer()

def humanize_text(input_text, complexity="Medium"):
    """Main humanization function"""
    if not input_text or not input_text.strip():
        return "Please enter some text to humanize."
    
    try:
        # Step 1: Paraphrase the text
        result = humanizer.paraphrase_text(input_text)
        
        # Step 2: Add variations based on complexity
        if complexity in ["Medium", "High"]:
            result = humanizer.add_variations(result)
        
        if complexity == "High":
            result = humanizer.vary_sentence_structure(result)
        
        # Step 3: Clean up formatting
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\s+([.!?,:;])', r'\1', result)
        
        # Ensure proper sentence capitalization
        sentences = result.split('. ')
        formatted_sentences = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                formatted_sentences.append(sentence)
        
        result = '. '.join(formatted_sentences)
        
        # Final cleanup
        if not result.endswith('.') and not result.endswith('!') and not result.endswith('?'):
            result += '.'
        
        return result
        
    except Exception as e:
        print(f"Humanization error: {e}")
        return f"Error processing text: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=humanize_text,
    inputs=[
        gr.Textbox(
            lines=10,
            placeholder="Paste your AI-generated or robotic text here...",
            label="Input Text",
            info="Enter the text you want to humanize"
        ),
        gr.Radio(
            choices=["Low", "Medium", "High"],
            value="Medium",
            label="Humanization Complexity",
            info="Low: Basic paraphrasing | Medium: + Vocabulary variations | High: + Structure changes"
        )
    ],
    outputs=gr.Textbox(
        label="Humanized Output",
        lines=10
    ),
    title="🤖➡️👨 AI Text Humanizer (Simple)",
    description="""
    **Transform robotic AI text into natural, human-like writing**
    
    This tool uses advanced paraphrasing techniques to make AI-generated text sound more natural and human-like.
    Perfect for academic papers, essays, reports, and any content that needs to pass AI detection tools.
    
    **Features:**
    ✅ Advanced T5-based paraphrasing  
    ✅ Vocabulary diversification  
    ✅ Sentence structure optimization  
    ✅ Academic tone preservation  
    ✅ Natural flow enhancement  
    """,
    examples=[
        [
            "The implementation of machine learning algorithms in data processing systems demonstrates significant improvements in efficiency and accuracy metrics.",
            "Medium"
        ],
        [
            "Artificial intelligence technologies are increasingly being utilized across various industries to enhance operational capabilities and drive innovation.",
            "High"
        ]
    ],
    theme="soft"
)

if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7861,
        debug=True
    )
