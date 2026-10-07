async function updateDashboard() {
    try {
        // 1. Fetch Status
        let statusRes = await fetch('/api/status');
        let statusData = await statusRes.json();
        document.getElementById('cam-status').innerText = statusData.camera_status;
        document.getElementById('face-count').innerText = statusData.face_count;
        document.getElementById('head-dir').innerText = statusData.head_direction;
        document.getElementById('sys-status').innerText = statusData.system_status;

        // 2. Fetch Events
        let eventsRes = await fetch('/api/events');
        let eventsData = await eventsRes.json();
        let tbody = document.getElementById('events-table-body');
        
        if (eventsData.events.length > 0) {
            tbody.innerHTML = eventsData.events.map(ev => `
                <tr>
                    <td>${ev.timestamp || 'N/A'}</td>
                    <td>${ev.anomaly_type || 'N/A'}</td>
                    <td>${ev.details || 'N/A'}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = `<tr><td colspan="3">No anomalies logged yet.</td></tr>`;
        }

        // 3. Fetch Screenshots
        let screenRes = await fetch('/api/screenshots');
        let screenData = await screenRes.json();
        let gallery = document.getElementById('screenshot-gallery');

        if (screenData.screenshots.length > 0) {
            gallery.innerHTML = screenData.screenshots.map(filename => `
                <img src="/screenshots/${encodeURIComponent(filename)}" alt="${filename}">
            `).join('');
        } else {
            gallery.innerHTML = `<p>No screenshots captured yet.</p>`;
        }

    } catch (err) {
        console.error("Fetch error:", err);
    }
}

// Run every 2 seconds smoothly without reloading the page
setInterval(updateDashboard, 2000);
updateDashboard();