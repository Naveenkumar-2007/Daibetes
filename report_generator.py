"""
Professional Medical Report Generator with Traditional Graphs
Generates comprehensive diabetes assessment reports with clinical visualizations
"""

from io import BytesIO
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


def generate_clinical_parameter_chart(report_data):
    """Generate traditional bar chart with parameter values and reference ranges"""
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    
    # Extract parameters
    params = {
        'Glucose\n(mg/dL)': {
            'value': float(report_data.get('Glucose', 0)),
            'normal_min': 70,
            'normal_max': 100,
            'warning': 126
        },
        'Blood Pressure\n(mmHg)': {
            'value': float(report_data.get('BloodPressure', 0)),
            'normal_min': 60,
            'normal_max': 80,
            'warning': 90
        },
        'BMI\n(kg/m²)': {
            'value': float(report_data.get('BMI', 0)),
            'normal_min': 18.5,
            'normal_max': 24.9,
            'warning': 30
        },
        'Insulin\n(μU/mL)': {
            'value': float(report_data.get('Insulin', 0)),
            'normal_min': 16,
            'normal_max': 166,
            'warning': 200
        },
        'Skin Thick.\n(mm)': {
            'value': float(report_data.get('SkinThickness', 0)),
            'normal_min': 10,
            'normal_max': 50,
            'warning': 60
        }
    }
    
    labels = list(params.keys())
    values = [params[k]['value'] for k in labels]
    colors_list = []
    
    # Determine color based on value vs normal range
    for label in labels:
        val = params[label]['value']
        if params[label]['normal_min'] <= val <= params[label]['normal_max']:
            colors_list.append('#10b981')  # Green - Normal
        elif val >= params[label]['warning']:
            colors_list.append('#ef4444')  # Red - High risk
        else:
            colors_list.append('#f59e0b')  # Amber - Borderline
    
    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, values, color=colors_list, edgecolor='#1e293b', linewidth=1.5, alpha=0.85)
    
    # Add reference range indicators
    for i, label in enumerate(labels):
        # Normal range shading
        normal_min = params[label]['normal_min']
        normal_max = params[label]['normal_max']
        ax.axhline(y=normal_max, xmin=(i-0.3)/len(labels), xmax=(i+0.3)/len(labels), 
                   color='#10b981', linestyle='--', linewidth=1.5, alpha=0.6)
        ax.axhline(y=normal_min, xmin=(i-0.3)/len(labels), xmax=(i+0.3)/len(labels), 
                   color='#10b981', linestyle='--', linewidth=1.5, alpha=0.6)
        
        # Add value labels on top of bars
        height = bars[i].get_height()
        ax.text(bars[i].get_x() + bars[i].get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontweight='bold', fontsize=10, color='#1e293b')
    
    ax.set_xlabel('Clinical Parameters', fontsize=13, fontweight='bold', color='#1e293b')
    ax.set_ylabel('Values', fontsize=13, fontweight='bold', color='#1e293b')
    ax.set_title('Laboratory Values vs. Reference Ranges', fontsize=15, fontweight='bold', 
                 color='#1e40af', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=10, color='#475569')
    ax.yaxis.set_tick_params(labelsize=10, colors='#475569')
    ax.grid(axis='y', linestyle=':', alpha=0.3, color='#94a3b8')
    ax.set_axisbelow(True)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#10b981', edgecolor='#1e293b', label='Normal Range'),
        mpatches.Patch(facecolor='#f59e0b', edgecolor='#1e293b', label='Borderline'),
        mpatches.Patch(facecolor='#ef4444', edgecolor='#1e293b', label='High Risk')
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.95, fontsize=10)
    
    plt.tight_layout()
    
    # Save to BytesIO
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer


def generate_risk_gauge_chart(confidence, risk_level):
    """Generate a gauge/speedometer chart showing diabetes risk level"""
    fig, ax = plt.subplots(figsize=(8, 5), subplot_kw={'projection': 'polar'}, facecolor='white')
    
    # Create gauge
    theta = np.linspace(0, np.pi, 100)
    
    # Risk zones
    low_zone = theta[theta < np.pi/3]
    medium_zone = theta[(theta >= np.pi/3) & (theta < 2*np.pi/3)]
    high_zone = theta[theta >= 2*np.pi/3]
    
    # Plot zones
    ax.fill_between(low_zone, 0, 1, color='#10b981', alpha=0.7, label='Low Risk')
    ax.fill_between(medium_zone, 0, 1, color='#f59e0b', alpha=0.7, label='Moderate Risk')
    ax.fill_between(high_zone, 0, 1, color='#ef4444', alpha=0.7, label='High Risk')
    
    # Determine needle position based on confidence and risk
    if risk_level.lower() == 'high':
        needle_angle = np.pi * (0.66 + 0.33 * (float(confidence) / 100))
    else:
        needle_angle = np.pi * (0.33 * (float(confidence) / 100))
    
    # Draw needle
    ax.arrow(needle_angle, 0, 0, 0.9, width=0.04, head_width=0.15, head_length=0.1,
             fc='#1e293b', ec='#1e293b', linewidth=2, zorder=5)
    
    # Center circle
    center_circle = plt.Circle((0, 0), 0.15, color='#1e293b', zorder=6)
    ax.add_patch(center_circle)
    
    ax.set_ylim(0, 1)
    ax.set_theta_zero_location('W')
    ax.set_theta_direction(1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)
    ax.set_title(f'Diabetes Risk Assessment\n{risk_level.upper()} ({confidence}% Confidence)', 
                 fontsize=14, fontweight='bold', color='#1e40af', pad=30)
    
    # Legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, 
              framealpha=0.95, fontsize=10)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer


