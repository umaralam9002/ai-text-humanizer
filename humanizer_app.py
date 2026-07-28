import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import random
import re
import warnings
import math
from collections import Counter
warnings.filterwarnings("ignore")

# Import NLTK with error handling
try:
    import nltk
    import textstat
    from nltk.corpus import wordnet
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
except ImportError as e:
    print(f"NLTK import error: {e}")
    NLTK_AVAILABLE = False
    # Fallback imports
    import textstat

# Download required NLTK data if available
if NLTK_AVAILABLE:
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        print("Downloading punkt_tab...")
        nltk.download('punkt_tab')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading punkt...")
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading wordnet...")
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        print("Downloading omw-1.4...")
        nltk.download('omw-1.4')

# Load multiple models for diverse paraphrasing
models = {
    "t5_paraphrase": {
        "model_name": "Vamsi/T5_Paraphrase_Paws",
        "tokenizer": None,
        "model": None
    },
    "pegasus": {
        "model_name": "tuner007/pegasus_paraphrase",
        "tokenizer": None,
        "model": None
    }
}

# Initialize models
for key, model_info in models.items():
    try:
        model_info["tokenizer"] = AutoTokenizer.from_pretrained(model_info["model_name"])
        model_info["model"] = AutoModelForSeq2SeqLM.from_pretrained(model_info["model_name"])
        print(f"Loaded {key} model successfully")
    except Exception as e:
        print(f"Failed to load {key}: {e}")

