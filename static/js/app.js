/**
 * LanScan IP Tracker - Client Application
 */

let currentDevices = [];
let activeFilter = 'all';
let isScanning = false;
let sseSource = null;
let currentEditingMac = null;

document.addEventListener('DOMContentLoaded', () => {
    initSubnetSelector();
    initAutoScanSelector();
    initSearch();
    loadStats();
    loadDevices();
    connectSSE();
});

// ----------------------------------------------------
// Server-Sent Events (SSE) for Real-Time Scan Progress
// ----------------------------------------------------
function connectSSE() {
    if (sseSource) {
        sseSource.close();
    }
    
    sseSource = new EventSource('/api/scan/stream');

    sseSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleScanEvent(data);
        } catch (e) {
            // Non-JSON or ping
        }
    };

    sseSource.onerror = () => {
        // Reconnect after brief pause
        setTimeout(connectSSE, 5000);
    };
}

function handleScanEvent(evt) {
    const card = document.getElementById('scanProgressCard');
    const progressBar = document.getElementById('progressBar');
    const progressCount = document.getElementById('scanProgressCount');
    const percentSpan = document.getElementById('scanPercent');
    const statusText = document.getElementById('scanStatusText');
    const foundSpan = document.getElementById('scanFoundCount');

    if (evt.type === 'start') {
        setScanningState(true);
        card.classList.remove('hidden');
        progressBar.style.width = '0%';
        percentSpan.innerText = '0%';
        statusText.innerText = `Сканування ${evt.subnet || 'мережі'}...`;
        foundSpan.innerText = '0';
    } else if (evt.type === 'progress') {
        progressBar.style.width = `${evt.percent}%`;
        percentSpan.innerText = `${evt.percent}%`;
        progressCount.innerText = `${evt.scanned} / ${evt.total}`;
    } else if (evt.type === 'device_found') {
        progressBar.style.width = `${evt.percent}%`;
        percentSpan.innerText = `${evt.percent}%`;
        progressCount.innerText = `${evt.scanned} / ${evt.total}`;
        foundSpan.innerText = parseInt(foundSpan.innerText || '0') + 1;
        // Reload list dynamically
        loadDevices(false);
        loadStats();
    } else if (evt.type === 'finished' || evt.type === 'complete') {
        progressBar.style.width = '100%';
        percentSpan.innerText = '100%';
        statusText.innerText = `Сканування завершено! Знайдено ${evt.total_found} пристроїв за ${evt.duration}с`;
        setScanningState(false);
        loadDevices();
        loadStats();
        showToast(`✅ Сканування завершено: знайдено ${evt.total_found} пристроїв (${evt.duration}с)`);
        setTimeout(() => {
            card.classList.add('hidden');
        }, 4000);
    } else if (evt.type === 'error') {
        setScanningState(false);
        showToast(`❌ Помилка: ${evt.error}`, '⚠️');
        card.classList.add('hidden');
    }
}

// ----------------------------------------------------
// Scan Actions (Top & Bottom Buttons)
// ----------------------------------------------------
async function startScan() {
    if (isScanning) return;

    let subnet = document.getElementById('subnetSelect').value;
    if (subnet === 'custom') {
        subnet = document.getElementById('customSubnetInput').value.trim();
        if (!subnet) {
            showToast('Введіть підмережу (наприклад 192.168.1.0/24)', '⚠️');
            return;
        }
    }

    setScanningState(true);

    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subnet: subnet })
        });
        const data = await res.json();
        
        if (data.status === 'already_scanning') {
            showToast('Сканування вже виконується', 'ℹ️');
        } else {
            showToast('Початок швидкого сканування...', '🔍');
            document.getElementById('scanProgressCard').classList.remove('hidden');
        }
    } catch (err) {
        setScanningState(false);
        showToast('Не вдалося запустити сканування', '❌');
    }
}

