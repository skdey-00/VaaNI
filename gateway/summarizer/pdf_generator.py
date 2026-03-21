"""
PDF Generator for VaaNI Session Summaries

Generates professional bilingual PDF summaries using WeasyPrint.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
import logging

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)


class PDFGenerator:
    """Generate bilingual PDF summaries for banking sessions."""

    # Language display names and titles
    LANGUAGE_TITLES = {
        'en': {'name': 'English', 'interaction_summary': 'Interaction Summary'},
        'hi': {'name': 'हिंदी', 'interaction_summary': 'अंतःक्रिया सारांश'},
        'mr': {'name': 'मराठी', 'interaction_summary': 'अंतःक्रिया सारांश'},
        'ta': {'name': 'தமிழ்', 'interaction_summary': 'தொடர்பு சுருக்கம்'},
        'te': {'name': 'తెలుగు', 'interaction_summary': 'సమావేశం సారాంశం'},
        'bn': {'name': 'বাংলা', 'interaction_summary': 'মিথস্ক্রিয়া সারাংশ'},
        'kn': {'name': 'ಕನ್ನಡ', 'interaction_summary': 'ಸಂವಹನ ಸಾರಾಂಶ'},
        'ml': {'name': 'മലയാളം', 'interaction_summary': 'ഇടപെടൽ സംഗ്രഹം'},
        'gu': {'name': 'ગુજરાતી', 'interaction_summary': 'વાર્તાલાપ સારંશ'},
        'es': {'name': 'Español', 'interaction_summary': 'Resumen de Interacción'},
        'fr': {'name': 'Français', 'interaction_summary': 'Résumé de l\'Interaction'},
        'de': {'name': 'Deutsch', 'interaction_summary': 'Zusammenfassung'},
        'zh': {'name': '中文', 'interaction_summary': '互动摘要'},
        'ar': {'name': 'العربية', 'interaction_summary': 'ملخص التفاعل'},
        'pt': {'name': 'Português', 'interaction_summary': 'Resumo da Interação'},
    }

    def __init__(self):
        """Initialize PDF generator."""
        self.template = JINJA_ENV.get_template('template.html')

    def generate_pdf(
        self,
        session_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from session data.

        Args:
            session_data: Dictionary containing session information
            output_path: Optional path to save PDF file

        Returns:
            PDF as bytes
        """
        try:
            # Render HTML template
            html_content = self._render_template(session_data)

            # Generate PDF
            logger.info("Generating PDF...")
            pdf_bytes = HTML(string=html_content).write_pdf()

            # Save to file if path provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                logger.info(f"PDF saved to {output_path}")

            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF generation failed: {e}", exc_info=True)
            raise

    def _render_template(self, session_data: Dict[str, Any]) -> str:
        """Render Jinja2 template with session data."""

        # Extract and format data
        session_id = session_data.get('session_id', 'Unknown')
        customer_language = session_data.get('customer_language', 'en')
        start_time = session_data.get('start_time')
        end_time = session_data.get('end_time')
        branch_code = session_data.get('branch_code', 'BR-001')
        staff_id = session_data.get('staff_id', 'STAFF-001')

        # Calculate duration
        duration_str = self._calculate_duration(start_time, end_time)

        # Format datetime
        date_str = self._format_datetime(start_time)
        time_range = self._format_time_range(start_time, end_time)

        # Get language titles
        lang_info = self.LANGUAGE_TITLES.get(
            customer_language,
            self.LANGUAGE_TITLES['en']
        )

        # Process transcript for table
        transcript_rows = self._process_transcript(
            session_data.get('transcript', [])
        )

        # Get summary texts
        summary_en = session_data.get('summary_en', '')
        summary_lang = session_data.get('summary_lang', '')

        # Get query type and resolution
        query_type = session_data.get('query_type', 'General Inquiry')
        resolved = session_data.get('resolved', True)
        escalated = session_data.get('escalated', False)

        # Get completed process steps
        process_steps = session_data.get('process_steps', [])
        completed_steps = [s for s in process_steps if s.get('completed', False)]

        # Render template
        return self.template.render(
            # Titles
            title_en='Interaction Summary',
            title_lang=lang_info['interaction_summary'],
            language_name=lang_info['name'],
            is_rtl=customer_language == 'ar',

            # Session metadata
            session_id=session_id,
            date=date_str,
            time_range=time_range,
            branch_code=branch_code,
            staff_id=staff_id,
            customer_language=customer_language,
            duration=duration_str,

            # Conversation log
            transcript_rows=transcript_rows,

            # Summaries
            summary_en=summary_en,
            summary_lang=summary_lang,

            # Query info
            query_type=query_type,
            resolved=resolved,
            escalated=escalated,

            # Process steps
            process_steps=process_steps,
            completed_steps=completed_steps,
            has_process_steps=len(process_steps) > 0,

            # Timestamp
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )

    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate and format session duration."""
        try:
            if isinstance(start_time, str):
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start = start_time

            if isinstance(end_time, str):
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            else:
                end = end_time or datetime.now()

            duration = end - start
            total_seconds = int(duration.total_seconds())

            minutes = total_seconds // 60
            seconds = total_seconds % 60

            if minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"

        except Exception:
            return "N/A"

    def _format_datetime(self, dt: Any) -> str:
        """Format datetime to readable string."""
        try:
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y')
        except Exception:
            return datetime.now().strftime('%B %d, %Y')

    def _format_time_range(self, start: Any, end: Any) -> str:
        """Format time range."""
        try:
            if isinstance(start, str):
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            else:
                start_dt = start

            if isinstance(end, str):
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            else:
                end_dt = end or datetime.now()

            start_str = start_dt.strftime('%I:%M %p')
            end_str = end_dt.strftime('%I:%M %p')

            return f"{start_str} - {end_str}"
        except Exception:
            return "N/A"

    def _process_transcript(self, transcript: List[Dict]) -> List[Dict]:
        """Process transcript for table display."""
        rows = []

        for entry in transcript:
            role = entry.get('role', 'customer')
            text = entry.get('text', entry.get('original_text', ''))
            translation = entry.get('translated_text', '')
            timestamp = entry.get('timestamp', '')

            # Format timestamp
            try:
                if isinstance(timestamp, str):
                    ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    ts = timestamp
                time_str = ts.strftime('%I:%M %p')
            except Exception:
                time_str = 'N/A'

            rows.append({
                'time': time_str,
                'speaker': 'Customer' if role == 'customer' else 'Staff',
                'original': text,
                'translation': translation,
            })

        return rows


# Singleton instance
pdf_generator = PDFGenerator()