class AdvancedHumanizer:
    def __init__(self):
        self.transition_words = [
            "However", "Nevertheless", "Furthermore", "Moreover", "Additionally",
            "Consequently", "Therefore", "Thus", "In contrast", "Similarly",
            "On the other hand", "Meanwhile", "Subsequently", "Notably",
            "Importantly", "Significantly", "Interestingly", "Remarkably"
        ]
        
        self.hedging_phrases = [
            "appears to", "seems to", "tends to", "suggests that", "indicates that",
            "may well", "might be", "could be", "potentially", "presumably",
            "arguably", "to some extent", "in many cases", "generally speaking"
        ]
        
        self.academic_connectors = [
            "In light of this", "Building upon this", "This finding suggests",
            "It is worth noting that", "This observation", "These results",
            "The evidence indicates", "This approach", "The data reveals"
        ]

    def add_natural_variations(self, text):
        """Add natural linguistic variations to make text less robotic"""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            # Fallback: simple sentence splitting
            sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        varied_sentences = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.endswith('.') and NLTK_AVAILABLE:
                sentence += '.'
            elif not sentence.endswith('.') and not NLTK_AVAILABLE:
                sentence += '.'
                
            # Randomly add hedging language
            if random.random() < 0.3 and not any(phrase in sentence.lower() for phrase in self.hedging_phrases):
                hedge = random.choice(self.hedging_phrases)
                if sentence.startswith("The ") or sentence.startswith("This "):
                    sentence = sentence.replace("The ", f"The {hedge} ", 1)
                    sentence = sentence.replace("This ", f"This {hedge} ", 1)
            
            # Add transitional phrases for flow
            if i > 0 and random.random() < 0.4:
                connector = random.choice(self.academic_connectors)
                sentence = f"{connector}, {sentence.lower()}"
            
            varied_sentences.append(sentence)
        
        return " ".join(varied_sentences)

    def diversify_vocabulary(self, text):
        """Replace common words with synonyms for variation"""
        if not NLTK_AVAILABLE:
            # Fallback: simple word replacements
            replacements = {
                "significant": "notable", "important": "crucial", "demonstrate": "show",
                "utilize": "use", "implement": "apply", "generate": "create",
                "facilitate": "help", "optimize": "improve", "analyze": "examine"
            }
            result = text
            for old, new in replacements.items():
                result = re.sub(r'\b' + old + r'\b', new, result, flags=re.IGNORECASE)
            return result
        
        words = word_tokenize(text)
        result = []
        
        for word in words:
            if word.isalpha() and len(word) > 4 and random.random() < 0.2:
                synonyms = []
                for syn in wordnet.synsets(word):
                    for lemma in syn.lemmas():
                        if lemma.name() != word and '_' not in lemma.name():
                            synonyms.append(lemma.name())
                
                if synonyms:
                    replacement = random.choice(synonyms[:3])  # Use top 3 synonyms
                    result.append(replacement)
                else:
                    result.append(word)
            else:
                result.append(word)
        
        return " ".join(result)

    def adjust_sentence_structure(self, text):
        """Modify sentence structures for more natural flow"""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            # Fallback: simple sentence splitting
            sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        modified = []
        
        for sentence in sentences:
            # Randomly split long sentences
            if len(sentence.split()) > 20 and random.random() < 0.4:
                words = sentence.split()
                mid_point = len(words) // 2
                # Find a good breaking point near the middle
                for i in range(mid_point - 3, mid_point + 3):
                    if i < len(words) and words[i].rstrip('.,').lower() in ['and', 'but', 'which', 'that']:
                        part1 = " ".join(words[:i]) + "."
                        part2 = " ".join(words[i+1:])
                        if part2:
                            part2 = part2[0].upper() + part2[1:]
                        modified.extend([part1, part2])
                        break
                else:
                    modified.append(sentence)
            else:
                modified.append(sentence)
        
        return " ".join(modified)

    def paraphrase_with_multiple_models(self, text, chunk_size=300):
        """Use multiple models to paraphrase different parts of the text"""
        # Check if any models are available
        available_models = [k for k, v in models.items() if v["model"] is not None]
        if not available_models:
            # No models available, use fallback humanization
            return self.fallback_humanization(text)
        
        if len(text) <= chunk_size:
            return self.paraphrase_single_chunk(text)
        
        # Split into chunks
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Paraphrase each chunk with different models
        paraphrased_chunks = []
        for i, chunk in enumerate(chunks):
            paraphrased = self.paraphrase_single_chunk(chunk, model_choice=i % len(available_models))
            paraphrased_chunks.append(paraphrased)
        
        return " ".join(paraphrased_chunks)

    def fallback_humanization(self, text):
        """Fallback humanization when no AI models are available"""
        # Use the vocabulary diversification and natural variations
        result = self.diversify_vocabulary(text)
        result = self.add_natural_variations(result)
        return result

    def paraphrase_single_chunk(self, text, model_choice=0):
        """Paraphrase a single chunk of text"""
        available_models = [k for k, v in models.items() if v["model"] is not None]
        if not available_models:
            # No models available, use fallback
            return self.fallback_humanization(text)
        
        model_key = available_models[model_choice % len(available_models)]
        model_info = models[model_key]
        
        try:
            if model_key == "t5_paraphrase":
                input_ids = model_info["tokenizer"].encode(
                    f"paraphrase: {text}",
                    return_tensors="pt",
                    max_length=512,
                    truncation=True
                )
                outputs = model_info["model"].generate(
                    input_ids=input_ids,
                    max_length=len(text.split()) + 50,
                    num_beams=5,
                    num_return_sequences=1,
                    temperature=1.2,
                    top_k=50,
                    top_p=0.92,
                    do_sample=True,
                    early_stopping=True
                )
                result = model_info["tokenizer"].decode(outputs[0], skip_special_tokens=True)
                
            elif model_key == "pegasus":
                input_ids = model_info["tokenizer"].encode(
                    text,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True
                )
                outputs = model_info["model"].generate(
                    input_ids=input_ids,
                    max_length=len(text.split()) + 30,
                    num_beams=4,
                    temperature=1.1,
                    top_p=0.9,
                    do_sample=True
                )
                result = model_info["tokenizer"].decode(outputs[0], skip_special_tokens=True)
            
            return result if result and len(result) > 10 else self.fallback_humanization(text)
        except Exception as e:
            print(f"Error with {model_key}: {e}")
            return self.fallback_humanization(text)

