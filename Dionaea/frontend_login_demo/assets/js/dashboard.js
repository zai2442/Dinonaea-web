/**
 * Dionaea Dashboard Logic
 * Handles authentication check, role-based rendering, and data fetching.
 */

const CONFIG = {
    API_BASE: 'http://localhost:8001/api/v1',
    LOGIN_URL: 'index.html'
};

// State
let currentUser = null;
let currentLogsPage = 0;
const logsPerPage = 50;

// Chart Instances
    let chartTopIPs = null;
    let chartTopUsers = null;
    let chartTopPwds = null;
    let chartAttackDist = null;
    let chartTrafficTimeline = null;

    document.addEventListener('DOMContentLoaded', async () => {
    // 1. Auth Check
    const token = localStorage.getItem('dionaea_access_token');
    if (!token) {
        window.location.href = CONFIG.LOGIN_URL;
        return;
    }

    // 2. Fetch User Info
    try {
        currentUser = await fetchCurrentUser(token);
        renderUserProfile(currentUser);
        renderSidebar(currentUser);
        
        // Setup Modal Listeners
        setupModalEventListeners();
        
        // Initial View
        loadDashboardStats();
        
    } catch (error) {
        console.error('Auth Error:', error);
        // If 401, redirect to login
        if (error.status === 401) {
            localStorage.removeItem('dionaea_access_token');
            localStorage.removeItem('dionaea_refresh_token');
            window.location.href = CONFIG.LOGIN_URL;
        } else {
            alert('无法加载用户信息，请重试');
        }
    }

    // 3. Event Listeners
    setupEventListeners();
    setupLogEventListeners();
});

// API Calls
async function fetchCurrentUser(token) {
    const response = await fetch(`${CONFIG.API_BASE}/users/me`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        const error = new Error('Failed to fetch user');
        error.status = response.status;
        throw error;
    }
    
    return await response.json();
}

async function fetchUsers() {
    const token = localStorage.getItem('dionaea_access_token');
    const response = await fetch(`${CONFIG.API_BASE}/users/?limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
        return await response.json();
    }
    return { items: [], total: 0 };
}

// Log & Stats API
async function fetchLogs(skip = 0, limit = 50, filters = {}) {
    const token = localStorage.getItem('dionaea_access_token');
    const params = new URLSearchParams({ skip, limit });
    
    if (filters.ip) params.append('source_ip', filters.ip);
    if (filters.protocol) params.append('attack_type', filters.protocol);
    if (filters.startDate) params.append('start_time', filters.startDate);
    if (filters.endDate) params.append('end_time', filters.endDate);

    const response = await fetch(`${CONFIG.API_BASE}/data/logs?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
        return await response.json();
    }
    throw new Error('Failed to fetch logs');
}

async function fetchStatsCharts() {
    const token = localStorage.getItem('dionaea_access_token');
    const response = await fetch(`${CONFIG.API_BASE}/data/stats/charts`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) return await response.json();
    throw new Error('Failed to fetch stats');
}

async function fetchStatsSummary() {
    const token = localStorage.getItem('dionaea_access_token');
    const response = await fetch(`${CONFIG.API_BASE}/data/stats/summary`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) return await response.json();
    throw new Error('Failed to fetch summary');
}


// --- Log Detail Modal Logic ---
function openLogDetailModal(content) {
    const modal = document.getElementById('log-detail-modal');
    const contentDiv = document.getElementById('log-detail-content');
    
    contentDiv.textContent = content || '暂无原始流量数据';
    modal.classList.remove('hidden');
    
    // Body scroll lock
    document.body.style.overflow = 'hidden';
}

function closeLogDetailModal() {
    const modal = document.getElementById('log-detail-modal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

function setupModalEventListeners() {
    // Log Detail Modal
    document.getElementById('close-log-modal').addEventListener('click', closeLogDetailModal);
    document.getElementById('btn-close-log-footer').addEventListener('click', closeLogDetailModal);
    
    document.getElementById('log-detail-modal').addEventListener('click', (e) => {
        if (e.target.id === 'log-detail-modal') closeLogDetailModal();
    });

    // Copy functionality
    document.getElementById('btn-copy-log').addEventListener('click', () => {
        const content = document.getElementById('log-detail-content').textContent;
        navigator.clipboard.writeText(content).then(() => {
            const btn = document.getElementById('btn-copy-log');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check mr-1"></i> 已复制';
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 2000);
        });
    });
}

// Rendering
function renderUserProfile(user) {
    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-avatar').textContent = user.username.charAt(0).toUpperCase();
    
    // Display roles
    const roles = user.roles && user.roles.length > 0 
        ? user.roles.map(r => r.name).join(', ') 
        : '普通用户';
    document.getElementById('user-role').textContent = roles;
}

function renderSidebar(user) {
    const menuContainer = document.getElementById('sidebar-menu');
    menuContainer.innerHTML = ''; // Clear

    // Define Menu Items with Permission Requirements
    const menuItems = [
        { id: 'nav-dashboard', label: '仪表盘', icon: 'fas fa-tachometer-alt', view: 'view-dashboard', permission: null },
        { id: 'nav-analysis', label: '流量分析', icon: 'fas fa-project-diagram', view: 'view-traffic-analysis', permission: 'data:stats' },
        { id: 'nav-users', label: '用户管理', icon: 'fas fa-users', view: 'view-users', permission: 'user:list' },
        { id: 'nav-roles', label: '角色权限', icon: 'fas fa-user-tag', view: 'view-roles', permission: 'role:list' },
        { id: 'nav-monitor', label: '系统监控', icon: 'fas fa-server', view: 'view-monitor', permission: 'system:monitor' },
        { id: 'nav-stats', label: '数据统计', icon: 'fas fa-chart-bar', view: 'view-stats', permission: 'data:stats' },
        { id: 'nav-settings', label: '系统设置', icon: 'fas fa-cogs', view: 'view-settings', permission: null },
    ];

    const userPermissions = new Set();
    let isSuperAdmin = false;

    if (user.roles) {
        user.roles.forEach(role => {
            if (role.code === 'super_admin') isSuperAdmin = true;
            if (role.permissions) {
                role.permissions.forEach(p => userPermissions.add(p.code));
            }
        });
    }

    menuItems.forEach(item => {
        // Check permission
        const hasPermission = !item.permission || isSuperAdmin || userPermissions.has(item.permission);
        
        if (hasPermission) {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'sidebar-item text-gray-600';
            if (item.id === 'nav-dashboard') link.classList.add('active'); // Active by default
            
            link.innerHTML = `<i class="${item.icon}"></i> <span>${item.label}</span>`;
            link.dataset.view = item.view;
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                switchView(item.view, link);
                // On mobile, close sidebar after click
                if (window.innerWidth < 768) {
                    toggleSidebar(false);
                }
            });
            
            menuContainer.appendChild(link);
        }
    });
}

