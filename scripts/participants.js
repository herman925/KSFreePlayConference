let currentData = [];
let currentExportSection = '';
let currentExportButton = null;

function showExportMenu(section, button) {
    const exportMenu = document.getElementById('exportMenu');
    const rect = button.getBoundingClientRect();
    
    hideExportMenu();
    
    currentExportSection = section;
    currentExportButton = button;
    
    const shuttleExportOption = document.getElementById('shuttleExportOption');
    if(shuttleExportOption) {
        shuttleExportOption.style.display = section === 'transport' ? 'flex' : 'none';
    }
    
    exportMenu.style.top = `${rect.bottom + window.scrollY + 5}px`;
    exportMenu.style.left = `${rect.left}px`;
    exportMenu.classList.add('active');
    
    document.addEventListener('click', handleExportMenuClick);
}

function hideExportMenu() {
    const exportMenu = document.getElementById('exportMenu');
    if(exportMenu) {
        exportMenu.classList.remove('active');
        document.removeEventListener('click', handleExportMenuClick);
    }
}

function handleExportMenuClick(e) {
    const exportMenu = document.getElementById('exportMenu');
    if (!exportMenu.contains(e.target) && e.target !== currentExportButton) {
        hideExportMenu();
    }
}

function exportData(format) {
    hideExportMenu();
    
    let data = [];
    let filename = '';
    
    switch (currentExportSection) {
        case 'registration':
            data = currentData.map(p => {
                return {
                    'Registration Time': p['Timestamp'] || '',
                    'Name': p['參加者中文全名'] || '',
                    'School': p['參加者所屬學校'] || '',
                    'Phone': p['參加者手提電話'] || '',
                    'Pick-up Point': p['去程集合點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || '',
                    'Drop-off Point': p['回程解散點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || ''
                };
            });
            filename = 'registration_list';
            break;
            
        case 'transport':
            const transportData = {pickup: {}, dropoff: {}};
            currentData.forEach(p => {
                const pickup = p['去程集合點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || 'Not Specified';
                const dropoff = p['回程解散點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || 'Not Specified';
                const name = p['參加者中文全名'] || 'Unknown';
                
                if (pickup && pickup !== 'nan') {
                    if (!transportData.pickup[pickup]) transportData.pickup[pickup] = [];
                    transportData.pickup[pickup].push(name);
                }
                
                if (dropoff && dropoff !== 'nan') {
                    if (!transportData.dropoff[dropoff]) transportData.dropoff[dropoff] = [];
                    transportData.dropoff[dropoff].push(name);
                }
            });
            
            data = [
                ...Object.entries(transportData.pickup).map(([location, names]) => ({
                    'Type': 'Pick-up',
                    'Location': location,
                    'Count': names.length,
                    'Participants': names.join(', ')
                })),
                ...Object.entries(transportData.dropoff).map(([location, names]) => ({
                    'Type': 'Drop-off',
                    'Location': location,
                    'Count': names.length,
                    'Participants': names.join(', ')
                }))
            ];
            filename = 'transport_summary';
            break;
    }
    
    if (format === 'xlsx') {
        exportToExcel(data, filename);
    } else {
        exportToCSV(data, filename);
    }
}

function exportToExcel(data, filename) {
    try {
        const ws = XLSX.utils.json_to_sheet(data, {
            skipHeader: false,
            origin: 'A1'
        });

        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Data');

        XLSX.writeFile(wb, `${filename}_${getFormattedDate()}.xlsx`);
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        alert('Failed to export Excel file. Please try again.');
    }
}

function exportToCSV(data, filename) {
    try {
        if (data.length === 0) {
            alert('No data to export');
            return;
        }

        const headers = Object.keys(data[0]);
        const bom = '\uFEFF';
        
        const csvContent = bom + headers.join(',') + '\n' + 
            data.map(row => 
                headers.map(field => {
                    let value = row[field] || '';
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                        value = '"' + value.replace(/"/g, '""') + '"';
                    }
                    return value;
                }).join(',')
            ).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `${filename}_${getFormattedDate()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting to CSV:', error);
        alert('Failed to export CSV file. Please try again.');
    }
}

function getFormattedDate() {
    const date = new Date();
    return date.toISOString().split('T')[0];
}

document.addEventListener('DOMContentLoaded', function() {
    loadRoles();
    loadParticipantData();
});

async function loadRoles() {
    const roleSelect = document.getElementById('roleSelect');
    if(!roleSelect) return;
    try {
        const response = await fetch('../data/roles.json?v=' + new Date().getTime());
        const data = await response.json();
        
        roleSelect.innerHTML = '<option value="">Select Your Role</option>';
        
        data.roles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.id;
            option.textContent = `${role.name}${role.title ? ` (${role.title})` : ''}`;
            roleSelect.appendChild(option);
        });
        
        const savedRole = localStorage.getItem('selectedRole');
        if (savedRole) {
            roleSelect.value = savedRole;
        }
    } catch (error) {
        console.error('Error loading roles:', error);
    }

    roleSelect.addEventListener('change', function() {
        const selectedRole = this.value;
        localStorage.setItem('selectedRole', selectedRole);
    });
}

async function loadParticipantData() {
    try {
        const response = await fetch('https://docs.google.com/spreadsheets/d/e/2PACX-1vQuYD89J0S3rimF3W1IMwsDzeC-9x0tL_4qu3NR8hz1T0xSAptXXTX-Y1WKOoV-LPy7yg8Y4HOW5sf3/pub?gid=1932839246&single=true&output=csv', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            cache: 'no-store'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const csvText = await response.text();
        currentData = parseCSV(csvText);
        
        renderParticipantTable(currentData);
        updateStatistics(currentData);
        renderTransportSummary(currentData);
        
    } catch (error) {
        console.error('Error loading participant data:', error);
        showNotification('Failed to load participant data', 'error');
    }
}

function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        if (values.length === headers.length) {
            const row = {};
            headers.forEach((header, index) => {
                row[header.trim()] = values[index].trim();
            });
            data.push(row);
        }
    }

    return data;
}

function renderParticipantTable(data) {
    const tbody = document.getElementById('participantTableBody');
    if(!tbody) return;
    tbody.innerHTML = '';

    data.forEach(participant => {
        const tr = document.createElement('tr');
        const time = participant['Timestamp'] || '';
        const name = participant['參加者中文全名'] || '';
        const school = participant['參加者所屬學校'] || '';
        const phone = participant['參加者手提電話'] || '';
        const pickup = participant['去程集合點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || '';
        const dropoff = participant['回程解散點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || '';
        
        tr.innerHTML = `
            <td>${time}</td>
            <td>${name}</td>
            <td>${school}</td>
            <td>${phone}</td>
            <td>${pickup}</td>
            <td>${dropoff}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderTransportSummary(data) {
    const pickupPoints = {};
    const dropoffPoints = {};
    const pickupParticipants = {};
    const dropoffParticipants = {};

    data.forEach(participant => {
        const pickup = participant['去程集合點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || 'Not Specified';
        const dropoff = participant['回程解散點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || 'Not Specified';
        const name = participant['參加者中文全名'] || 'Unknown';
        
        if (pickup && pickup !== 'nan') {
            pickupPoints[pickup] = (pickupPoints[pickup] || 0) + 1;
            if (!pickupParticipants[pickup]) {
                pickupParticipants[pickup] = [];
            }
            pickupParticipants[pickup].push(name);
        }

        if (dropoff && dropoff !== 'nan') {
            dropoffPoints[dropoff] = (dropoffPoints[dropoff] || 0) + 1;
            if (!dropoffParticipants[dropoff]) {
                dropoffParticipants[dropoff] = [];
            }
            dropoffParticipants[dropoff].push(name);
        }
    });

    renderTransportList('pickupList', pickupPoints, pickupParticipants, 'Pick-up');
    renderTransportList('dropoffList', dropoffPoints, dropoffParticipants, 'Drop-off');
}

function renderTransportList(elementId, points, participants, type) {
    const list = document.getElementById(elementId);
    if(!list) return;
    list.innerHTML = '';

    Object.entries(points)
        .sort((a, b) => b[1] - a[1])
        .forEach(([location, count]) => {
            const li = document.createElement('li');
            li.onclick = () => showPopup(`${type} Point: ${location}`, participants[location]);
            li.innerHTML = `
                <span class="transport-location">${location}</span>
                <span class="transport-count">${count}</span>
            `;
            list.appendChild(li);
        });
}

function showPopup(title, names) {
    const popupOverlay = document.getElementById('popupOverlay');
    const popupTitle = document.getElementById('popupTitle');
    const popupList = document.getElementById('popupList');
    if(!popupOverlay) return;

    popupTitle.textContent = title;
    popupList.innerHTML = names.map(name => `<li class="name-tag">${name}</li>`).join('');
    
    popupOverlay.classList.add('active');
}

function closePopup() {
    const popupOverlay = document.getElementById('popupOverlay');
    if(popupOverlay) popupOverlay.classList.remove('active');
}

// Close popup when clicking outside
document.addEventListener('click', (e) => {
    const popupOverlay = document.getElementById('popupOverlay');
    if (popupOverlay && e.target === popupOverlay) {
        closePopup();
    }
});

// Close popup with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closePopup();
    }
});

function exportShuttleAttendance() {
    hideExportMenu();
    
    try {
        const pickupLocations = {};
        
        currentData.forEach(p => {
            const pickup = p['去程集合點 (箭咀位置附近停車。實際停車位置視乎路況。)'] || 'Not Specified';
            if (!pickupLocations[pickup]) {
                pickupLocations[pickup] = [];
            }
            pickupLocations[pickup].push({
                name: p['參加者中文全名'] || '',
                school: p['參加者所屬學校'] || '',
                contact: p['參加者手提電話'] || ''
            });
        });

        const wb = XLSX.utils.book_new();
        
        Object.entries(pickupLocations).forEach(([location, participants]) => {
            const wsData = [
                ['Shuttle Bus Attendance Sheet'],
                [`Pick-up Point: ${location}`],
                [''],
                ['Name', 'School', 'Contact', 'Signature']
            ];
            
            participants.forEach(p => {
                wsData.push([p.name, p.school, p.contact, '']);
            });
            
            const ws = XLSX.utils.aoa_to_sheet(wsData);
            
            ws['!cols'] = [
                { wch: 25 }, // Name
                { wch: 35 }, // School
                { wch: 15 }, // Contact
                { wch: 20 }  // Signature
            ];
            
            const safeLocation = location
                .replace(/[\\\/\[\]\:\*\?]/g, ' ') 
                .replace(/\s+/g, ' ')              
                .trim()                            
                .substring(0, 31);                 
            
            XLSX.utils.book_append_sheet(wb, ws, safeLocation || 'Unspecified');
        });
        
        XLSX.writeFile(wb, `shuttle_attendance_${getFormattedDate()}.xlsx`);
        showPopup('Export Successful', ['Shuttle attendance sheets have been exported.']);
        
    } catch (error) {
        console.error('Error exporting shuttle attendance:', error);
        showPopup('Export Failed', ['Failed to export shuttle attendance sheets.', 'Please try again.']);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function updateStatistics(data) {
    // Update total registrations
    const totalRegistrations = data.length;
    const totalRegistrationsEl = document.getElementById('totalRegistrations');
    if(totalRegistrationsEl) totalRegistrationsEl.textContent = totalRegistrations;

    // Filter logic
    const teachersData = [];
    const hubData = [];
    
    data.forEach(participant => {
        const school = participant['參加者所屬學校'] || '';
        const isHub = school.includes('賽馬會童亮館') || school.includes('童亮館');
        
        if (isHub) {
            hubData.push(participant);
        } else {
            teachersData.push(participant);
        }
    });

    const totalTeachersEl = document.getElementById('totalTeachers');
    if(totalTeachersEl) totalTeachersEl.textContent = teachersData.length;
    
    const totalHubStaffEl = document.getElementById('totalHubStaff');
    if(totalHubStaffEl) totalHubStaffEl.textContent = hubData.length;

    // Calculate breakdowns
    const schoolCounts = {};
    teachersData.forEach(participant => {
        const school = participant['參加者所屬學校'] || 'Unknown';
        schoolCounts[school] = (schoolCounts[school] || 0) + 1;
    });
    
    const hubCounts = {};
    hubData.forEach(participant => {
        const hub = participant['參加者所屬學校'] || 'Unknown';
        hubCounts[hub] = (hubCounts[hub] || 0) + 1;
    });

    // Sort breakdowns
    const sortedSchools = Object.entries(schoolCounts)
        .sort(([schoolA, countA], [schoolB, countB]) => countB - countA);
        
    const sortedHubs = Object.entries(hubCounts)
        .sort(([hubA, countA], [hubB, countB]) => countB - countA);

    // Update school breakdown table
    const schoolTbody = document.getElementById('schoolBreakdownBody');
    if(schoolTbody) {
        schoolTbody.innerHTML = '';
        sortedSchools.forEach(([school, count]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${school}</td>
                <td>${count}</td>
            `;
            schoolTbody.appendChild(tr);
        });
    }
    
    // Update hub breakdown table
    const hubTbody = document.getElementById('hubBreakdownBody');
    if(hubTbody) {
        hubTbody.innerHTML = '';
        sortedHubs.forEach(([hub, count]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${hub}</td>
                <td>${count}</td>
            `;
            hubTbody.appendChild(tr);
        });
    }
}
