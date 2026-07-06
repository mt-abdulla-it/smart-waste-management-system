let map;
let markers = {};
let trendChart;

const socket = io();

socket.on('bin_update', (data) => {
    // When a bin updates, refresh dashboard to show new status
    if (window.location.pathname.includes('dashboard') || window.location.pathname === '/') {
        loadDashboard();
    }
});

function initMap() {
    map = L.map('city-map').setView([6.9271, 79.8612], 13);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

function initCharts() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Avg Fill Level %',
                data: [45, 52, 68, 40, 60, 85, 50],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.1)' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

async function downloadReport() {
    try {
        const btn = document.querySelector('button[onclick="downloadReport()"]');
        const oldText = btn.innerText;
        btn.innerText = "⏳ Generating...";
        
        const response = await fetch('/api/report');
        const data = await response.json();
        
        if (data.report_url) {
            window.open(data.report_url, '_blank');
        }
        btn.innerText = oldText;
    } catch(err) {
        console.error("Failed to generate report", err);
        alert("Failed to generate report");
    }
}

// Fetch dashboard data
async function loadDashboard() {
    loadBudget();
    try {
        const response = await fetch('/api/bins');
        const bins = await response.json();
        
        const container = document.getElementById('bins-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        bins.forEach(bin => {
            let statusClass = 'status-safe';
            let statusText = 'Safe';
            let bgColorClass = 'var(--accent-color)';
            let isEmergency = false;
            
            if (bin.fill_level >= 95) {
                statusClass = 'status-danger';
                statusText = '🚨 CRITICAL EMERGENCY';
                bgColorClass = 'var(--danger-color)';
                isEmergency = true;
            } else if (bin.fill_level >= 80) {
                statusClass = 'status-danger';
                statusText = 'Critical';
                bgColorClass = 'var(--danger-color)';
            } else if (bin.fill_level >= 50) {
                statusClass = 'status-warning';
                statusText = 'Warning';
                bgColorClass = '#f59e0b';
            }
            
            // Map Marker logic
            if (map) {
                let color = bin.fill_level >= 80 ? 'red' : (bin.fill_level >= 50 ? 'orange' : 'green');
                if (!markers[bin.id]) {
                    markers[bin.id] = L.circleMarker([bin.latitude, bin.longitude], {
                        color: color, fillColor: color, fillOpacity: 0.5, radius: 8
                    }).addTo(map);
                } else {
                    markers[bin.id].setStyle({color: color, fillColor: color});
                }
                markers[bin.id].bindPopup(`<b>${bin.location_name}</b><br>Fill Level: ${bin.fill_level}%<br>Predict: ${bin.time_to_full}h to full`);
            }
            
            const card = document.createElement('div');
            card.className = `glass-panel card ${isEmergency ? 'pulse-danger' : ''}`;
            if (isEmergency) {
                card.style.border = '2px solid var(--danger-color)';
                card.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.4)';
            }
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 class="card-title" style="margin-bottom: 0;">${bin.location_name}</h3>
                    <span style="font-size: 0.8rem; color: ${isEmergency ? 'var(--danger-color)' : 'var(--text-muted)'}; display: flex; align-items: center; font-weight: ${isEmergency ? 'bold' : 'normal'}">
                        <span class="status-indicator ${statusClass}"></span>
                        ${statusText}
                    </span>
                </div>
                
                <div style="margin-top: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem;">
                        <span>Fill Level</span>
                        <span style="font-weight: 600;">${bin.fill_level}%</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: ${bin.fill_level}%; background-color: ${bgColorClass}; box-shadow: 0 0 10px ${bgColorClass};"></div>
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-muted);">
                        🧠 AI Predict: Full in <b style="color: white;">${bin.time_to_full} hrs</b>
                    </div>
                </div>
                <div style="margin-top: 1rem; text-align: right;">
                    <button class="btn btn-primary" style="padding: 0.4rem 1rem; font-size: 0.8rem; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);" 
                            onclick="simulateFill(${bin.id}, ${bin.fill_level})"
                            onmouseover="this.style.background='var(--primary-color)'"
                            onmouseout="this.style.background='rgba(255,255,255,0.1)'">
                        Add Waste
                    </button>
                    ${bin.fill_level >= 80 ? `<button class="btn btn-primary" style="padding: 0.4rem 1rem; font-size: 0.8rem; margin-left: 0.5rem; background: var(--accent-color);" onclick="simulateEmpty(${bin.id})">Empty</button>` : ''}
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load bins", err);
    }
}