class AIDetector:
    def __init__(self):
        """Initialize AI detection patterns and thresholds"""
        # Common AI-generated text patterns
        self.ai_phrases = [
            "demonstrates significant", "substantial improvements", "comprehensive analysis",
            "furthermore", "moreover", "additionally", "consequently", "therefore",
            "implementation of", "utilization of", "optimization of", "enhancement of",
            "facilitate", "demonstrate", "indicate", "substantial", "comprehensive",
            "significant improvements", "notable enhancements", "effective approach",
            "robust methodology", "systematic approach", "extensive evaluation",
            "empirical results", "experimental validation", "performance metrics",
            "benchmark datasets", "state-of-the-art", "cutting-edge", "novel approach",
            "innovative solution", "groundbreaking", "revolutionary", "paradigm shift"
        ]
        
        # Academic buzzwords that AI overuses
        self.overused_academic_words = [
            "significant", "substantial", "comprehensive", "extensive", "robust",
            "novel", "innovative", "efficient", "effective", "optimal", "superior",
            "enhanced", "improved", "advanced", "sophisticated", "cutting-edge",
            "state-of-the-art", "groundbreaking", "revolutionary", "paradigm"
        ]
        
        # Transition words AI uses excessively
        self.excessive_transitions = [
            "furthermore", "moreover", "additionally", "consequently", "therefore",
            "thus", "hence", "nevertheless", "nonetheless", "however"
        ]
        
        # Formal structures AI tends to overuse
        self.formal_patterns = [
            r"the implementation of \w+",
            r"the utilization of \w+",
            r"in order to \w+",
            r"it is important to note that",
            r"it should be emphasized that",
            r"it can be observed that",
            r"the results demonstrate that",
            r"the findings indicate that"
        ]

    def calculate_ai_probability(self, text):
        """Calculate the probability that text is AI-generated"""
        if not text or len(text.strip()) < 50:
            return {"probability": 0, "confidence": "Low", "details": {"error": "Text too short for analysis"}}
        
        scores = {}
        
        # 1. Check for AI phrases
        scores['ai_phrases'] = self._check_ai_phrases(text)
        
        # 2. Check vocabulary repetition
        scores['vocab_repetition'] = self._check_vocabulary_repetition(text)
        
        # 3. Check sentence structure patterns
        scores['structure_patterns'] = self._check_structure_patterns(text)
        
        # 4. Check transition word overuse
        scores['transition_overuse'] = self._check_transition_overuse(text)
        
        # 5. Check formal pattern overuse
        scores['formal_patterns'] = self._check_formal_patterns(text)
        
        # 6. Check sentence length consistency
        scores['sentence_consistency'] = self._check_sentence_consistency(text)
        
        # 7. Check readability patterns
        scores['readability'] = self._check_readability_patterns(text)
        
        # Calculate weighted final score
        weights = {
            'ai_phrases': 0.2,
            'vocab_repetition': 0.15,
            'structure_patterns': 0.15,
            'transition_overuse': 0.15,
            'formal_patterns': 0.15,
            'sentence_consistency': 0.1,
            'readability': 0.1
        }
        
        final_score = sum(scores[key] * weights[key] for key in weights)
        final_score = min(100, max(0, final_score))  # Clamp between 0-100
        
        # Determine confidence level
        if final_score >= 80:
            confidence = "Very High"
            verdict = "Likely AI-Generated"
        elif final_score >= 60:
            confidence = "High"
            verdict = "Probably AI-Generated"
        elif final_score >= 40:
            confidence = "Medium"
            verdict = "Possibly AI-Generated"
        elif final_score >= 20:
            confidence = "Low"
            verdict = "Probably Human-Written"
        else:
            confidence = "Very Low"
            verdict = "Likely Human-Written"
        
        return {
            "probability": round(final_score, 1),
            "confidence": confidence,
            "verdict": verdict,
            "details": {
                "ai_phrases_score": round(scores['ai_phrases'], 1),
                "vocabulary_repetition": round(scores['vocab_repetition'], 1),
                "structure_patterns": round(scores['structure_patterns'], 1),
                "transition_overuse": round(scores['transition_overuse'], 1),
                "formal_patterns": round(scores['formal_patterns'], 1),
                "sentence_consistency": round(scores['sentence_consistency'], 1),
                "readability_score": round(scores['readability'], 1)
            }
        }
    
    def _check_ai_phrases(self, text):
        """Check for common AI-generated phrases"""
        text_lower = text.lower()
        phrase_count = sum(1 for phrase in self.ai_phrases if phrase in text_lower)
        words = len(text.split())
        
        if words == 0:
            return 0
        
        # Score based on phrase density
        density = (phrase_count / words) * 1000  # Per 1000 words
        return min(100, density * 10)  # Scale to 0-100
    
    def _check_vocabulary_repetition(self, text):
        """Check for repetitive vocabulary typical of AI"""
        words = [word.lower().strip('.,!?;:') for word in text.split() if word.isalpha()]
        if len(words) < 10:
            return 0
        
        word_counts = Counter(words)
        overused_count = sum(1 for word in self.overused_academic_words if word_counts.get(word, 0) > 1)
        
        # Calculate repetition score
        total_overused_words = len(self.overused_academic_words)
        repetition_ratio = overused_count / total_overused_words if total_overused_words > 0 else 0
        
        return min(100, repetition_ratio * 200)  # Scale to 0-100
    
    def _check_structure_patterns(self, text):
        """Check for repetitive sentence structures"""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 3:
            return 0
        
        # Check for similar sentence starters
        starters = [s.split()[:3] for s in sentences if len(s.split()) >= 3]
        starter_counts = Counter([' '.join(starter) for starter in starters])
        
        repeated_starters = sum(1 for count in starter_counts.values() if count > 1)
        repetition_ratio = repeated_starters / len(sentences) if len(sentences) > 0 else 0
        
        return min(100, repetition_ratio * 150)  # Scale to 0-100
    
    def _check_transition_overuse(self, text):
        """Check for excessive use of transition words"""
        text_lower = text.lower()
        transition_count = sum(1 for transition in self.excessive_transitions if transition in text_lower)
        words = len(text.split())
        
        if words == 0:
            return 0
        
        # Score based on transition density
        density = (transition_count / words) * 100  # Percentage
        return min(100, density * 20)  # Scale to 0-100
    
    def _check_formal_patterns(self, text):
        """Check for overly formal patterns typical of AI"""
        pattern_count = 0
        text_lower = text.lower()
        
        for pattern in self.formal_patterns:
            matches = re.findall(pattern, text_lower)
            pattern_count += len(matches)
        
        words = len(text.split())
        if words == 0:
            return 0
        
        density = (pattern_count / words) * 1000  # Per 1000 words
        return min(100, density * 15)  # Scale to 0-100
    
    def _check_sentence_consistency(self, text):
        """Check for unnaturally consistent sentence lengths"""
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 5:
            return 0
        
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # Calculate variance
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Low variance indicates AI (unnaturally consistent)
        consistency_score = 100 - min(100, std_dev * 10)  # Invert score
        return max(0, consistency_score - 20)  # Adjust threshold
    
    def _check_readability_patterns(self, text):
        """Check readability patterns that suggest AI generation"""
        try:
            # Simple readability metrics
            words = text.split()
            sentences = len([s for s in text.split('.') if s.strip()])
            
            if sentences == 0:
                return 0
            
            avg_words_per_sentence = len(words) / sentences
            
            # AI tends to have very consistent, moderate sentence lengths
            if 15 <= avg_words_per_sentence <= 25:
                return 30  # Moderate AI indicator
            elif 25 < avg_words_per_sentence <= 35:
                return 50  # Higher AI indicator
            else:
                return 10  # More natural variation
                
        except:
            return 0

