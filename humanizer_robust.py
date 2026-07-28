import gradio as gr
import random
import re
import warnings
warnings.filterwarnings("ignore")

class RobustHumanizer:
    def __init__(self):
        """Initialize with robust fallback techniques that don't require external models"""
        self.academic_replacements = {
            # Common AI patterns to humanize
            "demonstrates": ["shows", "reveals", "indicates", "illustrates", "displays"],
            "significant": ["notable", "considerable", "substantial", "important", "remarkable"],
            "utilize": ["use", "employ", "apply", "implement", "make use of"],
            "implement": ["apply", "use", "put into practice", "carry out", "execute"],
            "generate": ["create", "produce", "develop", "form", "make"],
            "facilitate": ["help", "enable", "assist", "support", "aid"],
            "optimize": ["improve", "enhance", "refine", "perfect", "better"],
            "analyze": ["examine", "study", "investigate", "assess", "evaluate"],
            "therefore": ["thus", "hence", "consequently", "as a result", "for this reason"],
            "however": ["nevertheless", "nonetheless", "yet", "on the other hand", "but"],
            "furthermore": ["moreover", "additionally", "in addition", "what is more", "besides"],
            "substantial": ["significant", "considerable", "notable", "important", "major"],
            "subsequently": ["later", "then", "afterward", "following this", "next"],
            "approximately": ["about", "roughly", "around", "nearly", "close to"],
            "numerous": ["many", "several", "multiple", "various", "a number of"],
            "encompasses": ["includes", "covers", "contains", "involves", "comprises"],
            "methodology": ["method", "approach", "technique", "procedure", "process"],
            "comprehensive": ["complete", "thorough", "extensive", "detailed", "full"],
            "indicates": ["shows", "suggests", "points to", "reveals", "demonstrates"],
            "established": ["set up", "created", "formed", "developed", "built"]
        }
        
        self.sentence_starters = [
            "Notably,", "Importantly,", "Significantly,", "Interestingly,", 
            "Furthermore,", "Moreover,", "Additionally,", "In contrast,",
            "Similarly,", "Nevertheless,", "Consequently,", "As a result,",
            "In particular,", "Specifically,", "Generally,", "Typically,"
        ]
        
        self.hedging_phrases = [
            "appears to", "seems to", "tends to", "suggests that", "indicates that",
            "may well", "might be", "could be", "potentially", "presumably",
            "arguably", "to some extent", "in many cases", "generally speaking",
            "it is likely that", "evidence suggests", "research indicates"
        ]
        
        self.connecting_phrases = [
            "In light of this", "Building upon this", "This finding suggests",
            "It is worth noting that", "This observation", "These results",
            "The evidence indicates", "This approach", "The data reveals",
            "Research shows", "Studies demonstrate", "Analysis reveals"
        ]

    def split_into_sentences(self, text):
        """Simple sentence splitting"""
        # Split by periods, but be careful with abbreviations
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char == '.' and len(current) > 10:
                # Check if this looks like end of sentence
                next_chars = text[text.find(current) + len(current):text.find(current) + len(current) + 3]
                if next_chars.strip() and (next_chars[0].isupper() or next_chars.strip()[0].isupper()):
                    sentences.append(current.strip())
                    current = ""
        
        if current.strip():
            sentences.append(current.strip())
        
        return [s for s in sentences if len(s.strip()) > 5]

    def vary_vocabulary(self, text):
        """Replace words with alternatives"""
        result = text
        
        for original, alternatives in self.academic_replacements.items():
            if original.lower() in result.lower():
                replacement = random.choice(alternatives)
                # Case-sensitive replacement
                pattern = re.compile(re.escape(original), re.IGNORECASE)
                result = pattern.sub(replacement, result, count=1)
        
        return result

    def add_natural_flow(self, text):
        """Add natural academic connectors and hedging"""
        sentences = self.split_into_sentences(text)
        if not sentences:
            return text
        
        modified_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add hedging to some sentences
            if random.random() < 0.3 and not any(hedge in sentence.lower() for hedge in self.hedging_phrases):
                if sentence.lower().startswith(('the ', 'this ', 'these ', 'that ')):
                    hedge = random.choice(self.hedging_phrases)
                    words = sentence.split()
                    if len(words) > 2:
                        words.insert(2, hedge)
                        sentence = " ".join(words)
            
            # Add connecting phrases for flow
            if i > 0 and random.random() < 0.4:
                connector = random.choice(self.connecting_phrases)
                sentence = f"{connector}, {sentence.lower()}"
            
            # Sometimes start with variety
            elif i > 0 and random.random() < 0.2:
                starter = random.choice(self.sentence_starters)
                sentence = f"{starter} {sentence.lower()}"
            
            modified_sentences.append(sentence)
        
        return " ".join(modified_sentences)

    def restructure_sentences(self, text):
        """Modify sentence structures for variety"""
        sentences = self.split_into_sentences(text)
        restructured = []
        
        for sentence in sentences:
            words = sentence.split()
            
            # For long sentences, sometimes break them up
            if len(words) > 25 and random.random() < 0.5:
                # Find a good break point
                break_words = ['and', 'but', 'which', 'that', 'because', 'since', 'while']
                for i, word in enumerate(words[10:20], 10):  # Look in middle section
                    if word.lower() in break_words:
                        part1 = " ".join(words[:i]) + "."
                        part2 = " ".join(words[i+1:])
                        if len(part2) > 10:  # Only if second part is substantial
                            part2 = part2[0].upper() + part2[1:] if part2 else part2
                            restructured.extend([part1, part2])
                            break
                else:
                    restructured.append(sentence)
            else:
                restructured.append(sentence)
        
        return " ".join(restructured)

    def clean_and_format(self, text):
        """Clean up the text formatting"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Fix capitalization
        sentences = self.split_into_sentences(text)
        formatted = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                
                # Ensure proper ending
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                
                formatted.append(sentence)
        
        return " ".join(formatted)

    def humanize_text(self, text, intensity="medium"):
        """Main humanization function"""
        if not text or len(text.strip()) < 10:
            return "Please enter substantial text to humanize (at least 10 characters)."
        
        result = text.strip()
        
        try:
            # Apply different levels of humanization
            if intensity.lower() in ["light", "low"]:
                # Just vocabulary changes
                result = self.vary_vocabulary(result)
                
            elif intensity.lower() in ["medium", "moderate"]:
                # Vocabulary + natural flow
                result = self.vary_vocabulary(result)
                result = self.add_natural_flow(result)
                
            elif intensity.lower() in ["heavy", "high", "maximum"]:
                # All techniques
                result = self.vary_vocabulary(result)
                result = self.add_natural_flow(result)
                result = self.restructure_sentences(result)
            
            # Always clean up formatting
            result = self.clean_and_format(result)
            
            return result if result and len(result) > 10 else text
            
        except Exception as e:
            print(f"Humanization error: {e}")
            return f"Error processing text. Please try again with different input."

# Initialize the humanizer
humanizer = RobustHumanizer()

def process_text(input_text, humanization_level):
    """Process the input text"""
    return humanizer.humanize_text(input_text, humanization_level)

# Create Gradio interface
demo = gr.Interface(
    fn=process_text,
    inputs=[
        gr.Textbox(
            lines=12,
            placeholder="Paste your AI-generated or robotic text here...\n\nExample: 'The implementation of machine learning algorithms demonstrates significant improvements in computational efficiency and accuracy metrics across various benchmark datasets.'",
            label="Input Text",
            info="Enter the text you want to make more natural and human-like"
        ),
        gr.Radio(
            choices=["Light", "Medium", "Heavy"],
            value="Medium",
            label="Humanization Intensity",
            info="Light: Basic vocabulary changes | Medium: + Natural flow | Heavy: + Sentence restructuring"
        )
    ],
    outputs=gr.Textbox(
        label="Humanized Output",
        lines=12,
        info="Copy this natural, human-like text"
    ),
    title="🤖➡️👨 Robust AI Text Humanizer",
    description="""
    **Transform robotic AI text into natural, human-like academic writing**
    
    This tool uses advanced linguistic techniques to make AI-generated text sound more natural and human-like.
    Perfect for academic papers, research reports, essays, and professional documents.
    
    ✅ **No external dependencies** - Always works  
    ✅ **Advanced vocabulary variation** - Natural word choices  
    ✅ **Sentence flow optimization** - Smooth transitions  
    ✅ **Academic tone preservation** - Maintains credibility  
    ✅ **Structure diversification** - Varied sentence patterns  
    ✅ **Natural connectors** - Academic linking phrases  
    """,
    examples=[
        [
            "The implementation of machine learning algorithms demonstrates significant improvements in computational efficiency and accuracy metrics across various benchmark datasets. These results indicate that the optimization of neural network architectures can facilitate enhanced performance in predictive analytics applications.",
            "Medium"
        ],
        [
            "Artificial intelligence technologies are increasingly being utilized across numerous industries to optimize operational processes and generate innovative solutions. The comprehensive analysis of these systems reveals substantial benefits in terms of efficiency and accuracy.",
            "Heavy"
        ],
        [
            "The research methodology encompasses a systematic approach to data collection and analysis, utilizing advanced statistical techniques to ensure robust and reliable results that demonstrate the effectiveness of the proposed framework.",
            "Light"
        ]
    ],
    theme="soft",
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    """,
    article="""
    ### 🎯 **How to Use:**
    1. **Paste your AI-generated text** in the input box
    2. **Choose intensity level** based on how much change you want
    3. **Click Submit** and get natural, human-like output
    4. **Copy the result** and use it in your work
    
    ### 💡 **Pro Tips:**
    - Use **Light** for minimal changes while preserving original structure
    - Use **Medium** for balanced humanization with natural flow
    - Use **Heavy** for maximum transformation and sentence variety
    - Always review the output to ensure it maintains your intended meaning
    - For best results, input complete sentences and paragraphs
    
    ### ⚖️ **Ethical Usage:**
    This tool is designed to improve writing quality and natural expression.  
    Please use responsibly and maintain academic integrity.
    """,
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7862,
        debug=True,
        show_error=True
    )
