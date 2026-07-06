import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf_report(bins_data, budget_data, output_path):
    """
    Generates a PDF report using ReportLab.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "EcoSync: Digital Waste Management Report")
    
    c.setFont("Helvetica", 12)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(50, height - 75, f"Generated on: {timestamp}")
    
    # Budget Section
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 120, "Financial Overview")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 145, f"Monthly Budget Limit: {budget_data.get('limit', 0):.2f} LKR")
    c.drawString(50, height - 165, f"Total Fuel Cost: {budget_data.get('total_fuel', 0):.2f} LKR")
    c.drawString(50, height - 185, f"Total Driver Cost: {budget_data.get('total_driver', 0):.2f} LKR")
    c.drawString(50, height - 205, f"Total Spent: {budget_data.get('total_spent', 0):.2f} LKR")
    
    # Bins Status Section
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 250, "Current Bin Status")
    
    y_pos = height - 275
    c.setFont("Helvetica", 12)
    for bin_info in bins_data:
        status = f"Location: {bin_info['location_name']} | Fill Level: {bin_info['fill_level']}%"
        c.drawString(50, y_pos, status)
        y_pos -= 20
        
        # Add new page if we run out of space
        if y_pos < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_pos = height - 50
            
    c.save()
    return output_path
