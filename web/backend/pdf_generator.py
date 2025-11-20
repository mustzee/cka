"""
PDF 리포트 및 인증서 생성기
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import qrcode
from io import BytesIO


class PDFReportGenerator:
    """PDF 리포트 생성기"""

    def __init__(self, output_dir: str = "results/pdf"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, session_data: dict) -> str:
        """
        시험 리포트 PDF 생성

        Args:
            session_data: 시험 세션 데이터

        Returns:
            PDF 파일 경로
        """
        filename = f"exam_report_{session_data['session_id']}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # 제목 스타일
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        # 제목
        story.append(Paragraph("CKA 시험 리포트", title_style))
        story.append(Spacer(1, 0.5 * inch))

        # 기본 정보
        info_data = [
            ['시험 타입', f"Type {session_data['exam_type']}"],
            ['세션 ID', session_data['session_id']],
            ['시험 날짜', session_data.get('start_time', '')[:19]],
            ['소요 시간', self._calculate_duration(session_data)],
        ]

        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f3ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.5 * inch))

        # 점수 정보
        passed = session_data.get('passed', False)
        percentage = session_data.get('percentage', 0)

        score_style = ParagraphStyle(
            'Score',
            parent=styles['Normal'],
            fontSize=18,
            textColor=colors.green if passed else colors.red,
            alignment=TA_CENTER,
        )

        story.append(Paragraph(
            f"<b>{'✓ 합격' if passed else '✗ 불합격'}</b>",
            score_style
        ))
        story.append(Spacer(1, 0.2 * inch))

        score_data = [
            ['획득 점수', f"{session_data.get('total_score', 0):.1f}"],
            ['총점', str(session_data.get('total_weight', 0))],
            ['정답률', f"{percentage:.1f}%"],
            ['합격 기준', '66%'],
        ]

        score_table = Table(score_data, colWidths=[3 * inch, 3 * inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        story.append(score_table)
        story.append(PageBreak())

        # 문제별 결과
        story.append(Paragraph("문제별 결과", styles['Heading2']))
        story.append(Spacer(1, 0.3 * inch))

        results = session_data.get('results', [])
        for idx, result in enumerate(results, 1):
            result_data = [
                ['문제 번호', str(idx)],
                ['제목', result.get('title', '')],
                ['점수', f"{result.get('score', 0):.1f} / {result.get('weight', 0)}"],
                ['결과', '✓ 정답' if result.get('passed') else '✗ 오답'],
            ]

            result_table = Table(result_data, colWidths=[1.5 * inch, 4.5 * inch])
            bg_color = colors.HexColor('#d4edda') if result.get('passed') else colors.HexColor('#f8d7da')

            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            story.append(result_table)
            story.append(Spacer(1, 0.2 * inch))

        # 문서 생성
        doc.build(story)
        return filepath

    def _calculate_duration(self, session_data: dict) -> str:
        """시험 소요 시간 계산"""
        try:
            start = datetime.fromisoformat(session_data.get('start_time', ''))
            end = datetime.fromisoformat(session_data.get('end_time', ''))
            duration = end - start
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes}분"
        except:
            return "N/A"


class CertificateGenerator:
    """인증서 생성기"""

    def __init__(self, output_dir: str = "results/certificates"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_certificate(self, session_data: dict) -> str:
        """
        합격 인증서 생성

        Args:
            session_data: 시험 세션 데이터

        Returns:
            인증서 파일 경로
        """
        filename = f"certificate_{session_data['session_id']}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # 인증서 테두리
        story.append(Spacer(1, 1 * inch))

        # 제목
        title_style = ParagraphStyle(
            'CertTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )

        story.append(Paragraph("🏆 Certificate of Achievement", title_style))
        story.append(Spacer(1, 0.5 * inch))

        # 부제목
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=18,
            alignment=TA_CENTER,
        )

        story.append(Paragraph("This is to certify that", subtitle_style))
        story.append(Spacer(1, 0.3 * inch))

        # 이름 (가상)
        name_style = ParagraphStyle(
            'Name',
            parent=styles['Normal'],
            fontSize=28,
            textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )

        story.append(Paragraph("<u>CKA Candidate</u>", name_style))
        story.append(Spacer(1, 0.3 * inch))

        # 본문
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
        )

        story.append(Paragraph(
            f"has successfully passed the Kubernetes CKA Simulator Exam",
            body_style
        ))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(
            f"Type {session_data['exam_type']} with a score of {session_data['percentage']:.1f}%",
            body_style
        ))
        story.append(Spacer(1, 0.5 * inch))

        # 날짜 및 정보
        date_str = datetime.now().strftime("%B %d, %Y")
        info_data = [
            ['Date of Completion:', date_str],
            ['Certificate ID:', session_data['session_id']],
            ['Score:', f"{session_data['percentage']:.1f}%"],
        ]

        info_table = Table(info_data, colWidths=[2.5 * inch, 3.5 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.5 * inch))

        # QR 코드 (검증용)
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(f"CKA:{session_data['session_id']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # QR 코드를 BytesIO로 저장
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        # 임시 파일로 저장
        qr_temp_path = os.path.join(self.output_dir, f"qr_{session_data['session_id']}.png")
        qr_img.save(qr_temp_path)

        # QR 이미지 추가
        qr_image = Image(qr_temp_path, width=1.5*inch, height=1.5*inch)
        story.append(qr_image)

        # 서명 라인
        story.append(Spacer(1, 0.5 * inch))
        sig_style = ParagraphStyle(
            'Signature',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
        )
        story.append(Paragraph("_________________________", sig_style))
        story.append(Paragraph("CKA Simulator Authority", sig_style))

        # 문서 생성
        doc.build(story)

        # QR 코드 임시 파일 삭제
        if os.path.exists(qr_temp_path):
            os.remove(qr_temp_path)

        return filepath