function setScanningState(scanning) {
    isScanning = scanning;
    const topBtn = document.getElementById('topScanBtn');
    const bottomBtn = document.getElementById('bottomScanBtn');

    [topBtn, bottomBtn].forEach(btn => {
        if (!btn) return;
        const icon = btn.querySelector('.scan-icon');
        const label = btn.querySelector('.scan-label');

        if (scanning) {
            btn.disabled = true;
            btn.classList.add('opacity-75');
            if (icon) icon.classList.add('spin-anim');
            if (label) label.innerText = 'Сканування...';
        } else {
            btn.disabled = false;
            btn.classList.remove('opacity-75');
            if (icon) icon.classList.remove('spin-anim');
            if (label) {
                label.innerText = btn.id === 'topScanBtn' ? 'Сканувати мережу' : 'Повторити сканування мережі';
            }
        }
    });
}

// ----------------------------------------------------
// Devices & Stats Loading
// ----------------------------------------------------
async function loadDevices(showLoadingSpinner = true) {
    const tbody = document.getElementById('deviceTableBody');
    const query = document.getElementById('searchInput').value.trim();

    if (showLoadingSpinner && currentDevices.length === 0) {
        tbody.innerHTML = `
            <tr>
              <td colspan="7" class="py-12 text-center text-slate-500">
                <div class="flex flex-col items-center justify-center gap-2">
                  <svg class="w-8 h-8 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span>Завантаження пристроїв...</span>
                </div>
              </td>
            </tr>
        `;
    }

    try {
        const url = `/api/devices?search=${encodeURIComponent(query)}&status=${activeFilter}`;
        const res = await fetch(url);
        const data = await res.json();
        currentDevices = data.devices || [];
        renderDeviceTable(currentDevices);
    } catch (err) {
        tbody.innerHTML = `
            <tr>
              <td colspan="7" class="py-8 text-center text-red-400">
                Помилка завантаження даних
              </td>
            </tr>
        `;
    }
}

async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();

        document.getElementById('statOnline').innerText = stats.online;
        document.getElementById('statComputers').innerText = stats.computers;
        document.getElementById('statTotal').innerText = stats.total;
        document.getElementById('statFavorites').innerText = stats.favorites;

        // Filter button counts
        document.getElementById('countFilterAll').innerText = stats.total;
        document.getElementById('countFilterOnline').innerText = stats.online;
        document.getElementById('countFilterComputers').innerText = stats.computers;
        document.getElementById('countFilterFavorites').innerText = stats.favorites;
        document.getElementById('countFilterOffline').innerText = stats.offline;
    } catch (err) {
        console.error("Stats load error", err);
    }
}

