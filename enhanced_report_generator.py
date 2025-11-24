"""
Enhanced Medical Report Generator with Comprehensive Graphs and Recommendations
Generates professional diabetes assessment reports with clinical visualizations and actionable advice
"""

from io import BytesIO
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Wedge
import matplotlib.patches as mpatches

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def generate_comprehensive_health_chart(report_data):
    """Generate comprehensive 4-panel health visualization"""
    fig = plt.figure(figsize=(14, 10), facecolor='white')
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Extract all parameters
    glucose = float(report_data.get('Glucose', 0))
    bp = float(report_data.get('BloodPressure', 0))
    bmi = float(report_data.get('BMI', 0))
    insulin = float(report_data.get('Insulin', 0))
    skin_thickness = float(report_data.get('SkinThickness', 0))
    pregnancies = float(report_data.get('Pregnancies', 0))
    dpf = float(report_data.get('DiabetesPedigreeFunction', 0))
    age = float(report_data.get('Age', 0))
    
    # Panel 1: Parameter Bar Chart with Risk Zones
    ax1 = fig.add_subplot(gs[0, 0])
    params = ['Glucose\n(mg/dL)', 'Blood\nPressure', 'BMI', 'Insulin\n(μU/mL)']
    values = [glucose, bp, bmi, insulin]
    normal_ranges = [(70, 100), (60, 80), (18.5, 25), (16, 166)]
    warning_levels = [126, 90, 30, 200]
    
    colors_list = []
    for val, (min_val, max_val), warn in zip(values, normal_ranges, warning_levels):
        if min_val <= val <= max_val:
            colors_list.append('#10b981')  # Green
        elif val >= warn:
            colors_list.append('#ef4444')  # Red
        else:
            colors_list.append('#f59e0b')  # Amber
    
    x_pos = np.arange(len(params))
    bars = ax1.bar(x_pos, values, color=colors_list, edgecolor='#1e293b', linewidth=2, alpha=0.85, width=0.6)
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1e293b')
    
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(params, fontsize=10, fontweight='bold', color='#475569')
    ax1.set_title('Key Health Parameters', fontsize=13, fontweight='bold', color='#1e40af', pad=15)
    ax1.set_ylabel('Value', fontsize=11, fontweight='bold', color='#475569')
    ax1.grid(axis='y', linestyle=':', alpha=0.3, color='#94a3b8')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Panel 2: Risk Assessment Gauge
    ax2 = fig.add_subplot(gs[0, 1])
    prediction = int(report_data.get('prediction', 0))
    probability = float(report_data.get('probability', 0))
    
    # Create gauge
    theta = np.linspace(0, np.pi, 100)
    radius = 1
    
    # Background segments
    segments = [
        (0, np.pi/3, '#10b981', 'Low Risk'),
        (np.pi/3, 2*np.pi/3, '#f59e0b', 'Moderate'),
        (2*np.pi/3, np.pi, '#ef4444', 'High Risk')
    ]
    
    for start, end, color, label in segments:
        wedge = Wedge((0, 0), radius, np.degrees(start), np.degrees(end),
                     facecolor=color, edgecolor='white', linewidth=3, alpha=0.8)
        ax2.add_patch(wedge)
    
    # Needle
    if probability < 0.33:
        needle_angle = np.pi * (1 - probability * 1.5)  # Low risk
        risk_text = "LOW RISK"
        risk_color = '#10b981'
    elif probability < 0.67:
        needle_angle = np.pi * (0.67 - (probability - 0.33) * 1.5)  # Moderate
        risk_text = "MODERATE RISK"
        risk_color = '#f59e0b'
    else:
        needle_angle = np.pi * (0.33 - (probability - 0.67) * 1.5)  # High
        risk_text = "HIGH RISK"
        risk_color = '#ef4444'
    
    needle_x = radius * 0.7 * np.cos(needle_angle)
    needle_y = radius * 0.7 * np.sin(needle_angle)
    ax2.arrow(0, 0, needle_x, needle_y, head_width=0.15, head_length=0.1,
             fc='#1e293b', ec='#1e293b', linewidth=3, zorder=10)
    
    # Center circle
    circle = plt.Circle((0, 0), 0.12, color='#1e293b', zorder=11)
    ax2.add_patch(circle)
    
    ax2.text(0, -0.4, risk_text, ha='center', va='top',
            fontsize=16, fontweight='bold', color=risk_color)
    ax2.text(0, -0.55, f'{probability*100:.1f}% Probability',
            ha='center', va='top', fontsize=12, color='#475569')
    
    ax2.set_xlim(-1.3, 1.3)
    ax2.set_ylim(-0.7, 1.3)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('Diabetes Risk Assessment', fontsize=13, fontweight='bold',
                 color='#1e40af', pad=10)
    
    # Panel 3: Radar Chart for All Features
    ax3 = fig.add_subplot(gs[1, 0], projection='polar')
    
    categories = ['Glucose', 'BP', 'BMI', 'Insulin', 'Skin', 'Preg.', 'DPF', 'Age']
    
    # Normalize values to 0-100 scale
    max_values = [200, 120, 40, 300, 99, 17, 2.5, 81]
    normalized_values = [
        min(100, (glucose / max_values[0]) * 100),
        min(100, (bp / max_values[1]) * 100),
        min(100, (bmi / max_values[2]) * 100),
        min(100, (insulin / max_values[3]) * 100),
        min(100, (skin_thickness / max_values[4]) * 100),
        min(100, (pregnancies / max_values[5]) * 100),
        min(100, (dpf / max_values[6]) * 100),
        min(100, (age / max_values[7]) * 100)
    ]
    
    # Close the plot
    normalized_values += normalized_values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]
    
    ax3.plot(angles, normalized_values, 'o-', linewidth=2, color='#3b82f6', markersize=8)
    ax3.fill(angles, normalized_values, alpha=0.25, color='#3b82f6')
    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(categories, size=10, fontweight='bold', color='#475569')
    ax3.set_ylim(0, 100)
    ax3.set_yticks([25, 50, 75, 100])
    ax3.set_yticklabels(['25', '50', '75', '100'], size=8, color='#94a3b8')
    ax3.set_title('Comprehensive Health Profile', fontsize=13, fontweight='bold',
                 color='#1e40af', pad=20)
    ax3.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
    
    # Panel 4: BMI Classification
    ax4 = fig.add_subplot(gs[1, 1])
    
    ranges = [
        ('Underweight', 0, 18.5, '#3b82f6'),
        ('Normal', 18.5, 25, '#10b981'),
        ('Overweight', 25, 30, '#f59e0b'),
        ('Obese', 30, 40, '#ef4444')
    ]
    
    y_pos = 0.5
    for label, start, end, color in ranges:
        width = end - start
        rect = Rectangle((start, y_pos-0.15), width, 0.3,
                        facecolor=color, edgecolor='#1e293b',
                        linewidth=2, alpha=0.8)
        ax4.add_patch(rect)
        ax4.text((start + end)/2, y_pos, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')
    
    # Plot patient's BMI
    ax4.plot(bmi, y_pos, 'D', markersize=15, color='#1e293b',
            markeredgewidth=2, markeredgecolor='white', zorder=10)
    ax4.annotate(f'Your BMI: {bmi:.1f}', xy=(bmi, y_pos),
                xytext=(bmi, y_pos+0.35),
                ha='center', fontsize=11, fontweight='bold', color='#1e293b',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                         edgecolor='#1e293b', linewidth=2),
                arrowprops=dict(arrowstyle='->', lw=2, color='#1e293b'))
    
    ax4.set_xlim(0, 40)
    ax4.set_ylim(0, 1)
    ax4.set_xlabel('BMI (kg/m²)', fontsize=11, fontweight='bold', color='#475569')
    ax4.set_title('Body Mass Index Classification', fontsize=13, fontweight='bold',
                 color='#1e40af', pad=15)
    ax4.set_yticks([])
    ax4.set_xticks([0, 10, 18.5, 25, 30, 40])
    ax4.tick_params(axis='x', labelsize=9, colors='#475569')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_visible(False)
    ax4.grid(axis='x', linestyle=':', alpha=0.3, color='#94a3b8')
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer


