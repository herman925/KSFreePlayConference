import pandas as pd
import json
import os
import re
# from bs4 import BeautifulSoup # Removing bs4 dependency to avoid install issues if not present, using simple string replace or just standard file IO if possible. 
# Actually, I should check if beautifulsoup4 is installed. If not, I'll install it.
# Assuming standard environment, but let's be safe.
# I'll include a check.

# Configuration
EXCEL_PATH = r'c:\Users\hkkchan\Downloads\KSWellBeingRetreat\data\docs\20260108 Conference Plan.xlsx'
DATA_DIR = r'c:\Users\hkkchan\Downloads\KSWellBeingRetreat\data'
PAGES_DIR = r'c:\Users\hkkchan\Downloads\KSWellBeingRetreat\pages'
TASKS_DIR = os.path.join(DATA_DIR, 'tasks')

def slugify(text):
    if not isinstance(text, str):
        return str(text)
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def load_excel():
    return pd.ExcelFile(EXCEL_PATH)

def process_staffing_and_tasks(xls):
    print("Processing Staffing and Tasks...")
    
    # --- 1. Process Staffing to get Roles ---
    try:
        df_staff = pd.read_excel(xls, sheet_name='Staffing')
    except Exception as e:
        print(f"Error reading Staffing sheet: {e}")
        return

    roles = []
    name_to_id = {}
    
    for _, row in df_staff.iterrows():
        # Adjust for potential header issues
        # Markdown showed headers on row 3 (index 2)?
        # Let's inspect the first few rows to find the header "Role"
        pass 
    
    # Reload with correct header if needed
    # The read_excel default header=0 (first row).
    # If the file has title rows, we might need to skip.
    # Let's read headerless first to find the header row.
    df_raw = pd.read_excel(xls, sheet_name='Staffing', header=None)
    header_row_idx = 0
    for i, row in df_raw.iterrows():
        if str(row[0]).strip().lower() == 'role':
            header_row_idx = i
            break
            
    df_staff = pd.read_excel(xls, sheet_name='Staffing', header=header_row_idx)
    
    for _, row in df_staff.iterrows():
        role_title = str(row.iloc[0]).strip()
        names_str = str(row.iloc[1]).strip()
        
        if role_title.lower() == 'total' or role_title == 'nan':
            continue
            
        people = re.split(r'[,&]|\n', names_str)
        
        for person in people:
            person = person.strip()
            if not person or 'helpers' in person.lower() or person == 'nan':
                continue
                
            clean_name = re.sub(r'^Dr\.?\s+', '', person)
            
            if "Pauline" in clean_name:
                short_name = "Pauline"
            else:
                short_name = clean_name.split(' ')[0]
            
            user_id = slugify(short_name)
            
            # Ensure unique ID
            base_id = user_id
            counter = 1
            while user_id in [r['id'] for r in roles]:
                user_id = f"{base_id}{counter}"
                counter += 1
                
            roles.append({
                "id": user_id,
                "name": clean_name,
                "title": role_title
            })
            name_to_id[short_name.lower()] = user_id
            name_to_id[clean_name.lower()] = user_id
    
    with open(os.path.join(DATA_DIR, 'roles.json'), 'w', encoding='utf-8') as f:
        json.dump({"roles": roles}, f, indent=4)
    print(f"Updated roles.json with {len(roles)} roles.")
    
    # --- 2. Process Event Manpower ---
    # Find header row
    df_raw_mp = pd.read_excel(xls, sheet_name='Event Manpower', header=None)
    header_row_idx = 0
    for i, row in df_raw_mp.iterrows():
        if str(row[0]).strip().lower() == 'time block':
            header_row_idx = i
            break
            
    df_manpower = pd.read_excel(xls, sheet_name='Event Manpower', header=header_row_idx)
    
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    
    # Initialize empty tasks for all roles
    task_map = {r['id']: {"tasks": {"event-support": []}} for r in roles}
    
    headers = [str(c).strip() for c in df_manpower.columns]
    
    for idx, row in df_manpower.iterrows():
        time_block = str(row.iloc[0]).strip()
        if time_block == 'nan': time_block = ""
        
        event_name = str(row.iloc[1]).strip()
        if event_name == 'nan': continue
        
        # Cols 2+ are people
        for col_idx in range(2, len(headers)):
            col_name = headers[col_idx]
            cell_val = str(row.iloc[col_idx]).strip()
            
            if not cell_val or cell_val.lower() == 'nan':
                continue
            
            # Identify person
            target_id = None
            if slugify(col_name) in [r['id'] for r in roles]:
                target_id = slugify(col_name)
            else:
                for name_key, uid in name_to_id.items():
                    if name_key in col_name.lower():
                        target_id = uid
                        break
            
            if target_id and target_id in task_map:
                task_map[target_id]["tasks"]["event-support"].append({
                    "id": f"task-{idx}-{col_idx}",
                    "time": time_block,
                    "text": cell_val,
                    "tag": event_name
                })
    
    for uid, data in task_map.items():
        filepath = os.path.join(TASKS_DIR, f"{uid}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    print(f"Updated {len(task_map)} task files.")

def process_resources(xls):
    print("Processing Resources...")
    
    # Find header for Box & Materials
    # It seems row 3 (index 2) is header
    df_box = pd.read_excel(xls, sheet_name='Box & Materials', header=2)
    
    boxes = []
    box_map = {}
    items = []
    categories = set()
    unique_zones = set()
    
    # Columns based on markdown extraction earlier:
    # 0: Location, 1: Item, 2: Count, 3: Unit, 4: Package ID, 5: Content Type, 6: Zone, 7: Remarks
    # 12: Package ID.1, 13: Zone.1, 14: Box Contents, 15: Person
    
    # Process Boxes (Right side)
    for _, row in df_box.iterrows():
        pkg_id = str(row.iloc[12]).strip()
        if pkg_id and pkg_id != 'nan':
            zone_name = str(row.iloc[13]).strip()
            box_content = str(row.iloc[14]).strip()
            
            if zone_name == 'nan': zone_name = 'Unassigned'
            
            box_id = f"box-{slugify(pkg_id)}"
            zone_id = slugify(zone_name)
            
            boxes.append({
                "boxid": box_id,
                "name": f"{box_content} ({pkg_id.replace('.0','')})",
                "zoneid": zone_id,
                "order": len(boxes) + 1
            })
            
            clean_pkg_id = pkg_id.replace('.0', '')
            box_map[clean_pkg_id] = box_id
            box_map[pkg_id] = box_id
            
            unique_zones.add(zone_name)
            
    # Save boxes
    pd.DataFrame(boxes).to_csv(os.path.join(DATA_DIR, 'boxes.csv'), index=False)
    
    # Save zones
    zones = [{"zoneid": slugify(z), "name": z, "description": "", "order": i} 
             for i, z in enumerate(unique_zones)]
    pd.DataFrame(zones).to_csv(os.path.join(DATA_DIR, 'zones.csv'), index=False)
    
    # Process Items (Left side)
    for _, row in df_box.iterrows():
        item_name = str(row.iloc[1]).strip()
        if not item_name or item_name == 'nan': continue
        
        count = row.iloc[2]
        try:
            count = int(float(count))
        except:
            count = 1
            
        pkg_ref = str(row.iloc[4]).strip().replace('.0', '')
        content_type = str(row.iloc[5]).strip()
        remarks = str(row.iloc[7]).strip()
        
        if content_type == 'nan': content_type = 'General'
        category_id = slugify(content_type)
        categories.add((category_id, content_type))
        
        box_id = box_map.get(pkg_ref, 'unassigned')
        
        items.append({
            "itemid": slugify(item_name)[:30] + '-' + str(len(items)),
            "name": item_name,
            "totalquantity": count,
            "remainingquantity": 0,
            "notes": remarks if remarks != 'nan' else "",
            "categoryid": category_id,
            "boxid": box_id,
            "quantityinbox": count
        })
        
    pd.DataFrame(items).to_csv(os.path.join(DATA_DIR, 'items.csv'), index=False)
    
    cats_list = [{"categoryid": c[0], "name": c[1], "order": i} for i, c in enumerate(categories)]
    pd.DataFrame(cats_list).to_csv(os.path.join(DATA_DIR, 'categories.csv'), index=False)
    
    print(f"Updated Resources.")

def process_programme(xls):
    print("Processing Programme Briefs...")
    
    # Find header
    df_raw = pd.read_excel(xls, sheet_name='00 - Programme Briefs', header=None)
    header_row_idx = 0
    for i, row in df_raw.iterrows():
        if str(row[3]).strip() == 'Time': # Check Col D
            header_row_idx = i
            break
            
    df = pd.read_excel(xls, sheet_name='00 - Programme Briefs', header=header_row_idx)
    
    # Info is in top-left, which might be above header_row_idx
    # Let's read raw again for Info
    info = {}
    for i in range(header_row_idx):
        row = df_raw.iloc[i]
        key = str(row[0]).strip()
        val = str(row[1]).strip()
        if key and key != 'nan':
            info[key] = val
            
    schedule_rows = []
    # Columns relative to header row: Time (3), Activity (4) -> indices in df (if header was set correctly)
    # Check columns
    time_col = df.columns[3] # Should be 'Time'
    act_col = df.columns[4] # Should be 'Activity'
    
    for _, row in df.iterrows():
        time_val = str(row.iloc[3]).strip()
        act_val = str(row.iloc[4]).strip()
        
        if time_val and time_val != 'nan' and act_val and act_val != 'nan':
            if any(char.isdigit() for char in time_val):
                schedule_rows.append({"time": time_val, "activity": act_val})
                
    update_overview(info)
    update_schedule(schedule_rows)

def update_overview(info):
    # Simple replace for now as we don't assume bs4 is installed on user machine unless we verify
    # But wait, I can use regex or simple string find/replace if structure is known
    # Or just write the whole file if I had a template.
    # I'll use regex to replace content inside specific tags.
    
    path = os.path.join(PAGES_DIR, 'overview.html')
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replacements map
    # Location
    loc_val = info.get('Location', '')
    if loc_val:
        # Regex to find Location span
        # <strong><i class="..."></i> Location</strong>\n<span>...</span>
        content = re.sub(
            r'(<strong>.*?Location</strong>\s*<span>)(.*?)(</span>)', 
            f'\\1{loc_val}\\3', 
            content, 
            flags=re.DOTALL
        )
        
    # Date
    date_val = info.get('Date & Time', '')
    if date_val:
        content = re.sub(
            r'(<strong>.*?Date</strong>\s*<span>)(.*?)(</span>)',
            f'\\1{date_val}\\3',
            content,
            flags=re.DOTALL
        )
        # Also page header date
        content = re.sub(
            r'(<div class="date-info">.*?</i>)(.*?)(</div>)',
            f'\\1 {date_val}\\3',
            content
        )
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_schedule(rows):
    path = os.path.join(PAGES_DIR, 'schedule.html')
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Construct new tbody rows
    new_rows = []
    for row in rows:
        icon = "fas fa-circle"
        act = row['activity'].lower()
        if 'registration' in act: icon = "fas fa-clipboard-check"
        elif 'lunch' in act: icon = "fas fa-utensils"
        elif 'break' in act: icon = "fas fa-coffee"
        
        html_row = f"""                    <tr>
                        <td>{row['time']}</td>
                        <td><i class="{icon}"></i> {row['activity']}</td>
                        <td></td>
                    </tr>"""
        new_rows.append(html_row)
        
    tbody_content = "\n".join(new_rows)
    
    # Regex replace tbody
    content = re.sub(
        r'(<tbody>)(.*?)(</tbody>)', 
        f'\\1\n{tbody_content}\n\\3', 
        content, 
        flags=re.DOTALL
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    try:
        xls = load_excel()
        process_staffing_and_tasks(xls)
        process_resources(xls)
        process_programme(xls)
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