// ----------------------------------------------------
// Rendering Device Table
// ----------------------------------------------------
function renderDeviceTable(devices) {
    const tbody = document.getElementById('deviceTableBody');

    if (!devices || devices.length === 0) {
        tbody.innerHTML = `
            <tr>
              <td colspan="7" class="py-12 text-center text-slate-400">
                <div class="flex flex-col items-center justify-center gap-2">
                  <svg class="w-10 h-10 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                  </svg>
                  <p class="font-medium text-slate-300">Пристроїв не знайдено</p>
                  <p class="text-xs text-slate-500">Натисніть кнопку "Сканувати мережу" зверху або знизу для пошуку пристроїв.</p>
                </div>
              </td>
            </tr>
        `;
        return;
    }

    let html = '';
    devices.forEach(dev => {
        const isOnline = dev.is_online === 1 || dev.is_online === true;
        const latency = dev.last_latency ? parseFloat(dev.last_latency) : 0;
        let latencyBadge = '';
        
        if (isOnline && latency > 0) {
            const latClass = latency < 25 ? 'latency-fast' : (latency < 100 ? 'latency-medium' : 'latency-slow');
            latencyBadge = `<span class="text-[10px] px-1.5 py-0.5 rounded font-mono ${latClass}">${latency} ms</span>`;
        }

        // Device Icon based on type
        let devIcon = '💻';
        const typeLower = (dev.device_type || '').toLowerCase();
        if (typeLower.includes('роутер')) devIcon = '🌐';
        else if (typeLower.includes('смартфон') || typeLower.includes('мобільний')) devIcon = '📱';
        else if (typeLower.includes('розумний') || typeLower.includes('iot')) devIcon = '💡';
        else if (typeLower.includes('принтер')) devIcon = '🖨️';
        else if (typeLower.includes('сховище') || typeLower.includes('nas')) devIcon = '🗄️';
        else if (typeLower.includes('тб') || typeLower.includes('медіа')) devIcon = '📺';

        // Favorite star
        const isFav = dev.is_favorite === 1;
        const favIcon = isFav ? '⭐' : '☆';

        // Display Name
        const customName = dev.custom_name ? escapeHtml(dev.custom_name) : '';
        const hostname = dev.hostname ? escapeHtml(dev.hostname) : '';
        
        let primaryName = customName || hostname || "Без назви";
        let secondaryName = customName && hostname ? hostname : (dev.vendor || '');

        html += `
          <tr class="device-row border-b border-slate-800/40">
            <!-- Online status indicator -->
            <td class="py-3 px-4 text-center">
              ${isOnline 
                ? '<span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 status-pulse-online" title="Онлайн"></span>'
                : '<span class="inline-block w-2.5 h-2.5 rounded-full bg-slate-600" title="Офлайн"></span>'}
            </td>

            <!-- IP Address -->
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <span class="font-mono font-semibold text-slate-100">${dev.ip}</span>
                ${latencyBadge}
                <button onclick="copyToClipboard('${dev.ip}', 'IP скопійовано')" class="text-slate-400 hover:text-blue-400 p-1 rounded hover:bg-slate-800 transition-colors" title="Копіювати IP">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </button>
              </div>
            </td>

            <!-- Device Name & Hostname -->
            <td class="py-3 px-4">
              <div class="flex items-center gap-2">
                <span class="text-base select-none">${devIcon}</span>
                <div>
                  <div class="font-medium text-slate-200 flex items-center gap-1.5">
                    <span>${primaryName}</span>
                    <button onclick="openEditModal('${dev.mac}')" class="text-slate-500 hover:text-blue-400 text-xs p-0.5 rounded hover:bg-slate-800" title="Змінити назву">
                      ✏️
                    </button>
                  </div>
                  ${secondaryName ? `<div class="text-xs text-slate-400 truncate max-w-xs">${secondaryName}</div>` : ''}
                </div>
              </div>
            </td>

            <!-- Vendor / Type -->
            <td class="py-3 px-4">
              <div class="text-xs font-medium text-slate-200">${escapeHtml(dev.vendor || 'Невідомо')}</div>
              <div class="text-[11px] text-blue-400/90">${escapeHtml(dev.device_type || 'Пристрій')}</div>
            </td>

            <!-- MAC Address -->
            <td class="py-3 px-4">
              <div class="flex items-center gap-1.5 font-mono text-xs text-slate-400">
                <span>${dev.mac}</span>
                <button onclick="copyToClipboard('${dev.mac}', 'MAC скопійовано')" class="text-slate-500 hover:text-blue-400 p-1" title="Копіювати MAC">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </button>
              </div>
            </td>

            <!-- Last Seen -->
            <td class="py-3 px-4 text-xs text-slate-400 whitespace-nowrap">
              ${formatTimestamp(dev.last_seen)}
            </td>

            <!-- Actions -->
            <td class="py-3 px-4 text-right whitespace-nowrap">
              <div class="flex items-center justify-end gap-1">
                <button onclick="toggleFavorite('${dev.mac}', ${!isFav})" class="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-amber-400 transition-colors" title="${isFav ? 'Видалити з обраних' : 'Додати до обраних'}">
                  ${favIcon}
                </button>
                <button onclick="openEditModal('${dev.mac}')" class="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-blue-400 transition-colors" title="Редагувати">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                  </svg>
                </button>
                <button onclick="confirmDelete('${dev.mac}')" class="p-1.5 rounded hover:bg-slate-800 text-slate-500 hover:text-red-400 transition-colors" title="Видалити з бази">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        `;
    });

    tbody.innerHTML = html;
}

// ----------------------------------------------------
// Filter & Search Controls
// ----------------------------------------------------
function setFilter(filter) {
    activeFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(btn => {
        if (btn.dataset.filter === filter) {
            btn.classList.add('bg-blue-600', 'text-white');
            btn.classList.remove('bg-slate-800', 'text-slate-300');
        } else {
            btn.classList.remove('bg-blue-600', 'text-white');
            btn.classList.add('bg-slate-800', 'text-slate-300');
        }
    });
    loadDevices();
}

function initSearch() {
    const input = document.getElementById('searchInput');
    let timeout = null;
    input.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            loadDevices(false);
        }, 200);
    });
}