# Initialize AI detector
ai_detector = AIDetector()

# Initialize humanizer
humanizer = AdvancedHumanizer()

def detect_ai_text(input_text):
    """Detect if text is AI-generated"""
    if not input_text.strip():
        return "Please enter some text to analyze."
    
    result = ai_detector.calculate_ai_probability(input_text)
    
    # Format the output
    output = f"""
## 🤖 AI Detection Analysis

**Overall Assessment:** {result['verdict']}
**AI Probability:** {result['probability']}%
**Confidence Level:** {result['confidence']}

### 📊 Detailed Breakdown:

- **AI Phrases Score:** {result['details']['ai_phrases_score']}%
- **Vocabulary Repetition:** {result['details']['vocabulary_repetition']}%
- **Structure Patterns:** {result['details']['structure_patterns']}%
- **Transition Overuse:** {result['details']['transition_overuse']}%
- **Formal Patterns:** {result['details']['formal_patterns']}%
- **Sentence Consistency:** {result['details']['sentence_consistency']}%
- **Readability Score:** {result['details']['readability_score']}%

### 💡 Interpretation:
- **0-20%:** Likely human-written with natural variations
- **21-40%:** Possibly AI-generated or heavily edited
- **41-60%:** Probably AI-generated with some humanization
- **61-80%:** Likely AI-generated with minimal editing
- **81-100%:** Very likely raw AI-generated content

### 🛡️ Tips to Improve:
- Add more natural vocabulary variations
- Use varied sentence structures
- Include personal insights or examples
- Reduce formal academic buzzwords
- Add natural transitions and flow
"""
    
    return output