function switchView(viewId, activeLink) {
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    
    // Show target view
    const target = document.getElementById(viewId);
    if (target) {
        target.classList.remove('hidden');
        // Update Title
        const titleMap = {
            'view-dashboard': '仪表盘',
            'view-traffic-analysis': '流量分析',
            'view-users': '用户管理',
            'view-roles': '角色权限管理',
            'view-monitor': '系统监控',
            'view-stats': '数据统计',
            'view-settings': '系统设置'
        };
        document.getElementById('page-title').textContent = titleMap[viewId] || '仪表盘';
        
        // Load data if needed
        if (viewId === 'view-users') loadUsersList();
        if (viewId === 'view-roles') loadRolesList();
        if (viewId === 'view-monitor') loadLogs();
        if (viewId === 'view-stats') loadStats();
        if (viewId === 'view-traffic-analysis') loadTrafficAnalysis();
        if (viewId === 'view-settings') loadNodesList();
    }

    // Update Sidebar Active State
    document.querySelectorAll('#sidebar-menu a').forEach(a => {
        a.classList.remove('active');
        a.classList.add('text-gray-600');
    });
    if (activeLink) {
        activeLink.classList.remove('text-gray-600');
        activeLink.classList.add('active');
    }
}

async function loadDashboardStats() {
    try {
        const users = await fetchUsers();
        document.getElementById('stat-users').textContent = users.total || 0;

        const stats = await fetchStatsSummary();
        document.getElementById('stat-total-logs').textContent = stats.total_logs || 0;
    } catch (e) {
        console.warn('Failed to fetch dashboard stats', e);
    }
}

async function loadUsersList() {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">加载中...</td></tr>';
    
    try {
        const data = await fetchUsers();
        tbody.innerHTML = '';
        
        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">暂无用户</td></tr>';
            // Even if no users, if super admin, show add button (logic below handles visibility)
        }

        const isSuperAdmin = currentUser && currentUser.roles && currentUser.roles.some(r => r.code === 'super_admin');
        
        // Show/Hide Add User Button
        const addUserBtn = document.getElementById('btn-add-user');
        if (isSuperAdmin) {
            addUserBtn.classList.remove('hidden');
            addUserBtn.onclick = openAddUserModal;
        } else {
            addUserBtn.classList.add('hidden');
        }

        data.items.forEach(user => {
            const roleNames = user.roles.map(r => r.name).join(', ') || '-';
            
            let actionButtons = '<span class="text-gray-400 text-xs">无权限</span>';
            if (isSuperAdmin) {
                if (user.username === 'admin') {
                     actionButtons = '<span class="text-gray-400 text-xs"><i class="fas fa-lock mr-1"></i>系统锁定</span>';
                } else {
                    actionButtons = `
                        <button class="text-primary hover:text-primary-hover mr-2 btn-edit-user" data-id="${user.id}">编辑</button>
                        <button class="text-error hover:text-red-700 btn-delete-user" data-id="${user.id}" data-username="${user.username}">删除</button>
                    `;
                }
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${user.username}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${user.email}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${roleNames}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                        ${user.status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${actionButtons}
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Event Delegation for buttons
        if (isSuperAdmin) {
            const editBtns = tbody.querySelectorAll('.btn-edit-user');
            editBtns.forEach(btn => {
                btn.addEventListener('click', () => openEditUserModal(btn.dataset.id));
            });
            
            const deleteBtns = tbody.querySelectorAll('.btn-delete-user');
            deleteBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const user = { id: btn.dataset.id, username: btn.dataset.username };
                    openDeleteUserModal(user);
                });
            });
        }
        
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-error">加载失败</td></tr>';
    }
}

// --- Monitor & Stats Logic ---

