import pandas as pd
import os

# Configuration
excel_path = 'data/docs/20260108 Conference Plan.xlsx'
output_dir = 'data/docs/markdown'

sheets_to_extract = {
    '00 - Programme Briefs': 'programme_briefs.md',
    'Activity Details': 'activity_details.md',
    'Event Manpower': 'event_manpower.md',
    'Staffing': 'staffing.md',
    'Box & Materials': 'box_and_materials.md'
}

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load Excel file
print(f"Loading {excel_path}...")
try:
    xls = pd.ExcelFile(excel_path)
except Exception as e:
    print(f"Error loading Excel file: {e}")
    exit(1)

# Process each sheet
for sheet_name, output_filename in sheets_to_extract.items():
    print(f"Processing '{sheet_name}'...")
    
    if sheet_name not in xls.sheet_names:
        print(f"Warning: Sheet '{sheet_name}' not found in Excel file.")
        continue
        
    try:
        # Read sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Clean up dataframe (optional, but good for markdown)
        # 1. Fill NaN with empty string
        df = df.fillna('')
        
        # 2. Convert all columns to string to avoid formatting issues
        df = df.astype(str)
        
        # Convert to markdown
        markdown_content = df.to_markdown(index=False)
        
        # Save to file
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {sheet_name}\n\n")
            f.write(markdown_content)
            
        print(f"Saved {output_path}")
        
    except Exception as e:
        print(f"Error processing sheet '{sheet_name}': {e}")

print("Extraction complete.")