function initSubnetSelector() {
    const select = document.getElementById('subnetSelect');
    const customBox = document.getElementById('customSubnetBox');
    const display = document.getElementById('currentSubnetDisplay');

    select.addEventListener('change', () => {
        if (select.value === 'custom') {
            customBox.classList.remove('hidden');
        } else {
            customBox.classList.add('hidden');
            display.innerText = select.value;
        }
    });
}

function initAutoScanSelector() {
    const select = document.getElementById('autoScanInterval');
    
    // Fetch initial status
    fetch('/api/auto-scan')
        .then(r => r.json())
        .then(cfg => {
            if (!cfg.enabled) {
                select.value = "0";
            } else {
                select.value = String(cfg.interval_seconds);
            }
        });

    select.addEventListener('change', async () => {
        const val = parseInt(select.value, 10);
        const enabled = val > 0;
        await fetch('/api/auto-scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: enabled, interval_seconds: val || 300 })
        });
        showToast(enabled ? `Авто-сканування увімкнено (кожні ${val/60} хв)` : 'Авто-сканування вимкнено', '⏱️');
    });
}

// ----------------------------------------------------
// Device Edit Modal
// ----------------------------------------------------
function openEditModal(mac) {
    const dev = currentDevices.find(d => d.mac.toUpperCase() === mac.toUpperCase());
    if (!dev) return;

    currentEditingMac = mac;
    document.getElementById('modalIp').innerText = dev.ip;
    document.getElementById('modalMac').innerText = dev.mac;
    document.getElementById('modalCustomName').value = dev.custom_name || '';
    document.getElementById('modalNotes').value = dev.notes || '';
    document.getElementById('modalFavorite').checked = dev.is_favorite === 1;

    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
    currentEditingMac = null;
}

async function saveDeviceEdit() {
    if (!currentEditingMac) return;

    const customName = document.getElementById('modalCustomName').value;
    const notes = document.getElementById('modalNotes').value;
    const isFavorite = document.getElementById('modalFavorite').checked;

    try {
        await fetch(`/api/devices/${encodeURIComponent(currentEditingMac)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                custom_name: customName,
                notes: notes,
                is_favorite: isFavorite
            })
        });

        closeEditModal();
        showToast('Дані пристрою збережено! ✨');
        loadDevices(false);
        loadStats();
    } catch (e) {
        showToast('Помилка збереження', '❌');
    }
}

async function toggleFavorite(mac, newFavStatus) {
    try {
        await fetch(`/api/devices/${encodeURIComponent(mac)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_favorite: newFavStatus })
        });
        loadDevices(false);
        loadStats();
    } catch (e) {
        showToast('Помилка оновлення', '❌');
    }
}

async function confirmDelete(mac) {
    if (confirm(`Видалити пристрій з MAC ${mac} з історії відстеження?`)) {
        await fetch(`/api/devices/${encodeURIComponent(mac)}`, { method: 'DELETE' });
        showToast('Пристрій видалено');
        loadDevices(false);
        loadStats();
    }
}

// ----------------------------------------------------
// Utilities & UI Helpers
// ----------------------------------------------------
function toggleExportMenu() {
    const menu = document.getElementById('exportMenu');
    menu.classList.toggle('hidden');
}

document.addEventListener('click', (e) => {
    const exportBtn = document.getElementById('exportBtn');
    const menu = document.getElementById('exportMenu');
    if (exportBtn && !exportBtn.contains(e.target) && menu && !menu.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

function copyToClipboard(text, successMsg) {
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMsg || 'Скопійовано!');
    }).catch(() => {
        showToast('Не вдалося скопіювати', '⚠️');
    });
}

function showToast(message, icon = '📋') {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');
    const toastIcon = document.getElementById('toastIcon');

    toastMsg.innerText = message;
    toastIcon.innerText = icon;

    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 2800);
}

function formatTimestamp(tsStr) {
    if (!tsStr) return '—';
    try {
        const parts = tsStr.split(' ');
        const datePart = parts[0];
        const timePart = parts[1] || '';
        return `<span class="text-slate-300 font-mono">${timePart.slice(0, 5)}</span> <span class="text-slate-500 text-[10px]">${datePart}</span>`;
    } catch (e) {
        return tsStr;
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}
