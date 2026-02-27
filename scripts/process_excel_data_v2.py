import pandas as pd
import json
import os
import re

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
        df_raw = pd.read_excel(xls, sheet_name='Staffing', header=None)
        header_row_idx = 0
        for i, row in df_raw.iterrows():
            if str(row[0]).strip().lower() == 'role':
                header_row_idx = i
                break
                
        df_staff = pd.read_excel(xls, sheet_name='Staffing', header=header_row_idx)
        
        roles = []
        name_to_id = {}
        title_mapping = {}

        for _, row in df_staff.iterrows():
            role_title = str(row.iloc[0]).strip()
            names_str = str(row.iloc[1]).strip()

            if role_title.lower() == 'total' or role_title == 'nan':
                continue
                
            if role_title == 'Porgramme Lead':
                role_title = 'Programme Lead'

            people = re.split(r'[,&]|\\n', names_str)
            for person in people:
                person = person.strip()
                if not person or 'helpers' in person.lower() or person == 'nan':
                    continue

                clean_name = re.sub(r'^Dr\\.?\\s+', '', person)
                if 'Pauline' in clean_name or 'Chan Po Lin' in clean_name:
                    clean_name = 'Pauline'
                short_name = clean_name.split(' ')[0]
                
                title_mapping[short_name] = role_title

        df_manpower = pd.read_excel(xls, sheet_name='Event Manpower')
        manpower_roles = [c for c in df_manpower.columns if c not in ['Time Block', 'Event'] and not str(c).startswith('Unnamed')]

        for person in manpower_roles:
            person = str(person).strip()
            if 'Pauline' in person or 'Chan Po Lin' in person:
                short_name = 'Pauline'
            else:
                short_name = person.split(' ')[0]

            user_id = slugify(short_name)
            title = title_mapping.get(short_name, 'Event Staff')

            if not any(r['id'] == user_id for r in roles):
                roles.append({
                    'id': user_id,
                    'name': short_name,
                    'title': title
                })
            name_to_id[short_name.lower()] = user_id
            name_to_id[person.lower()] = user_id

        with open(os.path.join(DATA_DIR, 'roles.json'), 'w', encoding='utf-8') as f:
            json.dump({"roles": roles}, f, indent=4)
        
        # Update tasks.html with new role IDs
        role_ids = [r['id'] for r in roles]
        update_tasks_page(role_ids)
        
        # Update overview.html Team Structure
        update_overview_team(roles)
        
        # --- 2. Process Event Manpower ---
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
                
    except Exception as e:
        print(f"Error processing staffing and tasks: {e}")

