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
    // permission: null means accessible to all authenticated users
    // permission: 'xxx' means requires that permission code (or super_admin role)
    const menuItems = [
        { id: 'nav-dashboard', label: '仪表盘', icon: 'fas fa-tachometer-alt', view: 'view-dashboard', permission: null },
        { id: 'nav-users', label: '用户管理', icon: 'fas fa-users', view: 'view-users', permission: 'user:list' },
        { id: 'nav-roles', label: '角色权限', icon: 'fas fa-user-tag', view: 'view-roles', permission: 'role:list' },
        { id: 'nav-monitor', label: '系统监控', icon: 'fas fa-server', view: 'view-monitor', permission: 'system:monitor' },
        { id: 'nav-stats', label: '数据统计', icon: 'fas fa-chart-bar', view: 'view-stats', permission: 'data:stats' },
        { id: 'nav-settings', label: '系统设置', icon: 'fas fa-cogs', view: 'view-settings', permission: null }, // Everyone can see settings (maybe profile settings)
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
            link.className = 'group flex items-center px-4 py-3 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50 hover:text-primary transition-colors mb-1';
            if (item.id === 'nav-dashboard') link.classList.add('bg-blue-50', 'text-primary'); // Active by default
            
            link.innerHTML = `<i class="${item.icon} mr-3 text-gray-400 group-hover:text-primary transition-colors"></i> ${item.label}`;
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
            'view-users': '用户管理',
            'view-roles': '角色权限管理',
            'view-monitor': '系统监控',
            'view-stats': '数据统计',
            'view-settings': '系统设置'
        };
        document.getElementById('page-title').textContent = titleMap[viewId] || '仪表盘';
        
        // Load data if needed
        if (viewId === 'view-users') {
            loadUsersList();
        }
    }

    // Update Sidebar Active State
    document.querySelectorAll('#sidebar-menu a').forEach(a => {
        a.classList.remove('bg-blue-50', 'text-primary');
        a.classList.add('text-gray-600');
    });
    if (activeLink) {
        activeLink.classList.remove('text-gray-600');
        activeLink.classList.add('bg-blue-50', 'text-primary');
    }
}

async function loadDashboardStats() {
    // Only fetch if user has permission
    // For demo, just mock or fetch minimal
    // Update stats
    try {
        const users = await fetchUsers();
        document.getElementById('stat-users').textContent = users.total || 0;
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
            return;
        }

        data.items.forEach(user => {
            const roleNames = user.roles.map(r => r.name).join(', ') || '-';
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
                    <button class="text-primary hover:text-primary-hover mr-2">编辑</button>
                    <button class="text-error hover:text-red-700">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-error">加载失败</td></tr>';
    }
}

// UI Interactions
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
}