async function loadLogs(resetPage = false) {
    if (resetPage) currentLogsPage = 0;
    
    const tbody = document.getElementById('logs-table-body');
    const loading = document.getElementById('logs-loading');
    
    tbody.innerHTML = '';
    loading.classList.remove('hidden');
    
    const filters = {
        ip: document.getElementById('filter-ip').value,
        protocol: document.getElementById('filter-protocol').value,
        startDate: document.getElementById('filter-start-date').value,
        endDate: document.getElementById('filter-end-date').value
    };

    try {
        const logs = await fetchLogs(currentLogsPage * logsPerPage, logsPerPage, filters);
        loading.classList.add('hidden');
        
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-gray-500">暂无日志数据</td></tr>';
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-blue-50 transition-all cursor-pointer group relative';
            tr.title = '点击查看完整流量包详情';
            
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${new Date(log.timestamp).toLocaleString()}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${log.sensor_name || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${log.source_ip || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${log.username || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">${log.password || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 flex items-center justify-between">
                    <span>${(log.protocol || 'SMB').toUpperCase()}</span>
                    <i class="fas fa-external-link-alt text-gray-300 group-hover:text-primary transition-colors text-xs ml-2"></i>
                </td>
            `;

            // Click event to show modal
            tr.addEventListener('click', () => {
                openLogDetailModal(log.raw_log);
            });

            tbody.appendChild(tr);
        });

        // Pagination controls state
        document.getElementById('btn-prev-page').disabled = currentLogsPage === 0;
        document.getElementById('btn-next-page').disabled = logs.length < logsPerPage;

    } catch (e) {
        loading.classList.add('hidden');
        tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-error">加载失败</td></tr>';
    }
}

async function loadStats() {
    try {
        const [chartsData, summaryData] = await Promise.all([
            fetchStatsCharts(),
            fetchStatsSummary()
        ]);
        
        renderStatsCharts(chartsData);
        renderStatsSummary(summaryData);
        
        document.getElementById('stats-last-updated').textContent = `更新时间: ${new Date().toLocaleTimeString()}`;
        
    } catch (e) {
        console.error("Failed to load stats", e);
    }
}

function renderStatsSummary(data) {
    // Mimic Login_statistics.sh output
    // { most_login_ip: {name, value}, ... }
    const setSummary = (id, item) => {
        document.getElementById(id).textContent = item.name || 'N/A';
        document.getElementById(`${id}-count`).textContent = `${item.value || 0} 次`;
    };
    
    setSummary('summary-ip', data.most_login_ip);
    setSummary('summary-user', data.most_login_username);
    setSummary('summary-pwd', data.most_login_password);
}

function renderStatsCharts(data) {
    // 1. Top IPs Bar Chart
    if (!chartTopIPs) chartTopIPs = echarts.init(document.getElementById('chart-top-ips'));
    chartTopIPs.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.top_ips.map(i => i.name) },
        yAxis: { type: 'value' },
        series: [{
            data: data.top_ips.map(i => i.value),
            type: 'bar',
            itemStyle: { color: '#1890ff' },
            label: { show: true, position: 'top' }
        }]
    });
    chartTopIPs.on('click', (params) => {
        // Drill down: switch to monitor view and filter by IP
        document.getElementById('filter-ip').value = params.name;
        // Find monitor link
        const monitorLink = document.querySelector('[data-view="view-monitor"]');
        if (monitorLink) monitorLink.click();
    });

    // 2. Top Users Pie Chart
    if (!chartTopUsers) chartTopUsers = echarts.init(document.getElementById('chart-top-users'));
    chartTopUsers.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
            name: '用户名',
            type: 'pie',
            radius: '50%',
            data: data.top_usernames,
            emphasis: {
                itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
            }
        }]
    });

    // 3. Top Passwords Word Cloud
    if (!chartTopPwds) chartTopPwds = echarts.init(document.getElementById('chart-top-pwds'));
    chartTopPwds.setOption({
        tooltip: {},
        series: [{
            type: 'wordCloud',
            gridSize: 2,
            sizeRange: [12, 50],
            rotationRange: [-90, 90],
            shape: 'pentagon',
            width: 600,
            height: 400,
            drawOutOfBound: false,
            textStyle: {
                color: function () {
                    return 'rgb(' + [
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160)
                    ].join(',') + ')';
                }
            },
            emphasis: {
                textStyle: { shadowBlur: 10, shadowColor: '#333' }
            },
            data: data.top_passwords
        }]
    });
    
    // Resize handling
    window.addEventListener('resize', () => {
        chartTopIPs && chartTopIPs.resize();
        chartTopUsers && chartTopUsers.resize();
        chartTopPwds && chartTopPwds.resize();
    });
}

function setupLogEventListeners() {
    // Search Button
    document.getElementById('btn-search-logs').addEventListener('click', () => {
        loadLogs(true);
    });
    
    // Pagination
    document.getElementById('btn-prev-page').addEventListener('click', () => {
        if (currentLogsPage > 0) {
            currentLogsPage--;
            loadLogs();
        }
    });
    
    document.getElementById('btn-next-page').addEventListener('click', () => {
        currentLogsPage++;
        loadLogs();
    });

    // Refresh Analysis Button
    const refreshAnalysisBtn = document.getElementById('btn-refresh-analysis');
    if (refreshAnalysisBtn) {
        refreshAnalysisBtn.addEventListener('click', loadTrafficAnalysis);
    }

    // Analysis Search Button
    const searchAnalysisBtn = document.getElementById('btn-search-analysis');
    if (searchAnalysisBtn) {
        searchAnalysisBtn.addEventListener('click', loadTrafficAnalysis);
    }
}

// --- Traffic Analysis Logic ---
async function loadTrafficAnalysis() {
    try {
        const token = localStorage.getItem('dionaea_access_token');
        
        // Build query params
        const filters = {
            ip: document.getElementById('analysis-filter-ip').value,
            type: document.getElementById('analysis-filter-type').value,
            startDate: document.getElementById('analysis-filter-start-date').value,
            endDate: document.getElementById('analysis-filter-end-date').value
        };

        const params = new URLSearchParams();
        if (filters.ip) params.append('source_ip', filters.ip);
        if (filters.type) params.append('attack_type', filters.type);
        if (filters.startDate) params.append('start_time', filters.startDate);
        if (filters.endDate) params.append('end_time', filters.endDate);

        // 1. Fetch Stats (Pass filters if backend supports, currently backend might not support filtering stats yet, but let's send for future)
        // Note: The current /stats/traffic endpoint in backend does not accept filters yet.
        // We might need to update backend to support filtered stats, or just filter logs table.
        // For now, let's just fetch global stats as before (or update backend if requested).
        // User asked for "filtering function similar to system monitor", implying the charts/table should update.
        // Let's assume we want to filter the TABLE first.
        
        const statsRes = await fetch(`${CONFIG.API_BASE}/data/stats/traffic?${params.toString()}`, {
             headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!statsRes.ok) throw new Error('Failed to fetch traffic stats');
        const stats = await statsRes.json();
        renderTrafficCharts(stats);
        
        // 2. Fetch Logs for Analysis Table with filters
        // Reuse logs endpoint but with higher limit
        params.append('limit', '100');
        const logsRes = await fetch(`${CONFIG.API_BASE}/data/logs?${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!logsRes.ok) throw new Error('Failed to fetch logs');
        const logs = await logsRes.json();
        renderAnalysisLogs(logs);
        
    } catch (e) {
        console.error(e);
        showToast('加载分析数据失败', 'error');
    }
}

function renderTrafficCharts(stats) {
    // 1. Attack Distribution Pie Chart
    if (!chartAttackDist) chartAttackDist = echarts.init(document.getElementById('chart-attack-dist'));
    chartAttackDist.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
            name: '攻击类型',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: { show: false, position: 'center' },
            emphasis: {
                label: { show: true, fontSize: '18', fontWeight: 'bold' }
            },
            labelLine: { show: false },
            data: stats.attack_distribution
        }]
    });
    
    // 2. Traffic Timeline Line Chart
    if (!chartTrafficTimeline) chartTrafficTimeline = echarts.init(document.getElementById('chart-traffic-timeline'));
    chartTrafficTimeline.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { 
            type: 'category', 
            data: stats.timeline.map(t => new Date(t.time).getHours() + ':00') 
        },
        yAxis: { type: 'value' },
        series: [{
            data: stats.timeline.map(t => t.count),
            type: 'line',
            smooth: true,
            areaStyle: { opacity: 0.3 },
            itemStyle: { color: '#722ed1' }
        }]
    });
    
    // Resize
    window.addEventListener('resize', () => {
        chartAttackDist && chartAttackDist.resize();
        chartTrafficTimeline && chartTrafficTimeline.resize();
    });
}

