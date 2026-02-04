"""
OCR Service for Proof of Payment Processing
Extracts payment information from bank receipts and EFT confirmations
"""
import re
from datetime import datetime
from decimal import Decimal
import io
try:
    from PIL import Image
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class OCRService:
    """
    Intelligent OCR service for extracting payment data from proof of payment documents
    """
    
    def __init__(self):
        self.confidence_threshold = 0.7
        
    def process_document(self, file_path, file_type):
        """
        Main entry point for processing a proof of payment document
        
        Args:
            file_path: Path to the uploaded file
            file_type: File extension (pdf, jpg, png, etc.)
            
        Returns:
            dict: Extracted payment information
        """
        try:
            # Extract text from document
            text = self._extract_text(file_path, file_type)
            
            if not text:
                return {
                    'success': False,
                    'error': 'Could not extract text from document',
                    'raw_text': ''
                }
            
            # Parse extracted text for payment information
            extracted_data = self._parse_payment_info(text)
            extracted_data['raw_text'] = text
            extracted_data['success'] = True
            
            return extracted_data
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_text': ''
            }
    
    def _extract_text(self, file_path, file_type):
        """Extract text from image or PDF"""
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return self._extract_from_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            # If PDF text extraction fails, try OCR on PDF images
            if TESSERACT_AVAILABLE:
                text = self._extract_from_pdf_with_ocr(file_path)
            else:
                raise e
        
        return text
    
    def _extract_from_pdf_with_ocr(self, file_path):
        """Extract text from PDF using OCR (for scanned PDFs)"""
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image)
            return text
        except ImportError:
            raise ImportError("pdf2image not installed. Install with: pip install pdf2image")
    
    def _extract_from_image(self, file_path):
        """Extract text from image file using OCR"""
        if not TESSERACT_AVAILABLE:
            raise ImportError("Tesseract OCR not installed. Install with: pip install pytesseract pillow")
        
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    
    def _parse_payment_info(self, text):
        """
        Parse extracted text to find payment information
        Uses regex patterns to extract amount, reference, date, and payer details
        """
        data = {
            'amount': None,
            'reference': None,
            'date': None,
            'payer_name': None,
            'payer_account': None,
            'bank_name': None,
            'confidence': 0.0
        }
        
        confidence_scores = []
        
        # Extract amount
        amount_result = self._extract_amount(text)
        if amount_result:
            data['amount'] = amount_result['value']
            confidence_scores.append(amount_result['confidence'])
        
        # Extract reference number
        reference_result = self._extract_reference(text)
        if reference_result:
            data['reference'] = reference_result['value']
            confidence_scores.append(reference_result['confidence'])
        
        # Extract date
        date_result = self._extract_date(text)
        if date_result:
            data['date'] = date_result['value']
            confidence_scores.append(date_result['confidence'])
        
        # Extract payer details
        payer_result = self._extract_payer_info(text)
        if payer_result:
            data.update(payer_result['values'])
            confidence_scores.append(payer_result['confidence'])
        
        # Extract bank name
        bank_result = self._extract_bank_name(text)
        if bank_result:
            data['bank_name'] = bank_result['value']
            confidence_scores.append(bank_result['confidence'])
        
        # Calculate overall confidence
        data['confidence'] = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return data
    
    def _extract_amount(self, text):
        """Extract payment amount from text"""
        # Common patterns for South African Rand amounts
        patterns = [
            r'(?:amount|total|paid|deposited?)[:\s]*R?\s*([0-9,]+\.?\d{0,2})',
            r'R\s*([0-9,]+\.?\d{2})',
            r'ZAR\s*([0-9,]+\.?\d{2})',
            r'([0-9,]+\.\d{2})\s*(?:ZAR|R)',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1).replace(',', '').replace(' ', '')
                try:
                    amount = Decimal(amount_str)
                    if 0 < amount < 1000000:  # Reasonable range
                        amounts.append(amount)
                except:
                    continue
        
        if amounts:
            # Return the most common amount or the largest if all different
            from collections import Counter
            amount_counts = Counter(amounts)
            most_common = amount_counts.most_common(1)[0][0]
            return {
                'value': float(most_common),
                'confidence': 0.9 if len(amounts) > 1 else 0.7
            }
        
        return None
    
    def _extract_reference(self, text):
        """Extract payment reference number"""
        patterns = [
            r'(?:reference|ref|ref\s*no|ref\s*number)[:\s]*([A-Z0-9\-]+)',
            r'(?:transaction|trans|txn)[:\s]*(?:id|number|no)[:\s]*([A-Z0-9\-]+)',
            r'INV[-\s]*([A-Z0-9]+)',
            r'ORD[-\s]*([A-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'value': match.group(1).strip(),
                    'confidence': 0.8
                }
        
        return None
    
    def _extract_date(self, text):
        """Extract payment date"""
        # South African date formats
        patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',  # DD Month YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = self._parse_date_string(date_str)
                if parsed_date:
                    return {
                        'value': parsed_date,
                        'confidence': 0.8
                    }
        
        return None
    
    def _parse_date_string(self, date_str):
        """Parse various date formats"""
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%d %B %Y', '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _extract_payer_info(self, text):
        """Extract payer name and account information"""
        data = {
            'payer_name': None,
            'payer_account': None
        }
        
        # Extract account number
        account_pattern = r'(?:account|acc)[:\s]*(?:no|number)?[:\s]*([0-9\s\-]{8,20})'
        account_match = re.search(account_pattern, text, re.IGNORECASE)
        if account_match:
            data['payer_account'] = account_match.group(1).replace(' ', '').replace('-', '')
        
        # Extract payer name (look for "from" or "payer" keywords)
        name_patterns = [
            r'(?:from|payer|sender)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'(?:name)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                data['payer_name'] = name_match.group(1).strip()
                break
        
        if data['payer_name'] or data['payer_account']:
            return {
                'values': data,
                'confidence': 0.7
            }
        
        return None
    
    def _extract_bank_name(self, text):
        """Extract bank name from text"""
        south_african_banks = [
            'ABSA', 'Standard Bank', 'FNB', 'Nedbank', 'Capitec',
            'Investec', 'African Bank', 'Bidvest Bank', 'Discovery Bank',
            'TymeBank', 'Bank Zero'
        ]
        
        text_upper = text.upper()
        for bank in south_african_banks:
            if bank.upper() in text_upper:
                return {
                    'value': bank,
                    'confidence': 0.9
                }
        
        return None
    
    def validate_payment(self, extracted_amount, expected_amount, tolerance=0.01):
        """
        Validate extracted payment amount against expected invoice amount
        
        Args:
            extracted_amount: Amount extracted from POP
            expected_amount: Invoice total amount
            tolerance: Acceptable difference percentage (default 1%)
            
        Returns:
            dict: Validation result with status and details
        """
        if not extracted_amount or not expected_amount:
            return {
                'matched': False,
                'status': 'manual_review',
                'reason': 'Missing amount information'
            }
        
        extracted = Decimal(str(extracted_amount))
        expected = Decimal(str(expected_amount))
        
        difference = abs(extracted - expected)
        percentage_diff = (difference / expected) * 100 if expected > 0 else 100
        
        if difference == 0:
            return {
                'matched': True,
                'status': 'verified',
                'reason': 'Exact match',
                'difference': 0
            }
        elif percentage_diff <= (tolerance * 100):
            return {
                'matched': True,
                'status': 'verified',
                'reason': f'Within tolerance ({percentage_diff:.2f}% difference)',
                'difference': float(difference)
            }
        elif extracted > expected:
            return {
                'matched': False,
                'status': 'overpayment',
                'reason': f'Overpayment detected (R{difference:.2f} extra)',
                'difference': float(difference)
            }
        else:
            return {
                'matched': False,
                'status': 'underpayment',
                'reason': f'Underpayment detected (R{difference:.2f} short)',
                'difference': float(difference)
            }