def humanize_academic_text(input_text, humanization_level="Moderate"):
    """
    Advanced humanization with multiple techniques
    """
    if not input_text.strip():
        return "Please enter some text to humanize."
    
    # Step 1: Initial paraphrasing with multiple models
    paraphrased = humanizer.paraphrase_with_multiple_models(input_text)
    
    # Apply different levels of humanization
    if humanization_level == "Light":
        # Minimal changes - just paraphrasing
        result = paraphrased
    elif humanization_level == "Moderate":
        # Add natural variations and some vocabulary changes
        result = humanizer.add_natural_variations(paraphrased)
        result = humanizer.diversify_vocabulary(result)
    else:  # Heavy
        # Apply all techniques
        result = humanizer.add_natural_variations(paraphrased)
        result = humanizer.diversify_vocabulary(result)
        result = humanizer.adjust_sentence_structure(result)
    
    # Clean up formatting
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'\s+([.,!?;:])', r'\1', result)
    
    # Ensure proper capitalization
    if NLTK_AVAILABLE:
        sentences = sent_tokenize(result)
    else:
        sentences = [s.strip() for s in result.split('.') if s.strip()]
    
    formatted_sentences = []
    for sentence in sentences:
        if sentence:
            sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            formatted_sentences.append(sentence)
    
    final_result = " ".join(formatted_sentences)
    
    return final_result if final_result else "Error processing text. Please try again."