def update_tasks_page(role_ids):
    path = os.path.join(PAGES_DIR, 'tasks.html')
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace the roles array
    new_roles_str = "const roles = " + json.dumps(role_ids) + ";"
    content = re.sub(r'const roles = \[.*?\];', new_roles_str, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated tasks.html roles.")

def update_overview_team(roles):
    path = os.path.join(PAGES_DIR, 'overview.html')
    if not os.path.exists(path): return
    
    # Group roles
    groups = {
        "Project Oversight": [],
        "Core Team": [],
        "Floor Operations": [],
        "Other": []
    }
    
    for role in roles:
        title = role['title'].lower()
        if "oversight" in title or "lead" in title:
            groups["Project Oversight"].append(role)
        elif "core" in title or "coordinator" in title or "facilitator" in title:
            groups["Core Team"].append(role)
        elif "operation" in title:
            groups["Floor Operations"].append(role)
        else:
            groups["Other"].append(role)
            
    # Generate HTML
    html_parts = []
    
    # Oversight
    if groups["Project Oversight"]:
        html_parts.append('<div class="team-member oversight">')
        html_parts.append('<h3><i class="fas fa-crown"></i> Project Oversight & Leads</h3><ul>')
        for r in groups["Project Oversight"]:
            html_parts.append(f'<li><i class="fas fa-user"></i> {r["name"]} ({r["title"]})</li>')
        html_parts.append('</ul></div>')
        
    # Core
    if groups["Core Team"]:
        html_parts.append('<div class="team-member core">')
        html_parts.append('<h3><i class="fas fa-star"></i> Core Team</h3><ul>')
        for r in groups["Core Team"]:
            html_parts.append(f'<li><i class="fas fa-user"></i> {r["name"]} ({r["title"]})</li>')
        html_parts.append('</ul></div>')
        
    # Ops
    if groups["Floor Operations"]:
        html_parts.append('<div class="team-member operations">')
        html_parts.append('<h3><i class="fas fa-walking"></i> Floor Operations</h3><ul>')
        for r in groups["Floor Operations"]:
            html_parts.append(f'<li><i class="fas fa-user"></i> {r["name"]} ({r["title"]})</li>')
        html_parts.append('</ul></div>')
        
    team_html = "\n".join(html_parts)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace content of team-grid
    content = re.sub(
        r'(<div class="team-grid">)(.*?)(</div>\s*</div>)', 
        f'\\1\n{team_html}\n\\3', 
        content, 
        flags=re.DOTALL
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated overview.html Team Structure.")

def process_programme(xls, activities_data=None):
    print("Processing Programme Briefs...")
    try:
        df_raw = pd.read_excel(xls, sheet_name='00 - Programme Briefs', header=None)
        header_row_idx = 0
        for i, row in df_raw.iterrows():
            if str(row[3]).strip() == 'Time': 
                header_row_idx = i
                break
                
        df = pd.read_excel(xls, sheet_name='00 - Programme Briefs', header=header_row_idx)
        
        # Info
        info = {}
        for i in range(header_row_idx):
            row = df_raw.iloc[i]
            key = str(row[0]).strip()
            val = str(row[1]).strip()
            if key and key != 'nan':
                info[key] = val
                
        # Schedule
        schedule_rows = []
        # Transport
        transport_rows = []
        
        for _, row in df.iterrows():
            # Schedule: Time (Col 3), Activity (Col 4)
            time_val = str(row.iloc[3]).strip()
            act_val = str(row.iloc[4]).strip()
            
            if time_val and time_val != 'nan' and act_val and act_val != 'nan':
                if any(char.isdigit() for char in time_val):
                    schedule_rows.append({"time": time_val, "activity": act_val})
            
            # Transport: Station (Col 6), Exit (Col 7), Departure (Col 8)
            try:
                station = str(row.iloc[6]).strip()
                exit_val = str(row.iloc[7]).strip()
                dept_val = str(row.iloc[8]).strip()
                
                if station and station != 'nan' and 'Station' in station:
                     transport_rows.append({
                         "station": station,
                         "exit": exit_val if exit_val != 'nan' else "",
                         "departure": dept_val if dept_val != 'nan' else ""
                     })
            except:
                pass
                    
        update_overview(info)
        update_schedule(schedule_rows, activities_data)
        if transport_rows:
            update_logistics_transport(transport_rows)
            
        update_interviews_date(info)
            
    except Exception as e:
        print(f"Error processing programme: {e}")
        import traceback
        traceback.print_exc()

def update_overview(info):
    path = os.path.join(PAGES_DIR, 'overview.html')
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    loc_val = info.get('Location', '')
    if loc_val:
        content = re.sub(
            r'(<strong>.*?Location</strong>\s*<span>)(.*?)(</span>)', 
            f'\\1{loc_val}\\3', 
            content, 
            flags=re.DOTALL
        )
        
    date_val = info.get('Date & Time', '')
    if date_val:
        content = re.sub(
            r'(<strong>.*?Date</strong>\s*<span>)(.*?)(</span>)',
            f'\\1{date_val}\\3',
            content, 
            flags=re.DOTALL
        )
        content = re.sub(
            r'(<div class="date-info">.*?</i>)(.*?)(</div>)',
            f'\\1 {date_val}\\3',
            content
        )
        
    # Update Key Objectives
    new_objectives = """
                <div class="details-grid">
                    <div class="detail-item">
                        <strong><i class="fas fa-layer-group"></i> Consolidate Learning</strong>
                        <span>Consolidate and summarize learning outcomes from the free play comprehensive teaching approach</span>
                    </div>
                    <div class="detail-item">
                        <strong><i class="fas fa-network-wired"></i> Professional Community</strong>
                        <span>Build cross-school and cross-district professional learning communities</span>
                    </div>
                    <div class="detail-item">
                        <strong><i class="fas fa-share-alt"></i> Practical Sharing</strong>
                        <span>Share real-world school case studies and implementation strategies</span>
                    </div>
                    <div class="detail-item">
                        <strong><i class="fas fa-comments"></i> Collaborative Problem Solving</strong>
                        <span>Engage in group activities and thematic discussions to address practical challenges</span>
                    </div>
                </div>
"""
    content = re.sub(
        r'(<h2><i class="fas fa-bullseye"></i> Key Objectives</h2>\s*)<div class="details-grid">.*?</div>\s*(</div>)',
        f'\\1{new_objectives}\\2',
        content,
        flags=re.DOTALL
    )
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_interviews_date(info):
    pass # Interviews page is removed

def update_schedule(rows, activities_data=None):
    path = os.path.join(PAGES_DIR, 'schedule.html')
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove Focused Group header if it exists
    content = re.sub(r'<th><i class="fas fa-users"></i> Focused Group</th>', '', content)
        
    new_rows = []
    for row in rows:
        icon = "fas fa-circle"
        act = row['activity'].lower()
        if 'registration' in act: icon = "fas fa-clipboard-check"
        elif 'lunch' in act: icon = "fas fa-utensils"
        elif 'break' in act: icon = "fas fa-coffee"
        
        # Details
        details_html = ""
        
        if 'school stories: session 1' in act:
            details_html = '''<div class="activity-details" style="margin-top: 8px; padding-left: 24px; font-size: 0.9em; color: #555; border-left: 2px solid #eee;">
                <div class="activity-step" style="margin-bottom: 4px;"><strong>09:40-09:50</strong> - S076新界婦孺福利會元朗幼兒學校</div>
                <div class="activity-step" style="margin-bottom: 4px;"><strong>09:50-10:00</strong> - S086港九街坊婦女會孫方中幼稚園</div>
                <div class="activity-step" style="margin-bottom: 4px;"><strong>10:00-10:10</strong> - S039竹園區神召會南昌康樂幼兒學校</div>
            </div>'''
        elif 'school stories: session 2' in act:
            details_html = '''<div class="activity-details" style="margin-top: 8px; padding-left: 24px; font-size: 0.9em; color: #555; border-left: 2px solid #eee;">
                <div class="activity-step" style="margin-bottom: 4px;"><strong>11:10-11:20</strong> - S017仁濟醫院山景幼稚園/幼兒中心</div>
                <div class="activity-step" style="margin-bottom: 4px;"><strong>11:20-11:30</strong> - S096新界婦孺福利會博康幼兒學校</div>
                <div class="activity-step" style="margin-bottom: 4px;"><strong>11:30-11:40</strong> - S057中華基督教會望覺堂賢貞幼稚園</div>
            </div>'''
        elif activities_data:
            act_key = None
            if 'activity 1' in act: act_key = 'activity-1'
            elif 'activity 2' in act: act_key = 'activity-2'
            
            if act_key and act_key in activities_data:
                steps = activities_data[act_key].get('steps', [])
                if steps:
                    details_html = '<div class="activity-details" style="margin-top: 8px; padding-left: 24px; font-size: 0.9em; color: #555; border-left: 2px solid #eee;">'
                    for step in steps:
                        details_html += f'<div class="activity-step" style="margin-bottom: 4px;"><strong>{step["time"]}</strong> - {step["name"]}</div>'
                    details_html += '</div>'
        
        html_row = f"""                    <tr>
                        <td style="vertical-align: top;">{row['time']}</td>
                        <td>
                            <div class="activity-title"><i class="{icon}"></i> {row['activity']}</div>
                            {details_html}
                        </td>
                    </tr>"""
        new_rows.append(html_row)
        
    tbody_content = "\n".join(new_rows)
    
    content = re.sub(
        r'(<tbody>)(.*?)(</tbody>)', 
        f'\\1\n{tbody_content}\n\\3', 
        content, 
        flags=re.DOTALL
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_logistics_transport(rows):
    path = os.path.join(PAGES_DIR, 'logistics.html')
    if not os.path.exists(path): return
    
    html_parts = []
    for row in rows:
        html_parts.append('<div class="shuttle-route">')
        html_parts.append(f'<h4><i class="fas fa-bus"></i> {row["station"]}</h4>')
        html_parts.append(f'<p><i class="fas fa-clock"></i> Departure: {row["departure"]}</p>')
        html_parts.append(f'<p><i class="fas fa-map-signs"></i> Location: {row["station"]} {row["exit"]}</p>')
        html_parts.append('</div>')
        
    new_content = "\n".join(html_parts)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = re.sub(
        r'(<div class="shuttle-section">)(.*?)(</div>\s*</div>)', 
        f'\\1\n{new_content}\n\\3', 
        content, 
        flags=re.DOTALL
    )
    
    # Also update Venue Contact
    new_contact = """
                    <h4><i class="fas fa-hotel"></i> Venue Contact</h4>
                    <ul>
                        <li><i class="fas fa-user"></i> Steven So</li>
                        <li><i class="fas fa-building"></i> Hong Kong Science and Technology Parks Corporation</li>
                        <li><i class="fas fa-phone"></i> +852 2639 8309</li>
                        <li><i class="fas fa-envelope"></i> steven.so@hkstp.org</li>
                    </ul>
    """
    
    content = re.sub(
        r'<div class="contact-section venue-contact">\s*<h4><i class="fas fa-hotel"></i> Venue Contact</h4>\s*<ul>.*?</ul>\s*</div>',
        f'<div class="contact-section venue-contact">{new_contact}</div>',
        content,
        flags=re.DOTALL
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated logistics.html Transport and Contacts.")

def process_resources_local(xls):
    print("Processing Resources...")
    try:
        # Load without header to capture everything
        df_box = pd.read_excel(xls, sheet_name='Box & Materials', header=None)
        
        boxes = []
        box_map = {}
        items = []
        categories = set()
        unique_zones = set()
        
        # Start reading from row index 1 (skipping header row 0)
        # Right side: Boxes (Cols 12-15)
        # Col 12: Package ID, Col 13: Zone, Col 14: Box Contents, Col 15: Person
        for i in range(1, len(df_box)):
            row = df_box.iloc[i]
            pkg_id = str(row[12]).strip()
            if pkg_id and pkg_id != 'nan' and pkg_id.lower() != 'package id':
                zone_name = str(row[13]).strip()
                box_content = str(row[14]).strip()
                if zone_name == 'nan': zone_name = 'Unassigned'
                
                # Format pkg_id nicely
                clean_pkg_id = pkg_id.replace('.0', '')
                box_id = f"box-{slugify(clean_pkg_id)}"
                zone_id = slugify(zone_name)
                
                boxes.append({
                    "boxid": box_id,
                    "name": f"{box_content} ({clean_pkg_id})",
                    "zoneid": zone_id,
                    "order": len(boxes) + 1
                })
                box_map[clean_pkg_id] = box_id
                box_map[pkg_id] = box_id
                unique_zones.add(zone_name)
                
        pd.DataFrame(boxes).to_csv(os.path.join(DATA_DIR, 'boxes.csv'), index=False)
        zones = [{"zoneid": slugify(z), "name": z, "description": "", "order": i} for i, z in enumerate(unique_zones)]
        pd.DataFrame(zones).to_csv(os.path.join(DATA_DIR, 'zones.csv'), index=False)
        
        # Left side: Items (Cols 0-7)
        # Col 1: Item, Col 2: Count, Col 3: Unit, Col 4: Package ID, Col 5: Content Type, Col 7: Remarks
        for i in range(1, len(df_box)):
            row = df_box.iloc[i]
            item_name = str(row[1]).strip()
            
            if not item_name or item_name == 'nan' or item_name.lower() == 'item': 
                continue
                
            count = row[2]
            try:
                count = int(float(count))
            except:
                count = 1
                
            pkg_ref = str(row[4]).strip().replace('.0', '')
            content_type = str(row[5]).strip()
            remarks = str(row[7]).strip()
            
            if content_type == 'nan' or not content_type: 
                content_type = 'General'
                
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
        
        print("Updated resources.")
    except Exception as e:
        print(f"Error processing resources: {e}")

def process_budget(xls):
    print("Processing Budget...")
    try:
        # Load with header=1 (row 2)
        df = pd.read_excel(xls, sheet_name='Budget', header=1)
        
        budget_items = []
        for _, row in df.iterrows():
            item = str(row.iloc[0]).strip()
            amount = row.iloc[1]
            details = str(row.iloc[2]).strip()
            
            if item and item != 'nan' and 'Total Budget' not in item:
                try:
                    amount_val = float(amount)
                except:
                    amount_val = 0.0
                    
                category = 'other'
                item_lower = item.lower()
                if 'venue' in item_lower: category = 'venue'
                elif 'meal' in item_lower or 'lunch' in item_lower: category = 'refreshments'
                elif 'refreshment' in item_lower: category = 'refreshments'
                elif 'transport' in item_lower: category = 'transportation'
                elif 'material' in item_lower: category = 'materials'
                
                budget_items.append({
                    "date": "2026-03-14",
                    "category": category,
                    "description": item + (f" - {details}" if details and details != 'nan' else ""),
                    "amount": amount_val # Keep positive as Allocation
                })
                
        with open(os.path.join(DATA_DIR, 'budget.json'), 'w', encoding='utf-8') as f:
            json.dump(budget_items, f, indent=4)
        print(f"Updated budget.json with {len(budget_items)} items.")
        
    except Exception as e:
        print(f"Error processing budget: {e}")

def process_activities(xls):
    print("Processing Activity Details...")
    activities = {}
    try:
        df = pd.read_excel(xls, sheet_name='Activity Details', header=2)
        
        activities = {
            "activity-1": {
                "title": "Structured Problem-Solving on Implementation Barriers",
                "steps": []
            },
            "activity-2": {
                "title": "Community Resource Mapping",
                "steps": []
            }
        }
        
        # Activity 1
        for _, row in df.iterrows():
            step_num = str(row.iloc[0]).strip()
            if not step_num or step_num == 'nan': continue
            if not step_num[0].isdigit(): continue
            
            time = str(row.iloc[1]).strip()
            name = str(row.iloc[2]).strip()
            part_act = str(row.iloc[3]).strip()
            fac_act = str(row.iloc[4]).strip()
            mat = str(row.iloc[5]).strip()
            
            activities["activity-1"]["steps"].append({
                "step": step_num,
                "time": time if time != 'nan' else "",
                "name": name if name != 'nan' else "",
                "participant_action": part_act if part_act != 'nan' else "",
                "facilitator_action": fac_act if fac_act != 'nan' else "",
                "materials": mat if mat != 'nan' else ""
            })
            
        # Activity 2
        col_offset = 7
        if len(df.columns) > 12:
            for _, row in df.iterrows():
                step_num = str(row.iloc[col_offset]).strip()
                if not step_num or step_num == 'nan': continue
                if not step_num[0].isdigit(): continue
                
                time = str(row.iloc[col_offset+1]).strip()
                name = str(row.iloc[col_offset+2]).strip()
                part_act = str(row.iloc[col_offset+3]).strip()
                fac_act = str(row.iloc[col_offset+4]).strip()
                mat = str(row.iloc[col_offset+5]).strip()
                
                activities["activity-2"]["steps"].append({
                    "step": step_num,
                    "time": time if time != 'nan' else "",
                    "name": name if name != 'nan' else "",
                    "participant_action": part_act if part_act != 'nan' else "",
                    "facilitator_action": fac_act if fac_act != 'nan' else "",
                    "materials": mat if mat != 'nan' else ""
                })
                
        with open(os.path.join(DATA_DIR, 'activities.json'), 'w', encoding='utf-8') as f:
            json.dump(activities, f, indent=4)
        print("Updated activities.json")
        
    except Exception as e:
        print(f"Error processing activities: {e}")
        
    return activities

def main():
    try:
        xls = load_excel()
        process_staffing_and_tasks(xls)
        process_resources_local(xls)
        process_budget(xls)
        activities = process_activities(xls)
        process_programme(xls, activities)
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
