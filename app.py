import gradio as gr
import random
import re
import warnings
import math
import os
import socket
from collections import Counter
from fastapi import FastAPI
from pydantic import BaseModel, Field
warnings.filterwarnings("ignore")

# Import NLTK with error handling
try:
    import nltk
    import textstat
    from nltk.corpus import wordnet
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        nltk.download('omw-1.4')
        
except ImportError as e:
    print(f"NLTK import error: {e}")
    NLTK_AVAILABLE = False
    import textstat

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
        
        # Enhanced vocabulary replacements for better humanization
        self.vocabulary_replacements = {
            "significant": ["notable", "considerable", "substantial", "important", "remarkable"],
            "demonstrate": ["show", "illustrate", "reveal", "display", "indicate"],
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

    def split_into_sentences(self, text):
        """Smart sentence splitting with NLTK fallback"""
        if NLTK_AVAILABLE:
            return sent_tokenize(text)
        else:
            # Enhanced fallback sentence splitting
            sentences = []
            current = ""
            
            for char in text:
                current += char
                if char == '.' and len(current) > 10:
                    # Check if this looks like end of sentence
                    remaining = text[text.find(current) + len(current):]
                    if remaining and (remaining[0].isupper() or remaining.strip().startswith(('The ', 'This ', 'A '))):
                        sentences.append(current.strip())
                        current = ""
            
            if current.strip():
                sentences.append(current.strip())
            
            return [s for s in sentences if len(s.strip()) > 5]

    def add_natural_variations(self, text):
        """Add natural linguistic variations to make text less robotic"""
        sentences = self.split_into_sentences(text)
        varied_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence.endswith('.'):
                sentence += '.'
                
            # Randomly add hedging language
            if random.random() < 0.3 and not any(phrase in sentence.lower() for phrase in self.hedging_phrases):
                hedge = random.choice(self.hedging_phrases)
                if sentence.startswith("The ") or sentence.startswith("This "):
                    words = sentence.split()
                    if len(words) > 2:
                        words.insert(2, hedge)
                        sentence = " ".join(words)
            
            # Add transitional phrases for flow
            if i > 0 and random.random() < 0.4:
                connector = random.choice(self.academic_connectors)
                sentence = f"{connector}, {sentence.lower()}"
            
            varied_sentences.append(sentence)
        
        return " ".join(varied_sentences)

    def diversify_vocabulary(self, text):
        """Replace common words with synonyms for variation"""
        if NLTK_AVAILABLE:
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
                        replacement = random.choice(synonyms[:3])
                        result.append(replacement)
                    else:
                        result.append(word)
                else:
                    result.append(word)
            
            return " ".join(result)
        else:
            # Enhanced fallback with more replacements
            result = text
            for original, alternatives in self.vocabulary_replacements.items():
                if original.lower() in result.lower():
                    replacement = random.choice(alternatives)
                    pattern = re.compile(re.escape(original), re.IGNORECASE)
                    result = pattern.sub(replacement, result, count=1)
            
            return result

    def adjust_sentence_structure(self, text):
        """Modify sentence structures for more natural flow"""
        sentences = self.split_into_sentences(text)
        modified = []
        
        for sentence in sentences:
            words = sentence.split()
            
            # For long sentences, sometimes break them up
            if len(words) > 20 and random.random() < 0.4:
                # Find a good break point
                break_words = ['and', 'but', 'which', 'that', 'because', 'since', 'while']
                for i, word in enumerate(words[8:18], 8):  # Look in middle section
                    if word.lower() in break_words:
                        part1 = " ".join(words[:i]) + "."
                        part2 = " ".join(words[i+1:])
                        if len(part2) > 5:  # Only if second part is substantial
                            part2 = part2[0].upper() + part2[1:] if part2 else part2
                            modified.extend([part1, part2])
                            break
                else:
                    modified.append(sentence)
            else:
                modified.append(sentence)
        
        return " ".join(modified)

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
                result = self.diversify_vocabulary(result)
                
            elif intensity.lower() in ["medium", "moderate"]:
                # Vocabulary + natural flow
                result = self.diversify_vocabulary(result)
                result = self.add_natural_variations(result)
                
            elif intensity.lower() in ["heavy", "high", "maximum"]:
                # All techniques
                result = self.diversify_vocabulary(result)
                result = self.add_natural_variations(result)
                result = self.adjust_sentence_structure(result)
            
            # Always clean up formatting
            result = self.clean_and_format(result)
            
            return result if result and len(result) > 10 else text
            
        except Exception as e:
            print(f"Humanization error: {e}")
            return "Error processing text. Please try again with different input."

class AIDetector:
    def __init__(self):
        """Initialize AI detection patterns and thresholds"""
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
        
        self.overused_academic_words = [
            "significant", "substantial", "comprehensive", "extensive", "robust",
            "novel", "innovative", "efficient", "effective", "optimal", "superior",
            "enhanced", "improved", "advanced", "sophisticated", "cutting-edge",
            "state-of-the-art", "groundbreaking", "revolutionary", "paradigm"
        ]
        
        self.excessive_transitions = [
            "furthermore", "moreover", "additionally", "consequently", "therefore",
            "thus", "hence", "nevertheless", "nonetheless", "however"
        ]
        
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
        
        # Various AI detection checks
        scores['ai_phrases'] = self._check_ai_phrases(text)
        scores['vocab_repetition'] = self._check_vocabulary_repetition(text)
        scores['structure_patterns'] = self._check_structure_patterns(text)
        scores['transition_overuse'] = self._check_transition_overuse(text)
        scores['formal_patterns'] = self._check_formal_patterns(text)
        scores['sentence_consistency'] = self._check_sentence_consistency(text)
        scores['readability'] = self._check_readability_patterns(text)
        
        # Calculate weighted final score
        weights = {
            'ai_phrases': 0.2, 'vocab_repetition': 0.15, 'structure_patterns': 0.15,
            'transition_overuse': 0.15, 'formal_patterns': 0.15,
            'sentence_consistency': 0.1, 'readability': 0.1
        }
        
        final_score = sum(scores[key] * weights[key] for key in weights)
        final_score = min(100, max(0, final_score))
        
        # Determine confidence level
        if final_score >= 80:
            confidence, verdict = "Very High", "Likely AI-Generated"
        elif final_score >= 60:
            confidence, verdict = "High", "Probably AI-Generated"
        elif final_score >= 40:
            confidence, verdict = "Medium", "Possibly AI-Generated"
        elif final_score >= 20:
            confidence, verdict = "Low", "Probably Human-Written"
        else:
            confidence, verdict = "Very Low", "Likely Human-Written"
        
        return {
            "probability": round(final_score, 1),
            "confidence": confidence,
            "verdict": verdict,
            "details": {k: round(v, 1) for k, v in scores.items()}
        }
    
    def _check_ai_phrases(self, text):
        text_lower = text.lower()
        phrase_count = sum(1 for phrase in self.ai_phrases if phrase in text_lower)
        words = len(text.split())
        return min(100, (phrase_count / words) * 1000 * 10) if words > 0 else 0
    
    def _check_vocabulary_repetition(self, text):
        words = [word.lower().strip('.,!?;:') for word in text.split() if word.isalpha()]
        if len(words) < 10:
            return 0
        word_counts = Counter(words)
        overused_count = sum(1 for word in self.overused_academic_words if word_counts.get(word, 0) > 1)
        return min(100, (overused_count / len(self.overused_academic_words)) * 200)
    
    def _check_structure_patterns(self, text):
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 3:
            return 0
        
        starters = [s.split()[:3] for s in sentences if len(s.split()) >= 3]
        starter_counts = Counter([' '.join(starter) for starter in starters])
        repeated_starters = sum(1 for count in starter_counts.values() if count > 1)
        return min(100, (repeated_starters / len(sentences)) * 150) if sentences else 0
    
    def _check_transition_overuse(self, text):
        text_lower = text.lower()
        transition_count = sum(1 for transition in self.excessive_transitions if transition in text_lower)
        words = len(text.split())
        return min(100, (transition_count / words) * 100 * 20) if words > 0 else 0
    
    def _check_formal_patterns(self, text):
        pattern_count = sum(len(re.findall(pattern, text.lower())) for pattern in self.formal_patterns)
        words = len(text.split())
        return min(100, (pattern_count / words) * 1000 * 15) if words > 0 else 0
    
    def _check_sentence_consistency(self, text):
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 5:
            return 0
        
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        consistency_score = 100 - min(100, std_dev * 10)
        return max(0, consistency_score - 20)
    
    def _check_readability_patterns(self, text):
        try:
            words = text.split()
            sentences = len([s for s in text.split('.') if s.strip()])
            if sentences == 0:
                return 0
            avg_words_per_sentence = len(words) / sentences
            if 15 <= avg_words_per_sentence <= 25:
                return 30
            elif 25 < avg_words_per_sentence <= 35:
                return 50
            else:
                return 10
        except:
            return 0

# Initialize components
humanizer = AdvancedHumanizer()
ai_detector = AIDetector()


class HumanizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to humanize")
    level: str = Field("Medium", description="Humanization level: Light, Medium, or Heavy")


class DetectRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")


class CombinedRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to humanize and analyze")
    level: str = Field("Medium", description="Humanization level: Light, Medium, or Heavy")

def process_text(input_text, humanization_level):
    """Process the input text"""
    return humanizer.humanize_text(input_text, humanization_level)

def detect_ai_text(input_text):
    """Detect if text is AI-generated"""
    if not input_text.strip():
        return "Please enter some text to analyze."
    
    result = ai_detector.calculate_ai_probability(input_text)
    
    return f"""
## 🤖 AI Detection Analysis

**Overall Assessment:** {result['verdict']}
**AI Probability:** {result['probability']}%
**Confidence Level:** {result['confidence']}

### 📊 Detailed Breakdown:
- **AI Phrases Score:** {result['details']['ai_phrases']}%
- **Vocabulary Repetition:** {result['details']['vocab_repetition']}%
- **Structure Patterns:** {result['details']['structure_patterns']}%
- **Transition Overuse:** {result['details']['transition_overuse']}%
- **Formal Patterns:** {result['details']['formal_patterns']}%
- **Sentence Consistency:** {result['details']['sentence_consistency']}%
- **Readability Score:** {result['details']['readability']}%

### 💡 Interpretation:
- **0-20%:** Likely human-written with natural variations
- **21-40%:** Possibly AI-generated or heavily edited
- **41-60%:** Probably AI-generated with some humanization
- **61-80%:** Likely AI-generated with minimal editing
- **81-100%:** Very likely raw AI-generated content
"""

def combined_process(text, level):
    """Humanize text and then analyze it"""
    if not text.strip():
        return "Please enter text to process.", "No analysis available."
    
    humanized = process_text(text, level)
    analysis = detect_ai_text(humanized)
    return humanized, analysis


api_app = FastAPI(
    title="AI Text Humanizer API",
    version="1.0.0",
    description="API endpoints for humanizing text and detecting AI-generated content."
)


@api_app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AI Text Humanizer API"}


@api_app.post("/api/humanize")
def humanize_endpoint(payload: HumanizeRequest):
    humanized = process_text(payload.text, payload.level)
    return {
        "input_text": payload.text,
        "humanized_text": humanized,
        "level": payload.level,
    }


@api_app.post("/api/detect")
def detect_endpoint(payload: DetectRequest):
    result = ai_detector.calculate_ai_probability(payload.text)
    return {
        "input_text": payload.text,
        "probability": result["probability"],
        "confidence": result["confidence"],
        "verdict": result.get("verdict"),
        "details": result["details"],
        "analysis_markdown": detect_ai_text(payload.text),
    }


@api_app.post("/api/combined")
def combined_endpoint(payload: CombinedRequest):
    humanized = process_text(payload.text, payload.level)
    result = ai_detector.calculate_ai_probability(humanized)
    return {
        "input_text": payload.text,
        "humanized_text": humanized,
        "level": payload.level,
        "analysis": {
            "probability": result["probability"],
            "confidence": result["confidence"],
            "verdict": result.get("verdict"),
            "details": result["details"],
        },
        "analysis_markdown": detect_ai_text(humanized),
    }

# Create Gradio interface
with gr.Blocks(theme="soft", title="AI Text Humanizer & Detector") as demo:
    gr.Markdown("""
    # 🤖➡️👨 AI Text Humanizer & Detector Pro
    
    **Complete solution for AI text processing - Humanize AND Detect AI-generated content**
    
    Transform robotic AI text into natural, human-like writing, then verify the results with our built-in AI detector.
    
    ⚠️ **Note:** This tool is for educational purposes. Please use responsibly and maintain academic integrity.
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
                        choices=["Light", "Medium", "Heavy"],
                        value="Medium",
                        label="Humanization Level",
                        info="Light: Basic changes | Medium: Vocabulary + flow | Heavy: All techniques"
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
                        "Medium"
                    ],
                    [
                        "Machine learning models exhibit superior performance characteristics when evaluated against traditional statistical approaches in predictive analytics applications.",
                        "Heavy"
                    ]
                ],
                inputs=[humanize_input, humanization_level],
                outputs=humanize_output
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
                outputs=detect_output
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
                    choices=["Light", "Medium", "Heavy"],
                    value="Medium",
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
        
        # Info Tab
        with gr.TabItem("ℹ️ Instructions"):
            gr.Markdown("""
            ### 🎯 How to Use:

            ### 🔌 API Access:

            The same humanize, detect, and combined features are also available through REST API endpoints.
            Use the API if you want to call this app from another script, backend, Postman, or automation tool.

            - `GET /api/health` - checks whether the service is running
            - `POST /api/humanize` - sends `text` and `level`, returns the humanized text
            - `POST /api/detect` - sends `text`, returns AI probability and analysis details
            - `POST /api/combined` - sends `text` and `level`, returns humanized text plus analysis

            OpenAPI docs are available at `/docs` and the UI is mounted at `/ui`.
            
            **Text Humanizer:**
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
            
            **Humanization Techniques:**
            - ✅ Advanced vocabulary variations
            - ✅ Natural sentence flow enhancement  
            - ✅ Academic tone preservation
            - ✅ Structure diversification
            - ✅ Linguistic pattern breaking
            
            **AI Detection:**
            - 🔍 7-point analysis system
            - 📊 Detailed scoring breakdown
            - 🎯 Confidence assessment
            - 💡 Improvement suggestions
            
            ### ⚖️ Ethical Usage:
            This tool is designed for:
            - ✅ Improving writing quality
            - ✅ Learning natural language patterns
            - ✅ Educational purposes
            - ✅ Understanding AI detection
            
            **Please use responsibly:**
            - 🚫 Don't use for plagiarism
            - 🚫 Don't violate academic policies
            - 🚫 Don't misrepresent authorship
            - ✅ Maintain academic integrity
            """)
    
    # Event handlers
    humanize_btn.click(
        fn=process_text,
        inputs=[humanize_input, humanization_level],
        outputs=humanize_output
    )
    
    detect_btn.click(
        fn=detect_ai_text,
        inputs=[detect_input],
        outputs=detect_output
    )
    
    combined_btn.click(
        fn=combined_process,
        inputs=[combined_input, combined_level],
        outputs=[combined_humanized, combined_analysis]
    )

def get_available_port(start_port=7860, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    return 7860


if __name__ == "__main__":
    preferred_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    server_port = get_available_port(preferred_port)
    api_app = gr.mount_gradio_app(api_app, demo, path="/ui")
    print(f"Starting API on http://127.0.0.1:{server_port}")
    print(f"Gradio UI available at http://127.0.0.1:{server_port}/ui")
    print(f"API docs available at http://127.0.0.1:{server_port}/docs")
    # import uvicorn
    # uvicorn.run(api_app, host="0.0.0.0", port=server_port)