# Create Gradio interface with tabs for both humanization and AI detection
with gr.Blocks(theme="soft", title="AI Text Humanizer & Detector") as demo:
    gr.Markdown("""
    # 🤖➡️👨 AI Text Humanizer & Detector Pro
    
    **Complete solution for AI text processing - Humanize AND Detect AI-generated content**
    
    Transform robotic AI text into natural, human-like writing, then verify the results with our built-in AI detector.
    """)
    
    with gr.Tabs():
        # Humanization Tab
        with gr.TabItem("🎭 Text Humanizer"):
            gr.Markdown("### Transform AI text into natural, human-like writing")
            
            with gr.Row():
                with gr.Column():
                    humanize_input = gr.Textbox(
                        lines=10,
                        placeholder="Enter machine-generated or robotic academic text here...",
                        label="Raw Input Text",
                        info="Paste your AI-generated text that needs to be humanized"
                    )
                    
                    humanization_level = gr.Radio(
                        choices=["Light", "Moderate", "Heavy"],
                        value="Moderate",
                        label="Humanization Level",
                        info="Light: Basic paraphrasing | Moderate: Natural variations + vocabulary | Heavy: All techniques"
                    )
                    
                    humanize_btn = gr.Button("🚀 Humanize Text", variant="primary", size="lg")
                
                with gr.Column():
                    humanize_output = gr.Textbox(
                        label="Humanized Academic Output",
                        lines=10,
                        info="Copy this natural, human-like text"
                    )
            
            # Examples for humanizer
            gr.Examples(
                examples=[
                    [
                        "The implementation of artificial intelligence algorithms demonstrates significant improvements in computational efficiency and accuracy metrics across various benchmark datasets.",
                        "Moderate"
                    ],
                    [
                        "Machine learning models exhibit superior performance characteristics when evaluated against traditional statistical approaches in predictive analytics applications.",
                        "Heavy"
                    ]
                ],
                inputs=[humanize_input, humanization_level],
                outputs=humanize_output,
                fn=humanize_academic_text
            )
        
        # AI Detection Tab
        with gr.TabItem("🕵️ AI Detector"):
            gr.Markdown("### Analyze text to detect if it's AI-generated")
            
            with gr.Row():
                with gr.Column():
                    detect_input = gr.Textbox(
                        lines=10,
                        placeholder="Paste text here to check if it's AI-generated...",
                        label="Text to Analyze",
                        info="Enter any text to check its AI probability"
                    )
                    
                    detect_btn = gr.Button("🔍 Analyze Text", variant="secondary", size="lg")
                
                with gr.Column():
                    detect_output = gr.Markdown(
                        label="AI Detection Results",
                        value="Analysis results will appear here..."
                    )
            
            # Examples for detector
            gr.Examples(
                examples=[
                    ["The implementation of machine learning algorithms demonstrates significant improvements in computational efficiency and accuracy metrics across various benchmark datasets. Furthermore, these results indicate substantial enhancements in performance."],
                    ["I love going to the coffee shop on weekends. The barista there makes the best cappuccino I've ever had, and I always end up chatting with other customers about random stuff."],
                    ["The comprehensive analysis reveals that the optimization of neural network architectures facilitates enhanced performance characteristics in predictive analytics applications."]
                ],
                inputs=[detect_input],
                outputs=detect_output,
                fn=detect_ai_text
            )
        
        # Combined Analysis Tab
        with gr.TabItem("🔄 Humanize & Test"):
            gr.Markdown("### Humanize text and immediately test the results")
            
            with gr.Column():
                combined_input = gr.Textbox(
                    lines=8,
                    placeholder="Enter AI-generated text to humanize and test...",
                    label="Original AI Text",
                    info="This will be humanized and then tested for AI detection"
                )
                
                combined_level = gr.Radio(
                    choices=["Light", "Moderate", "Heavy"],
                    value="Moderate",
                    label="Humanization Level"
                )
                
                combined_btn = gr.Button("🔄 Humanize & Analyze", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column():
                    combined_humanized = gr.Textbox(
                        label="Humanized Text",
                        lines=8
                    )
                
                with gr.Column():
                    combined_analysis = gr.Markdown(
                        label="AI Detection Analysis",
                        value="Analysis will appear here..."
                    )
        
        # Settings & Info Tab
        with gr.TabItem("ℹ️ Info & Settings"):
            gr.Markdown("""
            ### 🎯 How to Use:
            
            **Humanizer:**
            1. Paste your AI-generated text
            2. Choose humanization level
            3. Get natural, human-like output
            
            **AI Detector:**
            1. Paste any text
            2. Get detailed AI probability analysis
            3. See breakdown of detection factors
            
            **Combined Mode:**
            1. Humanize and test in one step
            2. Perfect for optimizing results
            3. Iterate until satisfied
            
            ### 🔧 Features:
            
            **Humanization:**
            - ✅ Multiple AI models for paraphrasing
            - ✅ Natural vocabulary variations
            - ✅ Sentence structure optimization  
            - ✅ Academic tone preservation
            - ✅ Three intensity levels
            
            **AI Detection:**
            - 🔍 Advanced pattern recognition
            - 📊 Detailed scoring breakdown
            - 🎯 Multiple detection criteria
            - 📈 Confidence assessment
            - 💡 Improvement suggestions
            
            ### ⚖️ Ethical Usage:
            This tool is for improving writing quality and understanding AI detection.
            Use responsibly and maintain academic integrity.
            """)
    
    # Event handlers
    humanize_btn.click(
        fn=humanize_academic_text,
        inputs=[humanize_input, humanization_level],
        outputs=humanize_output
    )
    
    detect_btn.click(
        fn=detect_ai_text,
        inputs=[detect_input],
        outputs=detect_output
    )
    
    def combined_process(text, level):
        """Humanize text and then analyze it"""
        if not text.strip():
            return "Please enter text to process.", "No analysis available."
        
        # First humanize
        humanized = humanize_academic_text(text, level)
        
        # Then analyze
        analysis = detect_ai_text(humanized)
        
        return humanized, analysis
    
    combined_btn.click(
        fn=combined_process,
        inputs=[combined_input, combined_level],
        outputs=[combined_humanized, combined_analysis]
    )

if __name__ == "__main__":
    demo.launch(
        share=False,
        debug=True,
        show_error=True,
        server_name="127.0.0.1",
        server_port=7860
    )