def get_personalized_recommendations(report_data):
    """Generate personalized health recommendations based on patient data"""
    glucose = float(report_data.get('Glucose', 0))
    bp = float(report_data.get('BloodPressure', 0))
    bmi = float(report_data.get('BMI', 0))
    insulin = float(report_data.get('Insulin', 0))
    age = float(report_data.get('Age', 0))
    prediction = int(report_data.get('prediction', 0))
    probability = float(report_data.get('probability', 0))
    
    recommendations = []
    
    # Risk-based general recommendations
    if prediction == 1 or probability > 0.5:
        recommendations.append({
            'category': '🔴 HIGH PRIORITY - Immediate Action Required',
            'items': [
                'Schedule an appointment with an endocrinologist within 1-2 weeks',
                'Start daily blood glucose monitoring (fasting and post-meal)',
                'Consult with a certified diabetes educator',
                'Get HbA1c test to assess long-term glucose control'
            ]
        })
    else:
        recommendations.append({
            'category': '✅ Prevention Focus - Maintain Healthy Habits',
            'items': [
                'Continue regular health check-ups (every 6 months)',
                'Maintain current healthy lifestyle practices',
                'Monitor blood sugar annually',
                'Stay informed about diabetes prevention'
            ]
        })
    
    # Glucose-specific recommendations
    if glucose > 126:
        recommendations.append({
            'category': '🍬 Blood Glucose Management',
            'items': [
                f'Your glucose level ({glucose:.0f} mg/dL) is elevated - target: <100 mg/dL fasting',
                'Limit refined carbohydrates and sugary foods',
                'Eat smaller, frequent meals (5-6 times/day)',
                'Choose low glycemic index foods (whole grains, legumes)',
                'Avoid sugary drinks - drink water, unsweetened tea',
                'Include cinnamon and fenugreek in your diet (consult doctor)'
            ]
        })
    elif glucose > 100:
        recommendations.append({
            'category': '🍬 Blood Glucose - Borderline',
            'items': [
                f'Your glucose ({glucose:.0f} mg/dL) is pre-diabetic range',
                'Reduce intake of refined carbs and sugar',
                'Increase fiber intake (vegetables, whole grains)',
                'Regular exercise to improve insulin sensitivity'
            ]
        })
    
    # BMI-specific recommendations
    if bmi > 30:
        recommendations.append({
            'category': '⚖️ Weight Management - Obesity',
            'items': [
                f'Your BMI ({bmi:.1f}) indicates obesity - target: <25',
                'Aim for 5-10% weight loss initially (significant health benefits)',
                'Consult a registered dietitian for personalized meal plan',
                'Start with 150 minutes moderate exercise per week',
                'Consider behavioral therapy or support groups',
                'Track daily calorie intake using apps'
            ]
        })
    elif bmi > 25:
        recommendations.append({
            'category': '⚖️ Weight Management - Overweight',
            'items': [
                f'Your BMI ({bmi:.1f}) is in overweight range',
                'Target gradual weight loss: 0.5-1 kg per week',
                'Reduce portion sizes by 20-30%',
                'Increase physical activity to 200 minutes/week',
                'Practice mindful eating'
            ]
        })
    elif bmi < 18.5:
        recommendations.append({
            'category': '⚖️ Weight Management - Underweight',
            'items': [
                f'Your BMI ({bmi:.1f}) indicates underweight',
                'Consult healthcare provider to rule out underlying conditions',
                'Increase calorie intake with nutrient-dense foods',
                'Include healthy fats (nuts, avocado, olive oil)',
                'Consider strength training to build muscle mass'
            ]
        })
    
    # Blood Pressure recommendations
    if bp > 90:
        recommendations.append({
            'category': '💓 Blood Pressure Management',
            'items': [
                f'Your blood pressure ({bp:.0f} mmHg) is elevated',
                'Reduce sodium intake to <2300mg/day (ideal: <1500mg)',
                'Increase potassium-rich foods (bananas, spinach, beans)',
                'Practice stress management: meditation, yoga, deep breathing',
                'Limit alcohol consumption',
                'Monitor BP at home regularly'
            ]
        })
    
    # Insulin recommendations
    if insulin > 200 or insulin < 16:
        recommendations.append({
            'category': '💉 Insulin Sensitivity',
            'items': [
                f'Your insulin level ({insulin:.0f} μU/mL) is concerning',
                'Focus on insulin-sensitizing foods (leafy greens, berries)',
                'Include omega-3 fatty acids (fish, flaxseeds)',
                'Regular aerobic exercise (30 min/day)',
                'Avoid prolonged sitting - move every hour',
                'Consult endocrinologist for detailed assessment'
            ]
        })
    
    # Diet recommendations (universal)
    recommendations.append({
        'category': '🥗 Dietary Guidelines',
        'items': [
            'Follow the plate method: 1/2 vegetables, 1/4 lean protein, 1/4 whole grains',
            'Include 5 servings of vegetables and 2 servings of fruits daily',
            'Choose lean proteins: fish, chicken, legumes, tofu',
            'Healthy fats: nuts, seeds, olive oil, avocado',
            'Stay hydrated: 8-10 glasses of water daily',
            'Limit processed foods, trans fats, and saturated fats',
            'Read food labels - watch for hidden sugars'
        ]
    })
    
    # Exercise recommendations
    recommendations.append({
        'category': '🏃 Physical Activity',
        'items': [
            'Aim for 150 minutes moderate-intensity exercise per week',
            'Include both aerobic (walking, swimming) and resistance training',
            'Start slowly if sedentary: 10-minute walks, gradually increase',
            'Exercise timing: 30-60 minutes after meals to reduce glucose spikes',
            'Track steps: aim for 7,000-10,000 steps/day',
            'Find activities you enjoy to ensure consistency',
            'Always warm up (5 min) and cool down (5 min)'
        ]
    })
    
    # Lifestyle recommendations
    recommendations.append({
        'category': '🌟 Lifestyle Modifications',
        'items': [
            'Get 7-9 hours quality sleep nightly',
            'Manage stress through relaxation techniques',
            'Quit smoking (increases diabetes risk by 30-40%)',
            'Limit alcohol: max 1 drink/day (women), 2/day (men)',
            'Maintain consistent meal and sleep schedules',
            'Build a support system: family, friends, support groups',
            'Regular dental and eye check-ups'
        ]
    })
    
    # Monitoring recommendations
    recommendations.append({
        'category': '📊 Regular Monitoring',
        'items': [
            'Schedule follow-up appointments as recommended',
            'Keep a health journal: diet, exercise, symptoms',
            'Regular lab tests: HbA1c (every 3-6 months), lipid panel',
            'Annual comprehensive eye exam',
            'Foot examination at each doctor visit',
            'Blood pressure monitoring',
            'Track progress with measurable goals'
        ]
    })
    
    # Age-specific recommendations
    if age > 45:
        recommendations.append({
            'category': '👴 Age-Related Considerations',
            'items': [
                'Annual comprehensive health screening',
                'Calcium and Vitamin D supplementation (consult doctor)',
                'Low-impact exercises to protect joints',
                'Regular bone density testing',
                'Cognitive health activities (puzzles, reading, social engagement)'
            ]
        })
    
    return recommendations


def format_recommendations_for_pdf(recommendations, body_style):
    """Format recommendations as PDF elements"""
    from reportlab.platypus import Paragraph, Spacer, Bullet
    
    elements = []
    
    for rec_group in recommendations:
        # Category header with colored background
        category = rec_group['category']
        category_style = ParagraphStyle(
            'CategoryHeader',
            parent=body_style,
            fontSize=12,
            textColor=colors.white,
            backColor=colors.HexColor('#3b82f6'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            leftIndent=8,
            rightIndent=8,
            leading=16
        )
        elements.append(Paragraph(category, category_style))
        elements.append(Spacer(1, 0.05*inch))
        
        # Items
        for item in rec_group['items']:
            bullet_text = f"• {item}"
            bullet_style = ParagraphStyle(
                'BulletText',
                parent=body_style,
                fontSize=10,
                leading=14,
                leftIndent=20,
                rightIndent=10,
                spaceAfter=4
            )
            elements.append(Paragraph(bullet_text, bullet_style))
        
        elements.append(Spacer(1, 0.1*inch))
    
    return elements
