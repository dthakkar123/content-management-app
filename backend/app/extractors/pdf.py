import pdfplumber
from typing import Dict, Any
import os
from app.extractors.base import BaseExtractor
import logging

logger = logging.getLogger(__name__)


class PDFExtractor(BaseExtractor):
    """
    Extractor for PDF files.

    Uses pdfplumber for robust text extraction including tables.
    """

    async def can_handle(self, source: str, is_file: bool = False) -> bool:
        """
        Can handle PDF files.

        Args:
            source: File path
            is_file: True for PDF files

        Returns:
            bool: True if source is a PDF file
        """
        if not is_file:
            return False

        return source.lower().endswith('.pdf')

    async def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from a PDF file.

        Args:
            source: Path to PDF file
            **kwargs: Additional arguments (unused)

        Returns:
            dict: Extracted content

        Raises:
            Exception: If extraction fails
        """
        try:
            if not os.path.exists(source):
                raise FileNotFoundError(f"PDF file not found: {source}")

            # Extract text from PDF
            extracted_text = []
            metadata = {}

            with pdfplumber.open(source) as pdf:
                # Get PDF metadata
                pdf_info = pdf.metadata or {}
                metadata.update({
                    'page_count': len(pdf.pages),
                    'pdf_info': pdf_info,
                })

                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text()
                        if text:
                            extracted_text.append(text)

                        # Also try to extract tables
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                # Convert table to text
                                table_text = '\n'.join(['\t'.join([str(cell) for cell in row if cell]) for row in table])
                                extracted_text.append(f"\n[Table]\n{table_text}\n")

                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {str(e)}")
                        continue

            if not extracted_text:
                raise ValueError("No text could be extracted from PDF")

            full_text = '\n\n'.join(extracted_text)

            # Try to extract title from PDF metadata or first line
            title = pdf_info.get('Title') or pdf_info.get('title')
            if not title and full_text:
                # Use first non-empty line as title
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                title = lines[0] if lines else "Untitled PDF"

            # Extract author from metadata
            author = pdf_info.get('Author') or pdf_info.get('author')

            # Extract creation date
            publish_date = None
            creation_date = pdf_info.get('CreationDate') or pdf_info.get('creation_date')
            if creation_date:
                try:
                    from dateutil import parser
                    publish_date = parser.parse(str(creation_date))
                except Exception:
                    pass

            return self._create_result(
                title=title or "Untitled PDF",
                content=full_text,
                author=author,
                publish_date=publish_date,
                metadata={
                    'file_path': source,
                    'extractor': 'pdf',
                    **metadata,
                }
            )

        except Exception as e:
            logger.error(f"Error extracting PDF {source}: {str(e)}")
            raise Exception(f"Failed to extract PDF: {str(e)}")

    def get_source_type(self) -> str:
        """Return source type identifier."""
        return 'pdf'
