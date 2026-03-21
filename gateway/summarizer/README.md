# PDF Summarizer Module

Generates professional bilingual PDF summaries for VaaNI banking sessions.

## Features

- **Bilingual Titles** - "Interaction Summary" in English and customer's language (15+ languages)
- **Session Metadata** - Date, time, branch code, staff ID, language, duration
- **Conversation Log** - Table with time, speaker, original text, and English translation
- **Bilingual Summaries** - Side-by-side columns for English and local language
- **Query Classification** - Query type, resolution status, escalation flag
- **Process Steps** - Checklist of completed banking process steps
- **Professional Layout** - A4 format with clean formal styling
- **No External Dependencies** - Uses system fonts, no CDN required

## Dependencies

- `weasyprint==60.1` - PDF generation from HTML/CSS
- `jinja2==3.1.3` - HTML templating

## Usage

### Basic Generation

```python
from summarizer.pdf_generator import pdf_generator

session_data = {
    "session_id": "abc-123",
    "customer_language": "hi",
    "start_time": "2025-01-15T10:30:00Z",
    "end_time": "2025-01-15T10:35:00Z",
    "branch_code": "BR-001",
    "staff_id": "STAFF-001",
    "transcript": [
        {
            "role": "customer",
            "text": "मैं रिफंड चाहता हूं",
            "translated_text": "I want a refund",
            "timestamp": "2025-01-15T10:30:15Z"
        },
        # ...
    ],
    "summary_en": "Customer inquired about refund process...",
    "summary_lang": "ग्राहक ने रिफंड प्रक्रिया के बारे में पूछा...",
    "query_type": "Refund Inquiry",
    "resolved": True,
    "escalated": False,
    "process_steps": [
        {"text": "Verify customer identity", "completed": True},
        {"text": "Check refund eligibility", "completed": True},
    ]
}

# Generate PDF
pdf_bytes = pdf_generator.generate_pdf(session_data)

# Or save to file
pdf_bytes = pdf_generator.generate_pdf(session_data, output_path="session_summary.pdf")
```

### API Endpoint

```bash
# Get PDF for a session
curl http://localhost:8000/session/{session_id}/export/pdf \
  --output session_summary.pdf

# Get JSON export
curl -X POST http://localhost:8000/session/{session_id}/export/json \
  --output session_data.json
```

## Supported Languages

| Code | Language | Title (Native Script) |
|------|----------|----------------------|
| en | English | Interaction Summary |
| hi | Hindi | अंतःक्रिया सारांश |
| mr | Marathi | अंतःक्रिया सारांश |
| ta | Tamil | தொடர்பு சுருக்கம் |
| te | Telugu | సమావేశం సారాంశం |
| bn | Bengali | মিথস্ক্রিয়া সারাংশ |
| kn | Kannada | ಸಂವಹನ ಸಾರಾಂಶ |
| ml | Malayalam | ഇടപെടൽ സംഗ്രഹം |
| gu | Gujarati | વાર્તાલાપ સારંશ |
| es | Spanish | Resumen de Interacción |
| fr | French | Résumé de l'Interaction |
| de | German | Zusammenfassung |
| zh | Chinese | 互动摘要 |
| ar | Arabic | ملخص التفاعل |
| pt | Portuguese | Resumo da Interação |

## Template Customization

Edit `template.html` to customize:
- Colors and styling
- Layout sections
- Header/footer content
- Table formats

## PDF Sections

1. **Header** - Bank logo, bilingual title
2. **Metadata Table** - Session ID, date, time, duration, branch, staff
3. **Conversation Log** - Full transcript with translations
4. **Bilingual Summary** - Side-by-side summaries
5. **Query & Resolution** - Type, resolved/escalated status
6. **Process Steps** - Completed steps checklist
7. **Footer** - Confidentiality notice, timestamp

## WeasyPrint System Requirements

On Ubuntu/Debian:
```bash
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

On macOS:
```bash
brew install cairo pango gdk-pixbuf libffi
```

On Windows, WeasyPrint includes the required DLLs.

## Troubleshooting

### Font Issues
If local language fonts don't render, install font packs:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-indic

# Or use Noto Fonts
sudo apt-get install fonts-noto
```

### Memory Issues
For long transcripts, increase memory:
```python
# In pdf_generator.py
HTML(string=html_content).write_pdf(
    presentational_hints=True,
    optimize_images=True
)
```
