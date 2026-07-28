# 🤖➡️👨 AI Text Humanizer & Detector Pro

A comprehensive web application for transforming AI-generated text into natural, human-like writing while providing advanced AI detection capabilities.

## Build

Built by M Umar Alam

- Email: umaralam9002@gmail.com
- Portfolio: umardev.me

## ✨ Features

### 🎭 Text Humanizer

- **Advanced Vocabulary Enhancement**: Replace robotic terms with natural alternatives
- **Sentence Flow Optimization**: Improve readability and natural rhythm
- **Structure Diversification**: Break up repetitive patterns
- **Academic Tone Preservation**: Maintain professional quality while adding humanity
- **Multi-level Processing**: Light, Medium, and Heavy humanization options

### 🕵️ AI Detector

- **7-Point Analysis System**: Comprehensive AI probability assessment
- **Detailed Scoring**: Individual metrics for each detection factor
- **Confidence Levels**: Clear interpretation of results
- **Pattern Recognition**: Identifies common AI writing patterns
- **Real-time Analysis**: Instant feedback on text authenticity

### 🔄 Combined Processing

- **One-Click Workflow**: Humanize and test in a single process
- **Optimization Loop**: Perfect for iterative improvements
- **Quality Validation**: Ensure humanization effectiveness

## 🚀 Live Demo

Visit the live application: [Hugging Face Spaces](https://huggingface.co/spaces/YOUR_USERNAME/ai-text-humanizer)

## 📦 Installation

### Local Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd umardev-main
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open your browser to the local URL printed in the terminal. If port `7860` is already in use, the app automatically chooses another free port.

### Windows shortcut

```powershell
run.bat
```

## 🔌 API Endpoints

When you run `python app.py`, the server exposes:

- `GET /api/health` - health check
- `POST /api/humanize` - humanize text
- `POST /api/detect` - analyze text for AI probability
- `POST /api/combined` - humanize first, then analyze

### Request and Response Details

#### `GET /api/health`

- Request: no body
- Response: JSON status object

Example response:

```json
{ "status": "ok", "service": "AI Text Humanizer API" }
```

#### `POST /api/humanize`

- Request body:
  - `text` - the text to humanize
  - `level` - `Light`, `Medium`, or `Heavy`
- Response:
  - `input_text` - original text
  - `humanized_text` - processed output
  - `level` - selected humanization level

Example request:

```json
{
  "text": "The implementation of machine learning algorithms demonstrates significant improvements.",
  "level": "Medium"
}
```

Example response:

```json
{ "input_text": "...", "humanized_text": "...", "level": "Medium" }
```

#### `POST /api/detect`

- Request body:
  - `text` - text you want to analyze
- Response:
  - `probability` - AI probability score
  - `confidence` - confidence label
  - `verdict` - human-readable assessment
  - `details` - score breakdown for each detection factor
  - `analysis_markdown` - formatted analysis text

#### `POST /api/combined`

- Request body:
  - `text` - text you want to humanize and analyze
  - `level` - `Light`, `Medium`, or `Heavy`
- Response:
  - `humanized_text` - processed text
  - `analysis` - AI detection summary for the processed text
  - `analysis_markdown` - formatted analysis text

The interactive UI is available at:

- `http://127.0.0.1:<port>/ui`

The OpenAPI docs are available at:

- `http://127.0.0.1:<port>/docs`

### Example requests

```bash
curl -X POST "http://127.0.0.1:7860/api/humanize" ^
	-H "Content-Type: application/json" ^
	-d "{\"text\":\"The implementation of machine learning algorithms demonstrates significant improvements.\",\"level\":\"Medium\"}"
```

```bash
curl -X POST "http://127.0.0.1:7860/api/detect" ^
	-H "Content-Type: application/json" ^
	-d "{\"text\":\"The implementation of machine learning algorithms demonstrates significant improvements.\"}"
```

### UI note about the API

The UI includes a short instructions tab that explains the API endpoints, what each endpoint expects, and what it returns. This is informational only and does not change how the app works.

### Requirements

- Python 3.8+
- Gradio 4.44.0
- NLTK 3.8.1
- textstat 0.7.3
- numpy 1.24.3
- pandas 2.0.3

## 🛠️ Technical Details

### Humanization Algorithms

- **Vocabulary Diversification**: WordNet-based synonym replacement
- **Structural Variation**: Sentence pattern modification
- **Natural Flow Enhancement**: Academic connector and hedge phrase insertion
- **Linguistic Pattern Breaking**: AI-specific phrase elimination

### AI Detection Metrics

1. **AI Phrase Detection**: Identifies common AI-generated expressions
2. **Vocabulary Repetition**: Analyzes overuse of academic terms
3. **Structure Patterns**: Detects repetitive sentence starters
4. **Transition Overuse**: Measures excessive formal connectors
5. **Formal Pattern Recognition**: Identifies robotic phrasing
6. **Sentence Consistency**: Analyzes unnatural uniformity
7. **Readability Assessment**: Evaluates writing naturalness

## 📈 Usage Examples

### Input (AI-Generated):

```
The implementation of artificial intelligence algorithms demonstrates significant improvements in computational efficiency and accuracy metrics across various benchmark datasets.
```

### Output (Humanized):

```
AI algorithms show notable improvements in both computational efficiency and accuracy when tested across different benchmark datasets. These results indicate considerable advances in performance.
```

## 🔧 Configuration

### Humanization Levels:

- **Light**: Basic vocabulary substitution
- **Medium**: Vocabulary + natural flow enhancement
- **Heavy**: All techniques including structure modification

### AI Detection Thresholds:

- **0-20%**: Likely human-written
- **21-40%**: Possibly AI-generated
- **41-60%**: Probably AI-generated
- **61-80%**: Likely AI-generated
- **81-100%**: Very likely AI-generated

## 🌐 Deployment Options

### Hugging Face Spaces (Recommended)

1. Fork this repository
2. Create a new Space on Hugging Face
3. Link your GitHub repository
4. Automatic deployment with free GPU access

### Railway

1. Connect your GitHub repository
2. Deploy with one click
3. Free tier available

### Heroku

1. Create new Heroku app
2. Connect GitHub repository
3. Deploy from dashboard

## ⚖️ Ethical Usage

This tool is designed for:

- ✅ Improving writing quality and naturalness
- ✅ Educational purposes and learning
- ✅ Understanding AI detection mechanisms
- ✅ Research and development

**Important Guidelines:**

- 🚫 Do not use for plagiarism or academic dishonesty
- 🚫 Do not violate institutional policies
- 🚫 Do not misrepresent authorship
- ✅ Maintain transparency about AI assistance
- ✅ Follow academic integrity guidelines

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes
- Feature enhancements
- Algorithm improvements
- Documentation updates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NLTK team for natural language processing tools
- Hugging Face for hosting and deployment platform
- Gradio team for the web interface framework
- Open source community for various libraries and tools

## 📞 Support

For questions, issues, or suggestions:

- Open an issue on GitHub
- Contact: umaralam9002@gmail.com

---

**Disclaimer**: This tool is for educational and research purposes. Users are responsible for ensuring compliance with their institution's policies and maintaining academic integrity.