def generate_parameter_radar_chart(report_data):
    """Generate radar/spider chart showing all health parameters"""
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'), facecolor='white')
    
    # Parameters (normalized to 0-100 scale)
    categories = ['Glucose\nControl', 'Blood\nPressure', 'Weight\nManagement', 
                  'Insulin\nLevel', 'Genetic\nRisk', 'Age\nFactor']
    
    # Normalize values to 0-100 scale
    glucose = min(100, (float(report_data.get('Glucose', 100)) / 200) * 100)
    bp = min(100, (float(report_data.get('BloodPressure', 80)) / 120) * 100)
    bmi = min(100, (float(report_data.get('BMI', 25)) / 40) * 100)
    insulin = min(100, (float(report_data.get('Insulin', 100)) / 300) * 100)
    dpf = min(100, float(report_data.get('DiabetesPedigreeFunction', 0.5)) * 50)
    age = min(100, (float(report_data.get('Age', 40)) / 80) * 100)
    
    values = [glucose, bp, bmi, insulin, dpf, age]
    
    # Number of variables
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    values += values[:1]  # Complete the circle
    angles += angles[:1]
    
    # Plot
    ax.plot(angles, values, 'o-', linewidth=2, color='#2563eb', label='Current Values')
    ax.fill(angles, values, alpha=0.25, color='#3b82f6')
    
    # Ideal/target range
    target_values = [50, 50, 50, 50, 30, 50]  # Target ranges
    target_values += target_values[:1]
    ax.plot(angles, target_values, 'o--', linewidth=2, color='#10b981', 
            label='Target Range', alpha=0.7)
    ax.fill(angles, target_values, alpha=0.1, color='#10b981')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, color='#475569')
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25', '50', '75', '100'], fontsize=9, color='#64748b')
    ax.grid(True, linestyle=':', alpha=0.5, color='#94a3b8')
    ax.set_title('Comprehensive Health Parameter Analysis', fontsize=14, fontweight='bold',
                 color='#1e40af', pad=25)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.95, fontsize=10)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer


def generate_bmi_classification_chart(bmi_value):
    """Generate BMI classification visual chart"""
    fig, ax = plt.subplots(figsize=(10, 3), facecolor='white')
    
    # BMI ranges
    ranges = [
        ('Underweight', 0, 18.5, '#3b82f6'),
        ('Normal', 18.5, 25, '#10b981'),
        ('Overweight', 25, 30, '#f59e0b'),
        ('Obese', 30, 40, '#ef4444')
    ]
    
    y_pos = 0.5
    for label, start, end, color in ranges:
        width = end - start
        rect = FancyBboxPatch((start, y_pos-0.15), width, 0.3, 
                              boxstyle="round,pad=0.02", 
                              facecolor=color, edgecolor='#1e293b', 
                              linewidth=2, alpha=0.8)
        ax.add_patch(rect)
        ax.text((start + end)/2, y_pos, label, ha='center', va='center',
                fontsize=11, fontweight='bold', color='white')
    
    # Plot patient's BMI
    bmi = float(bmi_value)
    ax.plot(bmi, y_pos, 'D', markersize=15, color='#1e293b', 
            markeredgewidth=2, markeredgecolor='white', zorder=10)
    ax.annotate(f'Your BMI: {bmi:.1f}', xy=(bmi, y_pos), 
                xytext=(bmi, y_pos+0.35),
                ha='center', fontsize=12, fontweight='bold', color='#1e293b',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#1e293b', linewidth=2),
                arrowprops=dict(arrowstyle='->', lw=2, color='#1e293b'))
    
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 1)
    ax.set_xlabel('BMI (kg/m²)', fontsize=13, fontweight='bold', color='#1e293b')
    ax.set_title('Body Mass Index Classification', fontsize=14, fontweight='bold',
                 color='#1e40af', pad=15)
    ax.set_yticks([])
    ax.set_xticks([0, 10, 18.5, 25, 30, 40])
    ax.tick_params(axis='x', labelsize=10, colors='#475569')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', linestyle=':', alpha=0.3, color='#94a3b8')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    plt.close(fig)
    
    return img_buffer