async function simulateFill(binId, currentLevel) {
    const newLevel = Math.min(currentLevel + Math.floor(Math.random() * 25) + 10, 100);
    updateBin(binId, newLevel);
}

async function simulateEmpty(binId) {
    updateBin(binId, 0);
}

async function updateBin(binId, level) {
    try {
        await fetch('/api/update_bin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: binId, fill_level: level })
        });
        // UI refreshes automatically via SocketIO event
    } catch (err) {
        console.error("Failed to update bin", err);
    }
}

async function loadBudget() {
    try {
        const response = await fetch('/api/budget');
        const data = await response.json();
        
        const formatLKR = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'LKR' }).format(val);
        
        const limitEl = document.getElementById('budget-limit');
        const fuelEl = document.getElementById('fuel-cost');
        const driverEl = document.getElementById('driver-cost');
        const remEl = document.getElementById('budget-remaining');
        
        if(limitEl) limitEl.innerText = formatLKR(data.limit);
        if(fuelEl) fuelEl.innerText = formatLKR(data.total_fuel);
        if(driverEl) driverEl.innerText = formatLKR(data.total_driver);
        
        if(remEl) {
            remEl.innerText = formatLKR(data.remaining);
            if (data.remaining < 0) {
                remEl.style.color = "var(--danger-color)";
            }
        }
    } catch(err) {
        console.error("Failed to load budget", err);
    }
}

async function calculateRoute() {
    const resultsDiv = document.getElementById('route-results');
    const pathList = document.getElementById('path-list');
    const costMetrics = document.getElementById('cost-metrics');
    
    pathList.innerHTML = '<li style="padding: 1rem; text-align: center;">Running optimization algorithm...</li>';
    if(costMetrics) costMetrics.innerHTML = '';
    resultsDiv.style.display = 'block';
    
    try {
        const response = await fetch('/api/optimize');
        const data = await response.json();
        
        pathList.innerHTML = '';
        if (data.route.length <= 1 || data.route[0] === "No full bins to collect") {
            pathList.innerHTML = '<li class="glass-panel" style="padding: 1rem; border-radius: 8px;">✅ All bins are below the critical threshold. No collection needed.</li>';
            if(costMetrics) costMetrics.style.display = 'none';
            return;
        }
        
        if(costMetrics && data.costs) {
            costMetrics.style.display = 'block';
            let effColor = data.costs.efficiency === 'High' ? 'var(--accent-color)' : (data.costs.efficiency === 'Medium' ? '#f59e0b' : 'var(--danger-color)');
            costMetrics.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.2rem;">Total Distance</p>
                        <h3 style="font-size: 1.2rem;">${data.costs.distance_km} km</h3>
                    </div>
                    <div>
                        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.2rem;">Vehicle</p>
                        <h3 style="font-size: 1.2rem;">${data.costs.vehicle_type || 'Standard'}</h3>
                    </div>
                    <div>
                        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.2rem;">Fuel Used</p>
                        <h3 style="font-size: 1.2rem;">${data.costs.fuel_used} L</h3>
                    </div>
                    <div>
                        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.2rem;">Route Cost</p>
                        <h3 style="font-size: 1.2rem; color: #3b82f6;">${data.costs.total_cost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} LKR</h3>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: ${effColor}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
                            Efficiency: ${data.costs.efficiency}
                        </span>
                    </div>
                </div>
            `;
        }
        
        data.route.forEach((node, index) => {
            const li = document.createElement('li');
            li.className = 'glass-panel';
            li.style = 'padding: 1rem; margin-bottom: 0.8rem; border-radius: 8px; display: flex; align-items: center; transition: transform 0.2s; cursor: pointer;';
            li.onmouseover = () => li.style.transform = 'translateX(10px)';
            li.onmouseout = () => li.style.transform = 'translateX(0)';
            
            li.innerHTML = `
                <span style="background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); color: white; width: 28px; height: 28px; display: inline-flex; justify-content: center; align-items: center; border-radius: 50%; margin-right: 1rem; font-weight: bold; font-size: 0.9rem; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4);">
                    ${index + 1}
                </span>
                <span style="font-weight: 500; font-size: 1.1rem;">${node}</span>
            `;
            pathList.appendChild(li);
        });
        
    } catch (err) {
        console.error("Failed to calculate route", err);
        pathList.innerHTML = '<li class="glass-panel" style="padding: 1rem; border-radius: 8px; color: var(--danger-color); border-left: 4px solid var(--danger-color);">Failed to generate route. Server error.</li>';
    }
}

// Ensure nav links get active state appropriately
document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
