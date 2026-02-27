# Free Play Case Conference Dashboard

## Overview
This dashboard is designed for the KeySteps@JC (Phase Two) Free Play Case Conference. It serves as a central coordination platform for all team members involved in organizing and running the conference.

## Features

### 1. Role-Based Access
- **Personalized Views**: Select your role to see relevant information and tasks
- **Team Coordination**: Each team member can access their specific responsibilities
- **Dynamic Content**: Interface adapts based on user role

### 2. Key Sections
- **Overview**: Conference details, key objectives, and general information
- **Schedule**: Detailed timeline of the conference day with all sessions and activities
- **Activity Playbook**: Complete guide for Activity 1 and Activity 2 including:
  - Step-by-step instructions
  - Participant and facilitator actions
  - Materials and resources checklists
  - CPS (Child Playfulness Signals) framework guidance
- **Tasks**: Role-specific responsibilities and assignments for all team members
- **Resources**: Inventory management with zones, boxes, and item tracking
- **Logistics**: Venue details, transportation info, and contact information

### 3. Conference Information
- **Event**: Free Play Case Conference
- **Project**: KeySteps@JC (Phase Two)
- **Date**: January 4, 2025 (Saturday)
- **Venue**: Inno Centre, 72 Tat Chee Avenue, Kowloon Tong, Kowloon
- **Target Group**: Teachers from five districts (Tuen Mun, Yuen Long, Kowloon City, Sha Tin, Sham Shui Po)

## Quick Start
1. Open `index.html` in your web browser, or
2. Use a local server to serve the dashboard:
   ```bash
   python -m http.server 8000
   ```
3. Navigate to `http://localhost:8000` in your browser
4. Select your role from the dropdown menu
5. Navigate through different sections using the dashboard cards

## Key Activities

### Activity 1: Solving Persistent Implementation Barriers
- **Duration**: 40 minutes
- **Objective**: Help teachers identify and solve real difficulties in sustaining Free Play practice
- **Method**: Group-based challenge exchange using CPS analytical lens
- **Materials**: Flip charts, challenge slips, CPS prompt sheets

### Activity 2: Our Playful Community - Resource Mapping
- **Duration**: 40 minutes
- **Objective**: Identify and evaluate local community resources for quality play
- **Platform**: Padlet collaborative mapping
- **Output**: District-based community play resource map

## Repository
Access the source code at: https://github.com/herman925/KSFreePlayConference

## Contact Information
- **Activities Lead**: Pauline (9122 2847)
- **Coordination**: May (6206 4525), Herman (9727 8202), Archie (Venue Liaison: yjunle@eduhk.hk)
- **Support**: All other staff members

## Technical Details
- Built with HTML, CSS, and vanilla JavaScript
- Data stored in CSV and JSON files
- Responsive design for desktop and mobile viewing
- GitHub Pages compatible for easy deployment

## File Structure
```
KSFreePlayConference/
├── index.html              # Main dashboard
├── pages/                  # Individual section pages
│   ├── activity_details.html  # Activity Playbook
│   ├── schedule.html       # Conference schedule
│   ├── tasks.html          # Role-based tasks
│   ├── resources.html      # Inventory management
│   ├── logistics.html      # Venue and contact info
│   └── overview.html       # General information
├── data/                   # Data files
│   ├── items.csv          # Inventory items
│   ├── boxes.csv          # Box organization
│   ├── zones.csv          # Location zones
│   ├── categories.csv     # Item categories
│   ├── roles.json         # Staff roles
│   └── tasks/             # Individual task files
├── scripts/               # JavaScript files
├── styles/                # CSS files
└── README.md             # This file
```

## Support
If you encounter any issues, please contact the coordination team.