function renderAnalysisLogs(logs) {
    const tbody = document.getElementById('analysis-logs-body');
    tbody.innerHTML = '';
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center text-gray-500">暂无数据</td></tr>';
        return;
    }

    logs.forEach(log => {
        // Highlight logic: if attack_type is not simple protocol, treat as suspicious/high-risk
        const isSuspicious = !['smb', 'http', 'ftp', 'mssql'].includes((log.attack_type || '').toLowerCase());
        const rowClass = isSuspicious ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-blue-50';
        const typeClass = isSuspicious ? 'text-red-600 font-bold' : 'text-gray-600';
        
        const tr = document.createElement('tr');
        tr.className = `${rowClass} transition-all cursor-pointer group`;
        tr.title = '点击查看完整流量包详情';
        
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${new Date(log.timestamp).toLocaleString()}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${log.sensor_name || '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm ${typeClass}">${log.attack_type || 'Unknown'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${log.source_ip}</td>
            <td class="px-6 py-4 text-sm text-gray-500 font-mono truncate max-w-xs">
                <div class="flex items-center justify-between">
                    <span class="truncate">${(log.raw_log || '').substring(0, 50)}...</span>
                    <i class="fas fa-external-link-alt text-gray-300 group-hover:text-primary transition-colors text-xs ml-2 flex-shrink-0"></i>
                </div>
            </td>
        `;

        // Click event to show modal
        tr.addEventListener('click', () => {
            openLogDetailModal(log.raw_log);
        });

        tbody.appendChild(tr);
    });
}

// UI Interactions (Existing)
function setupEventListeners() {
    // Sidebar Toggle (Mobile)
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    function toggleSidebar(show) {
        if (show) {
            sidebar.classList.remove('-translate-x-full');
            overlay.classList.remove('hidden', 'opacity-0');
            overlay.classList.add('opacity-100');
        } else {
            sidebar.classList.add('-translate-x-full');
            overlay.classList.remove('opacity-100');
            overlay.classList.add('opacity-0');
            setTimeout(() => overlay.classList.add('hidden'), 300);
        }
    }

    toggleBtn.addEventListener('click', () => {
        const isHidden = sidebar.classList.contains('-translate-x-full');
        toggleSidebar(isHidden);
    });

    overlay.addEventListener('click', () => {
        toggleSidebar(false);
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('dionaea_access_token');
        localStorage.removeItem('dionaea_refresh_token');
        window.location.href = CONFIG.LOGIN_URL;
    });

    // User Modals
    setupUserModalListeners();
    // Node Modals
    setupNodeListeners();
}

// --- Toast Notification ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const colors = type === 'success' ? 'bg-green-500' : (type === 'error' ? 'bg-red-500' : 'bg-blue-500');
    const icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle');
    
    toast.className = `${colors} text-white px-4 py-3 rounded shadow-lg flex items-center transition-all duration-300 transform translate-y-2 opacity-0`;
    toast.innerHTML = `<i class="fas ${icon} mr-2"></i> ${message}`;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --- Role Management (for Edit Modal) ---
async function fetchRoles() {
    const token = localStorage.getItem('dionaea_access_token');
    try {
        const response = await fetch(`${CONFIG.API_BASE}/roles/`, {
             headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) return await response.json();
    } catch (e) {
        console.warn('Failed to fetch roles', e);
    }
    return [
        { id: 1, name: 'Super Admin', code: 'super_admin' },
        { id: 2, name: 'Admin', code: 'admin' },
        { id: 3, name: 'User', code: 'user' }
    ];
}

// --- User Operations ---
let userToDelete = null;

function setupUserModalListeners() {
    // Edit Modal
    document.getElementById('close-edit-modal').addEventListener('click', () => {
        document.getElementById('edit-user-modal').classList.add('hidden');
    });
    document.getElementById('cancel-edit').addEventListener('click', () => {
        document.getElementById('edit-user-modal').classList.add('hidden');
    });
    document.getElementById('edit-user-form').addEventListener('submit', handleEditUserSubmit);
    
    // Status Toggle Label Update
    document.getElementById('edit-status').addEventListener('change', (e) => {
        document.getElementById('edit-status-label').textContent = e.target.checked ? 'Active' : 'Pending';
    });

    // Delete Modal
    document.getElementById('cancel-delete').addEventListener('click', () => {
        document.getElementById('delete-user-modal').classList.add('hidden');
        userToDelete = null;
    });
    document.getElementById('confirm-delete').addEventListener('click', confirmDeleteUser);

    // Add User Modal
    document.getElementById('close-add-modal').addEventListener('click', () => {
        document.getElementById('add-user-modal').classList.add('hidden');
    });
    document.getElementById('cancel-add').addEventListener('click', () => {
        document.getElementById('add-user-modal').classList.add('hidden');
    });
    document.getElementById('add-status').addEventListener('change', (e) => {
        document.getElementById('add-status-label').textContent = e.target.checked ? 'Active' : 'Pending';
    });
    document.getElementById('add-user-form').addEventListener('submit', handleAddUserSubmit);

    // Role Modals
    setupRoleModalListeners();
}

// --- Role Operations ---
let allPermissions = [];

function setupRoleModalListeners() {
    // Add Role Button
    document.getElementById('btn-add-role').addEventListener('click', openAddRoleModal);

    // Modal Controls
    document.getElementById('close-role-modal').addEventListener('click', () => {
        document.getElementById('role-modal').classList.add('hidden');
    });
    document.getElementById('cancel-role').addEventListener('click', () => {
        document.getElementById('role-modal').classList.add('hidden');
    });
    document.getElementById('role-form').addEventListener('submit', handleRoleSubmit);
    
    // Status Toggle
    document.getElementById('role-status').addEventListener('change', (e) => {
        document.getElementById('role-status-label').textContent = e.target.checked ? 'Active' : 'Inactive';
    });

    // Permission Select All/None
    document.getElementById('btn-select-all-perms').addEventListener('click', () => {
        document.querySelectorAll('#permissions-container input[type="checkbox"]').forEach(cb => cb.checked = true);
    });
    document.getElementById('btn-deselect-all-perms').addEventListener('click', () => {
        document.querySelectorAll('#permissions-container input[type="checkbox"]').forEach(cb => cb.checked = false);
    });
}

async function loadRolesList() {
    const tbody = document.getElementById('roles-table-body');
    tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-gray-500">加载中...</td></tr>';
    
    try {
        const token = localStorage.getItem('dionaea_access_token');
        const response = await fetch(`${CONFIG.API_BASE}/roles/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Failed to fetch roles');
        const roles = await response.json();
        
        tbody.innerHTML = '';
        if (roles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-gray-500">暂无角色</td></tr>';
        }

        const isSuperAdmin = currentUser && currentUser.roles && currentUser.roles.some(r => r.code === 'super_admin');
        
        // Show/Hide Add Role Button
        const addRoleBtn = document.getElementById('btn-add-role');
        if (isSuperAdmin) addRoleBtn.classList.remove('hidden');
        else addRoleBtn.classList.add('hidden');

        roles.forEach(role => {
            let actionButtons = '<span class="text-gray-400 text-xs">无权限</span>';
            if (isSuperAdmin) {
                // Protect system roles
                if (['super_admin', 'user', 'admin'].includes(role.code)) {
                     actionButtons = `
                        <button class="text-primary hover:text-primary-hover mr-2 btn-edit-role" data-id="${role.id}">配置</button>
                        <span class="text-gray-400 text-xs ml-1"><i class="fas fa-lock"></i> 核心</span>
                     `;
                } else {
                    actionButtons = `
                        <button class="text-primary hover:text-primary-hover mr-2 btn-edit-role" data-id="${role.id}">配置</button>
                        <button class="text-error hover:text-red-700 btn-delete-role" data-id="${role.id}" data-name="${role.name}">删除</button>
                    `;
                }
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${role.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono bg-gray-50 rounded">${role.code}</td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title="${role.description || ''}">${role.description || '-'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${role.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                        ${role.status || 'active'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${actionButtons}
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Bind events
        if (isSuperAdmin) {
            tbody.querySelectorAll('.btn-edit-role').forEach(btn => {
                btn.addEventListener('click', () => openEditRoleModal(btn.dataset.id));
            });
            tbody.querySelectorAll('.btn-delete-role').forEach(btn => {
                btn.addEventListener('click', () => deleteRole(btn.dataset.id, btn.dataset.name));
            });
        }

    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-4 text-center text-error">加载失败</td></tr>';
    }
}

async function fetchPermissions() {
    if (allPermissions.length > 0) return allPermissions;
    
    const token = localStorage.getItem('dionaea_access_token');
    const response = await fetch(`${CONFIG.API_BASE}/roles/permissions/list`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
        allPermissions = await response.json();
        return allPermissions;
    }
    return [];
}

function renderPermissions(container, selectedIds = []) {
    container.innerHTML = '';
    
    // Group permissions by resource_type or prefix
    const groups = {};
    allPermissions.forEach(p => {
        const type = p.resource_type || p.code.split(':')[0] || 'other';
        if (!groups[type]) groups[type] = [];
        groups[type].push(p);
    });

    for (const [type, perms] of Object.entries(groups)) {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'mb-4';
        
        const title = document.createElement('h4');
        title.className = 'text-xs font-bold text-gray-500 uppercase mb-2 border-b pb-1';
        title.textContent = type;
        groupDiv.appendChild(title);
        
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-1 md:grid-cols-2 gap-2';
        
        perms.forEach(p => {
            const label = document.createElement('label');
            label.className = 'flex items-start p-2 hover:bg-white rounded cursor-pointer transition-colors';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = p.id;
            checkbox.className = 'mt-1 mr-2 text-primary focus:ring-primary';
            if (selectedIds.includes(p.id)) checkbox.checked = true;
            
            const info = document.createElement('div');
            info.innerHTML = `
                <div class="text-sm font-medium text-gray-700">${p.code}</div>
                <div class="text-xs text-gray-500">${p.description || p.name || ''}</div>
            `;
            
            label.appendChild(checkbox);
            label.appendChild(info);
            grid.appendChild(label);
        });
        
        groupDiv.appendChild(grid);
        container.appendChild(groupDiv);
    }
}

async function openAddRoleModal() {
    document.getElementById('role-modal-title').textContent = '新增角色';
    document.getElementById('role-form').reset();
    document.getElementById('role-id').value = '';
    document.getElementById('role-status-label').textContent = 'Active';
    
    // Fetch and render permissions
    const container = document.getElementById('permissions-container');
    container.innerHTML = '<p class="text-gray-500 text-center">加载权限中...</p>';
    await fetchPermissions();
    renderPermissions(container, []);
    
    document.getElementById('role-modal').classList.remove('hidden');
}

async function openEditRoleModal(roleId) {
    try {
        const token = localStorage.getItem('dionaea_access_token');
        const response = await fetch(`${CONFIG.API_BASE}/roles/${roleId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Failed to fetch role');
        const role = await response.json();
        
        document.getElementById('role-modal-title').textContent = '编辑角色';
        document.getElementById('role-id').value = role.id;
        document.getElementById('role-name').value = role.name;
        document.getElementById('role-code').value = role.code;
        document.getElementById('role-description').value = role.description || '';
        
        const statusActive = role.status === 'active';
        document.getElementById('role-status').checked = statusActive;
        document.getElementById('role-status-label').textContent = statusActive ? 'Active' : 'Disabled';
        
        // Fetch permissions and mark selected
        const container = document.getElementById('permissions-container');
        container.innerHTML = '<p class="text-gray-500 text-center">加载权限中...</p>';
        await fetchPermissions();
        
        const selectedIds = role.permissions ? role.permissions.map(p => p.id) : [];
        renderPermissions(container, selectedIds);
        
        document.getElementById('role-modal').classList.remove('hidden');
        
    } catch (e) {
        showToast('获取角色信息失败', 'error');
    }
}

async function handleRoleSubmit(e) {
    e.preventDefault();
    
    const roleId = document.getElementById('role-id').value;
    const isEdit = !!roleId;
    
    const name = document.getElementById('role-name').value;
    const code = document.getElementById('role-code').value;
    const description = document.getElementById('role-description').value;
    const status = document.getElementById('role-status').checked ? 'active' : 'disabled';
    
    // Get selected permissions
    const permission_ids = Array.from(document.querySelectorAll('#permissions-container input[type="checkbox"]:checked'))
        .map(cb => parseInt(cb.value));
        
    const payload = {
        name,
        description,
        status,
        permission_ids
    };
    
    if (!isEdit) payload.code = code; // Code is usually immutable or unique checked on create
    
    const token = localStorage.getItem('dionaea_access_token');
    const url = isEdit ? `${CONFIG.API_BASE}/roles/${roleId}` : `${CONFIG.API_BASE}/roles/`;
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            showToast(`角色${isEdit ? '更新' : '创建'}成功`);
            document.getElementById('role-modal').classList.add('hidden');
            loadRolesList();
        } else {
            const error = await response.json();
            showToast(`操作失败: ${error.detail}`, 'error');
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

async function deleteRole(roleId, roleName) {
    if (!confirm(`确定要删除角色 "${roleName}" 吗？此操作不可恢复。`)) return;
    
    const token = localStorage.getItem('dionaea_access_token');
    try {
        const response = await fetch(`${CONFIG.API_BASE}/roles/${roleId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok || response.status === 204) {
            showToast('角色已删除');
            loadRolesList();
        } else {
            const error = await response.json();
            showToast(`删除失败: ${error.detail}`, 'error');
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

async function openAddUserModal() {
    try {
        // Reset Form
        document.getElementById('add-user-form').reset();
        document.getElementById('add-status-label').textContent = 'Active';

        // Populate Roles
        const roles = await fetchRoles();
        const roleSelect = document.getElementById('add-role');
        roleSelect.innerHTML = '';
        roles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.id;
            option.textContent = role.name;
            // Default to 'User'
            if (role.code === 'user') option.selected = true;
            roleSelect.appendChild(option);
        });

        document.getElementById('add-user-modal').classList.remove('hidden');
    } catch (e) {
        showToast('初始化失败', 'error');
    }
}

async function handleAddUserSubmit(e) {
    e.preventDefault();

    const username = document.getElementById('add-username').value;
    const email = document.getElementById('add-email').value;
    const password = document.getElementById('add-password').value;
    const roleId = parseInt(document.getElementById('add-role').value);
    const status = document.getElementById('add-status').checked ? 'active' : 'pending';

    const payload = {
        username,
        email,
        password,
        status,
        role_ids: [roleId]
    };

    const token = localStorage.getItem('dionaea_access_token');

    try {
        const response = await fetch(`${CONFIG.API_BASE}/users/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            showToast('用户创建成功');
            document.getElementById('add-user-modal').classList.add('hidden');
            loadUsersList();
        } else {
            const error = await response.json();
            showToast(`创建失败: ${error.detail || '未知错误'}`, 'error');
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

async function openEditUserModal(userId) {
    try {
        const token = localStorage.getItem('dionaea_access_token');
        const response = await fetch(`${CONFIG.API_BASE}/users/${userId}`, {
             headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Failed to fetch user details');
        const user = await response.json();
        
        // Populate Form
        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-user-version').value = user.version || 0;
        document.getElementById('edit-username').value = user.username;
        document.getElementById('edit-email').value = user.email;
        
        const statusCheckbox = document.getElementById('edit-status');
        statusCheckbox.checked = user.status === 'active';
        document.getElementById('edit-status-label').textContent = user.status === 'active' ? 'Active' : 'Pending';

        // Populate Roles
        const roles = await fetchRoles();
        const roleSelect = document.getElementById('edit-role');
        roleSelect.innerHTML = '';
        roles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.id;
            option.textContent = role.name;
            if (user.roles.some(r => r.id === role.id)) {
                option.selected = true;
            }
            roleSelect.appendChild(option);
        });
        
        document.getElementById('edit-user-modal').classList.remove('hidden');
        
    } catch (e) {
        showToast('获取用户信息失败', 'error');
    }
}

async function handleEditUserSubmit(e) {
    e.preventDefault();
    
    const userId = document.getElementById('edit-user-id').value;
    const version = parseInt(document.getElementById('edit-user-version').value);
    const username = document.getElementById('edit-username').value;
    const email = document.getElementById('edit-email').value;
    const status = document.getElementById('edit-status').checked ? 'active' : 'pending';
    const roleId = parseInt(document.getElementById('edit-role').value);
    
    const payload = {
        username,
        email,
        status,
        role_ids: [roleId],
        version: version
    };
    
    const token = localStorage.getItem('dionaea_access_token');
    
    // Secondary Confirmation
    if (!confirm('确定要保存修改吗？')) return;

    try {
        const response = await fetch(`${CONFIG.API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            showToast('用户修改成功');
            document.getElementById('edit-user-modal').classList.add('hidden');
            loadUsersList(); // Refresh list
        } else {
            const error = await response.json();
            if (response.status === 409) {
                showToast('修改冲突：数据已被其他人修改，请刷新后重试', 'error');
            } else {
                showToast(`修改失败: ${error.detail || '未知错误'}`, 'error');
            }
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

function openDeleteUserModal(user) {
    userToDelete = user;
    document.getElementById('delete-username-display').textContent = user.username; // Note: user.username might be undefined if passing user object directly from data attributes?
    // Wait, in loadUsersList I passed: const user = { id: btn.dataset.id, username: btn.dataset.username };
    // So user.username is correct.
    document.getElementById('delete-user-modal').classList.remove('hidden');
}

async function confirmDeleteUser() {
    if (!userToDelete) return;
    
    const token = localStorage.getItem('dionaea_access_token');
    try {
        const response = await fetch(`${CONFIG.API_BASE}/users/${userToDelete.id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok || response.status === 204) {
            showToast('用户已删除');
            document.getElementById('delete-user-modal').classList.add('hidden');
            loadUsersList();
        } else {
            const error = await response.json();
            showToast(`删除失败: ${error.detail}`, 'error');
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

// --- Node Management Logic ---

let nodesWebSocket = null;
let activeNodes = [];

async function loadNodesList() {
    const tbody = document.getElementById('nodes-table-body');
    tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">加载中...</td></tr>';
    
    try {
        const token = localStorage.getItem('dionaea_access_token');
        const response = await fetch(`${CONFIG.API_BASE}/nodes/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) throw new Error('Failed to fetch nodes');
        
        const nodes = await response.json();
        activeNodes = nodes;
        renderNodesTable(nodes);
        updateNodeStats(nodes);
        renderNodeCharts(nodes);
        
        // Connect WebSocket if not connected
        if (!nodesWebSocket || nodesWebSocket.readyState !== WebSocket.OPEN) {
            connectNodesWebSocket();
        }
        
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-error">加载失败</td></tr>';
    }
}

function renderNodesTable(nodes) {
    const tbody = document.getElementById('nodes-table-body');
    tbody.innerHTML = '';
    
    if (nodes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">暂无节点</td></tr>';
        return;
    }

    nodes.forEach(node => {
        const tr = document.createElement('tr');
        tr.id = `node-row-${node.id}`;
        
        const statusColor = node.status === 'online' ? 'bg-green-100 text-green-800' : 
                          (node.status === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800');
        
        const cpuColor = node.cpu_usage > 80 ? 'text-red-600 font-bold' : 'text-gray-900';
        
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${node.name}</div>
                <div class="text-xs text-gray-500">${node.group || 'Default'}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">${node.ip_address}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColor}">
                    ${node.status.toUpperCase()}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm ${cpuColor}">
                ${node.cpu_usage.toFixed(1)}%
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${node.last_seen ? new Date(node.last_seen).toLocaleString() : 'Never'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button class="text-error hover:text-red-700 btn-delete-node" onclick="deleteNode(${node.id}, '${node.name}')">删除</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function updateNodeStats(nodes) {
    const total = nodes.length;
    const online = nodes.filter(n => n.status === 'online').length;
    const offline = nodes.filter(n => n.status === 'offline').length;
    const warning = nodes.filter(n => n.cpu_usage > 80).length; // Or use status 'warning' if implemented
    
    document.getElementById('nodes-total').textContent = total;
    document.getElementById('nodes-online').textContent = online;
    document.getElementById('nodes-offline').textContent = offline;
    document.getElementById('nodes-warning').textContent = warning;
}

function connectNodesWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use the API_BASE but replace http with ws and remove /api/v1 prefix if needed, or just append ws path
    // CONFIG.API_BASE is http://localhost:8001/api/v1
    const wsUrl = CONFIG.API_BASE.replace('http', 'ws') + '/nodes/ws';
    
    nodesWebSocket = new WebSocket(wsUrl);
    
    nodesWebSocket.onopen = () => {
        console.log('Nodes WebSocket Connected');
    };
    
    nodesWebSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'update') {
            // Update local state
            const index = activeNodes.findIndex(n => n.id === data.node_id);
            if (index !== -1) {
                activeNodes[index] = { ...activeNodes[index], ...data };
                // Re-render (or optimize to update specific row)
                renderNodesTable(activeNodes);
                updateNodeStats(activeNodes);
            }
        } else if (data.type === 'alert') {
            showToast(data.message, 'error');
        }
    };
    
    nodesWebSocket.onclose = () => {
        console.log('Nodes WebSocket Disconnected, retrying in 5s...');
        setTimeout(connectNodesWebSocket, 5000);
    };
}

function setupNodeListeners() {
    // Add Node Button
    const btnAdd = document.getElementById('btn-add-node');
    if (btnAdd) {
        btnAdd.addEventListener('click', () => {
            document.getElementById('add-node-form').reset();
            document.getElementById('add-node-modal').classList.remove('hidden');
        });
    }
    
    // Close Modal
    const btnClose = document.getElementById('close-add-node-modal');
    if (btnClose) {
        btnClose.addEventListener('click', () => {
            document.getElementById('add-node-modal').classList.add('hidden');
        });
    }
    
    const btnCancel = document.getElementById('cancel-add-node');
    if (btnCancel) {
        btnCancel.addEventListener('click', () => {
            document.getElementById('add-node-modal').classList.add('hidden');
        });
    }
    
    // Submit Form
    const form = document.getElementById('add-node-form');
    if (form) {
        form.addEventListener('submit', handleAddNodeSubmit);
    }

    // Search
    const searchInput = document.getElementById('search-node');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = activeNodes.filter(n => 
                n.name.toLowerCase().includes(term) || 
                n.ip_address.includes(term)
            );
            renderNodesTable(filtered);
        });
    }
}

async function handleAddNodeSubmit(e) {
    e.preventDefault();
    
    const name = document.getElementById('node-name').value;
    const ip = document.getElementById('node-ip').value;
    const port = parseInt(document.getElementById('node-port').value);
    const group = document.getElementById('node-group').value;
    
    // Basic IP validation
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/;
    
    if (!ipRegex.test(ip)) {
        showToast('请输入有效的IP地址', 'error');
        return;
    }

    const payload = {
        name,
        ip_address: ip,
        port,
        group,
        is_active: true
    };
    
    const token = localStorage.getItem('dionaea_access_token');
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/nodes/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            showToast('节点添加成功');
            document.getElementById('add-node-modal').classList.add('hidden');
            loadNodesList();
        } else {
            const error = await response.json();
            showToast(`添加失败: ${error.detail}`, 'error');
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

async function deleteNode(id, name) {
    if (!confirm(`确定要删除节点 "${name}" 吗？`)) return;
    
    const token = localStorage.getItem('dionaea_access_token');
    try {
        const response = await fetch(`${CONFIG.API_BASE}/nodes/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok || response.status === 204) {
            showToast('节点已删除');
            loadNodesList();
        } else {
            showToast('删除失败', 'error');
        }
    } catch (e) {
        showToast('请求失败', 'error');
    }
}

let chartNodeStatus = null;
let chartNodeGroup = null;

function renderNodeCharts(nodes) {
    const statusCounts = { online: 0, offline: 0, warning: 0 };
    const groupCounts = {};

    nodes.forEach(n => {
        statusCounts[n.status] = (statusCounts[n.status] || 0) + 1;
        const g = n.group || 'default';
        groupCounts[g] = (groupCounts[g] || 0) + 1;
    });

    // 1. Status Chart
    if (!chartNodeStatus) chartNodeStatus = echarts.init(document.getElementById('chart-node-status'));
    chartNodeStatus.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0 },
        series: [{
            name: 'Status',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: { show: false, position: 'center' },
            emphasis: {
                label: { show: true, fontSize: '20', fontWeight: 'bold' }
            },
            data: [
                { value: statusCounts.online, name: 'Online', itemStyle: { color: '#52c41a' } },
                { value: statusCounts.offline, name: 'Offline', itemStyle: { color: '#ff4d4f' } },
                { value: statusCounts.warning, name: 'Warning', itemStyle: { color: '#faad14' } }
            ]
        }]
    });

    // 2. Group Chart
    if (!chartNodeGroup) chartNodeGroup = echarts.init(document.getElementById('chart-node-group'));
    chartNodeGroup.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: Object.keys(groupCounts) },
        yAxis: { type: 'value' },
        series: [{
            data: Object.values(groupCounts),
            type: 'bar',
            itemStyle: { color: '#1890ff' },
            label: { show: true, position: 'top' }
        }]
    });
    
    window.addEventListener('resize', () => {
        chartNodeStatus && chartNodeStatus.resize();
        chartNodeGroup && chartNodeGroup.resize();
    });
}
