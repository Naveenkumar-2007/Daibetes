"""
Enhanced PDF Report Generator for Diabetes Risk Assessment
Generates comprehensive 2-page reports with visualizations and AI analysis
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image as RLImage, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pytz import timezone


def generate_health_visualizations(report):
    """Generate comprehensive 4-panel health visualization dashboard"""
    try:
        # Extract data with fallbacks
        glucose = float(report.get('Glucose') or report.get('glucose', 100))
        bmi = float(report.get('BMI') or report.get('bmi', 25))
        bp = float(report.get('BloodPressure') or report.get('blood_pressure', 70))
        insulin = float(report.get('Insulin') or report.get('insulin', 80))
        age = int(report.get('Age') or report.get('age', 30))
        dpf = float(report.get('DiabetesPedigreeFunction') or report.get('diabetes_pedigree', 0.5))
        
        # Determine risk
        prediction = report.get('prediction', 0)
        probability = report.get('probability', 0.5)
        if isinstance(probability, (int, float)):
            risk_score = probability if probability <= 1 else probability / 100
        else:
            risk_score = 0.5
        
        if isinstance(prediction, int):
            risk_level = 'High Risk' if prediction == 1 else 'Low Risk'
        else:
            risk_level = 'High Risk' if 'High' in str(prediction) else 'Low Risk'
        
        # Create figure
        fig = plt.figure(figsize=(10, 7))
        fig.patch.set_facecolor('white')
        
        # 1. Glucose Level Gauge (Top Left)
        ax1 = plt.subplot(2, 2, 1)
        ax1.set_xlim(0, 200)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        ax1.set_title('Glucose Level (mg/dL)', fontsize=11, fontweight='bold', pad=8)
        
        # Glucose ranges
        glucose_colors = ['#22c55e', '#fbbf24', '#ef4444']
        ranges = [(0, 100, 'Normal'), (100, 126, 'Prediabetes'), (126, 200, 'Diabetes')]
        for i, (start, end, label) in enumerate(ranges):
            ax1.barh(0, end-start, left=start, height=0.25, color=glucose_colors[i], alpha=0.8)
            ax1.text((start+end)/2, -0.15, label, ha='center', fontsize=8)
        
        # Glucose marker
        ax1.plot([glucose, glucose], [0, 0.25], 'b-', linewidth=3)
        ax1.plot(glucose, 0.125, 'bv', markersize=10)
        ax1.text(glucose, 0.45, f'{glucose:.0f}', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
        
        # 2. BMI Status (Top Right)
        ax2 = plt.subplot(2, 2, 2)
        ax2.set_xlim(15, 40)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('Body Mass Index (BMI)', fontsize=11, fontweight='bold', pad=8)
        
        bmi_colors = ['#3b82f6', '#22c55e', '#fbbf24', '#f97316', '#ef4444']
        bmi_ranges = [(15, 18.5, 'Under'), (18.5, 25, 'Normal'), (25, 30, 'Over'), 
                      (30, 35, 'Obese I'), (35, 40, 'Obese II')]
        
        for i, (start, end, label) in enumerate(bmi_ranges):
            ax2.barh(0, end-start, left=start, height=0.25, color=bmi_colors[i], alpha=0.8)
            ax2.text((start+end)/2, -0.15, label, ha='center', fontsize=7)
        
        ax2.plot([bmi, bmi], [0, 0.25], 'b-', linewidth=3)
        ax2.plot(bmi, 0.125, 'bv', markersize=10)
        ax2.text(bmi, 0.45, f'{bmi:.1f}', ha='center', fontsize=13, fontweight='bold', color='#1e40af')
        
        # 3. Health Parameters Radar (Bottom Left)
        ax3 = plt.subplot(2, 2, 3, projection='polar')
        
        categories = ['Glucose', 'BMI', 'BP', 'Insulin', 'Age', 'DPF']
        
        # Normalize to 0-100
        values = [
            min(glucose / 2, 100),
            min(bmi * 2.5, 100),
            min(bp * 1.25, 100),
            min(insulin / 2, 100),
            min(age * 1.25, 100),
            min(dpf * 100, 100)
        ]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values_plot = values + values[:1]
        angles_plot = angles + angles[:1]
        
        ax3.plot(angles_plot, values_plot, 'o-', linewidth=2, color='#3b82f6', markersize=6)
        ax3.fill(angles_plot, values_plot, alpha=0.25, color='#3b82f6')
        ax3.set_xticks(angles)
        ax3.set_xticklabels(categories, fontsize=9)
        ax3.set_ylim(0, 100)
        ax3.set_yticks([25, 50, 75, 100])
        ax3.set_yticklabels(['25', '50', '75', '100'], fontsize=7, color='gray')
        ax3.grid(True, linestyle='--', alpha=0.6, linewidth=0.5)
        ax3.set_title('Health Parameters Profile', fontsize=11, fontweight='bold', pad=15)
        
        # 4. Risk Assessment Gauge (Bottom Right)
        ax4 = plt.subplot(2, 2, 4)
        ax4.set_xlim(-1.5, 1.5)
        ax4.set_ylim(-0.3, 1.5)
        ax4.axis('off')
        ax4.set_title('Diabetes Risk Assessment', fontsize=11, fontweight='bold', pad=8)
        
        # Semi-circle gauge
        theta = np.linspace(0, np.pi, 100)
        
        # Color zones
        ax4.fill_between(np.cos(theta[0:33]) * 1.2, 0, np.sin(theta[0:33]) * 1.2, 
                        color='#22c55e', alpha=0.7)
        ax4.fill_between(np.cos(theta[33:66]) * 1.2, 0, np.sin(theta[33:66]) * 1.2, 
                        color='#fbbf24', alpha=0.7)
        ax4.fill_between(np.cos(theta[66:100]) * 1.2, 0, np.sin(theta[66:100]) * 1.2, 
                        color='#ef4444', alpha=0.7)
        
        # Needle
        needle_angle = np.pi * (1 - risk_score)
        needle_x = [0, np.cos(needle_angle) * 1.0]
        needle_y = [0, np.sin(needle_angle) * 1.0]
        ax4.plot(needle_x, needle_y, 'k-', linewidth=4)
        ax4.plot(0, 0, 'ko', markersize=10)
        
        # Labels
        ax4.text(0, -0.2, f'{risk_score*100:.1f}%', ha='center', fontsize=16, fontweight='bold', color='#1e40af')
        risk_color = '#ef4444' if 'High' in risk_level else '#22c55e'
        ax4.text(0, 1.35, risk_level, ha='center', fontsize=12, fontweight='bold', color=risk_color)
        ax4.text(-1.1, -0.05, 'Low\n0%', ha='center', fontsize=8, color='gray')
        ax4.text(0, 1.25, '50%', ha='center', fontsize=8, color='gray')
        ax4.text(1.1, -0.05, 'High\n100%', ha='center', fontsize=8, color='gray')
        
        plt.tight_layout(rect=[0, 0, 1, 0.97])
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        plt.close()
        
        return buffer
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_enhanced_pdf_report(report, report_id):
    """
    Generate comprehensive 2-page PDF report with professional layout and visualizations
    
    Args:
        report (dict): Report data containing patient info and health metrics
        report_id (str): Unique report identifier
        
    Returns:
        BytesIO: PDF file buffer
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=0.6*inch, leftMargin=0.6*inch,
                          topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica'
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.white,
        backColor=colors.HexColor('#3b82f6'),
        borderPadding=(8, 10, 8, 10),
        spaceAfter=10,
        spaceBefore=14,
        fontName='Helvetica-Bold'
    )
    
    body_text = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        alignment=TA_LEFT
    )
    
    # ===== PAGE 1: REPORT HEADER & PATIENT DATA =====
    
    # Header with blue accent bar
    header_table = Table([['']], colWidths=[7*inch], rowHeights=[0.25*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Title
    story.append(Paragraph("<b>DIABETES RISK ASSESSMENT REPORT</b>", title_style))
    story.append(Paragraph("AI-Powered Health Analysis & Predictions", subtitle_style))
    
    # Report Info Bar
    ist = timezone('Asia/Kolkata')
    try:
        timestamp = report.get('timestamp') or report.get('created_at')
        if timestamp:
            if isinstance(timestamp, str):
                date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                date_obj = datetime.fromtimestamp(timestamp)
            date_obj = date_obj.astimezone(ist)
            formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p IST")
        else:
            formatted_date = datetime.now(ist).strftime("%B %d, %Y at %I:%M %p IST")
    except:
        formatted_date = datetime.now(ist).strftime("%B %d, %Y at %I:%M %p IST")
    
    info_data = [[f"Report ID: {report_id}", f"Generated: {formatted_date}"]]
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#64748b')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.2*inch))
    
    # DIAGNOSIS
    story.append(Paragraph("DIAGNOSIS", section_heading))
    
    prediction = report.get('prediction', 0)
    if isinstance(prediction, int):
        result_text = 'High Risk - Diabetes Detected' if prediction == 1 else 'Low Risk - No Diabetes'
        result_color = '#dc2626' if prediction == 1 else '#16a34a'
    else:
        result_text = str(prediction)
        result_color = '#dc2626' if 'High' in result_text else '#16a34a'
    
    diagnosis_style = ParagraphStyle(
        'Diagnosis',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor(result_color),
        spaceAfter=10,
        spaceBefore=5,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(f"<b>{result_text}</b>", diagnosis_style))
    
    # Confidence
    confidence = report.get('probability', 0.5)
    if isinstance(confidence, (int, float)):
        conf_pct = confidence * 100 if confidence <= 1 else confidence
    else:
        conf_pct = 50
    
    story.append(Paragraph(f"Confidence Level: <b>{conf_pct:.1f}%</b>", body_text))
    story.append(Spacer(1, 0.15*inch))
    
    # PATIENT INFORMATION
    story.append(Paragraph("PATIENT INFORMATION", section_heading))
    
    patient_name = report.get('patient_name', report.get('name', 'Unknown'))
    age = report.get('Age') or report.get('age', 'N/A')
    sex = report.get('sex', 'N/A')
    contact = report.get('contact', 'N/A')
    
    patient_data = [
        ['Patient Name:', patient_name, 'Age:', f'{age} years'],
        ['Gender:', sex, 'Contact:', contact],
        ['Report Date:', formatted_date[:20], '', '']
    ]
    
    patient_table = Table(patient_data, colWidths=[1.4*inch, 2.1*inch, 1.2*inch, 2.3*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e0f2fe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#0284c7')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.15*inch))
    
    # HEALTH METRICS
    story.append(Paragraph("HEALTH METRICS", section_heading))
    
    glucose = report.get('Glucose') or report.get('glucose', 'N/A')
    bmi = report.get('BMI') or report.get('bmi', 'N/A')
    bp = report.get('BloodPressure') or report.get('blood_pressure', 'N/A')
    insulin = report.get('Insulin') or report.get('insulin', 'N/A')
    skin = report.get('SkinThickness') or report.get('skin_thickness', 'N/A')
    pregnancies = report.get('Pregnancies') or report.get('pregnancies', 'N/A')
    dpf = report.get('DiabetesPedigreeFunction') or report.get('diabetes_pedigree', 'N/A')
    
    metrics_data = [
        ['Parameter', 'Value', 'Unit', 'Normal Range'],
        ['Glucose', str(glucose), 'mg/dL', '70-100'],
        ['Blood Pressure', str(bp), 'mmHg', '60-80 (diastolic)'],
        ['Body Mass Index', str(bmi), 'kg/m²', '18.5-24.9'],
        ['Insulin', str(insulin), 'μU/mL', '16-166'],
        ['Skin Thickness', str(skin), 'mm', '10-50'],
        ['Pregnancies', str(pregnancies), 'count', '-'],
        ['Diabetes Pedigree', str(dpf), 'function', '0.0-2.5']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.2*inch, 1.3*inch, 1.3*inch, 1.9*inch])
    metrics_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metrics_table)
    
    # PAGE BREAK
    story.append(PageBreak())
    
    # ===== PAGE 2: VISUALIZATIONS & AI ANALYSIS =====
    
    # Add header on page 2
    story.append(header_table)
    story.append(Spacer(1, 0.1*inch))
    
    # HEALTH VISUALIZATION DASHBOARD
    story.append(Paragraph("COMPREHENSIVE HEALTH ANALYSIS", section_heading))
    story.append(Spacer(1, 0.08*inch))
    
    # Generate and add visualization
    chart_buffer = generate_health_visualizations(report)
    if chart_buffer:
        chart_img = RLImage(chart_buffer, width=7*inch, height=4.8*inch)
        story.append(chart_img)
        story.append(Spacer(1, 0.15*inch))
    
    # AI ANALYSIS
    ai_analysis = report.get('ai_analysis', '')
    if ai_analysis:
        story.append(Paragraph("AI MEDICAL ANALYSIS", section_heading))
        
        # Split into paragraphs
        analysis_paragraphs = ai_analysis.split('\n\n')
        for para in analysis_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_text))
                story.append(Spacer(1, 0.08*inch))
    
    # RISK FACTORS
    risk_factors = report.get('risk_factors', [])
    if risk_factors and len(risk_factors) > 0:
        story.append(Paragraph("IDENTIFIED RISK FACTORS", section_heading))
        
        for i, factor in enumerate(risk_factors[:5], 1):  # Limit to 5
            story.append(Paragraph(f"<b>{i}.</b> {factor}", body_text))
            story.append(Spacer(1, 0.05*inch))
        
        story.append(Spacer(1, 0.1*inch))
    
    # RECOMMENDATIONS
    recommendations = report.get('recommendations', [])
    if recommendations and len(recommendations) > 0:
        story.append(Paragraph("HEALTH RECOMMENDATIONS", section_heading))
        
        for i, rec in enumerate(recommendations[:6], 1):  # Limit to 6
            story.append(Paragraph(f"<b>{i}.</b> {rec}", body_text))
            story.append(Spacer(1, 0.05*inch))
    
    # FOOTER
    story.append(Spacer(1, 0.15*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    story.append(Paragraph("<i>This report is generated by AI-assisted diagnostic technology and should be reviewed by a qualified healthcare professional.</i>", footer_style))
    story.append(Paragraph(f"<i>Report ID: {report_id} | Generated: {formatted_date}</i>", footer_style))
    story.append(Paragraph("<i>© 2025 Diabetes Risk Predictor | All Rights Reserved</i>", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
