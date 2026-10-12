const refreshInterval = 2000;

function setConnectionStatus(label, state) {
    const indicator = document.createElement('span');
    indicator.className = 'status-dot';
    indicator.setAttribute('aria-hidden', 'true');

    const status = document.getElementById('connection-status');
    status.className = `connection-status connection-status--${state}`;
    status.replaceChildren(indicator, document.createTextNode(label));
}

function setMetric(id, value, state) {
    const element = document.getElementById(id);
    element.textContent = value;
    element.dataset.state = state;
}

function stateForCamera(value) {
    const status = String(value || '').toUpperCase();
    if (status === 'ONLINE') return 'good';
    if (status === 'STARTING') return 'loading';
    return 'bad';
}

function stateForSystem(value) {
    const status = String(value || '').toUpperCase();
    if (status === 'NORMAL') return 'good';
    if (status.startsWith('ALERT')) return 'warning';
    if (status.startsWith('ERROR') || status === 'OFFLINE') return 'bad';
    return 'loading';
}

function updateFeedStatus(cameraStatus) {
    const value = String(cameraStatus || '').toUpperCase();
    const state = stateForCamera(value);
    const label = state === 'good' ? 'Streaming' : state === 'bad' ? 'Camera offline' : 'Connecting';

    const status = document.getElementById('feed-status');
    status.className = `feed-state feed-state--${state}`;
    document.getElementById('feed-status-label').textContent = label;

    const overlay = document.getElementById('feed-overlay');
    overlay.textContent = state === 'good' ? 'LIVE' : state === 'bad' ? 'OFFLINE' : 'CONNECTING';
    overlay.dataset.state = state;
}

function renderEvents(events) {
    const tbody = document.getElementById('events-table-body');
    tbody.replaceChildren();

    if (events.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 3;
        cell.className = 'empty-state';
        cell.textContent = 'No anomalies logged yet.';
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    events.forEach((event) => {
        const row = document.createElement('tr');
        [event.timestamp, event.anomaly_type, event.details].forEach((value) => {
            const cell = document.createElement('td');
            cell.textContent = value || 'N/A';
            row.appendChild(cell);
        });
        tbody.appendChild(row);
    });
}

function renderScreenshots(screenshots) {
    const gallery = document.getElementById('screenshot-gallery');
    gallery.replaceChildren();

    if (screenshots.length === 0) {
        const emptyState = document.createElement('p');
        emptyState.className = 'empty-state';
        emptyState.textContent = 'No screenshots captured yet.';
        gallery.appendChild(emptyState);
        return;
    }

    screenshots.forEach((filename) => {
        const figure = document.createElement('figure');
        figure.className = 'evidence-card';

        const image = document.createElement('img');
        image.src = `/screenshots/${encodeURIComponent(filename)}`;
        image.alt = `Captured evidence: ${filename}`;
        image.loading = 'lazy';

        const caption = document.createElement('figcaption');
        caption.textContent = filename;

        figure.append(image, caption);
        gallery.appendChild(figure);
    });
}

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`${url} returned HTTP ${response.status}`);
    }
    return response.json();
}

async function updateDashboard() {
    try {
        const [statusData, eventsData, screenData] = await Promise.all([
            fetchJson('/api/status'),
            fetchJson('/api/events'),
            fetchJson('/api/screenshots')
        ]);

        if (!Array.isArray(eventsData.events) || !Array.isArray(screenData.screenshots)) {
            throw new Error('Dashboard API returned an unexpected response');
        }
        setMetric('cam-status', statusData.camera_status || 'UNKNOWN', stateForCamera(statusData.camera_status));
        updateFeedStatus(statusData.camera_status);
        setMetric('face-count', statusData.face_count ?? '--', 'neutral');
        setMetric('head-dir', statusData.head_direction || 'N/A', 'neutral');
        setMetric('sys-status', statusData.system_status || 'UNKNOWN', stateForSystem(statusData.system_status));
        renderEvents(eventsData.events);
        renderScreenshots(screenData.screenshots);

        document.getElementById('updated-time').textContent = new Date().toLocaleTimeString();
        setConnectionStatus('Connected', 'connected');
    } catch (error) {
        console.error('Dashboard refresh failed:', error);
        setConnectionStatus('Connection issue', 'error');
    }
}

updateDashboard();
setInterval(updateDashboard, refreshInterval);
