// 3D Admin Dashboard JavaScript
let scene, camera, renderer, blocks = [];
let authToken = null;

// Check authentication on load
window.addEventListener('DOMContentLoaded', () => {
    authToken = localStorage.getItem('admin_token');
    if (!authToken) {
        window.location.href = '/admin/login';
        return;
    }
    
    init3DBlockchain();
    loadDashboardData();
    
    // Auto-refresh every 10 seconds
    setInterval(loadDashboardData, 10000);
});

// Logout function
function logout() {
    localStorage.removeItem('admin_token');
    window.location.href = '/admin/login';
}

// Section navigation
function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(`${sectionName}-section`).classList.remove('hidden');
    
    // Load section data
    if (sectionName === 'elections') loadElections();
    if (sectionName === 'candidates') loadCandidates();
    if (sectionName === 'voters') loadVoters();
    if (sectionName === 'blockchain') loadBlockchainData();
    if (sectionName === 'results') loadResults();
}

// API request helper with JWT
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
        ...options.headers
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        logout();
        return;
    }
    
    return response;
}

// ========== 3D BLOCKCHAIN VISUALIZATION ==========
function init3DBlockchain() {
    const container = document.getElementById('blockchain3d');
    if (!container) return;
    
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    
    // Camera
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 15;
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const pointLight = new THREE.PointLight(0x00d4ff, 1, 100);
    pointLight.position.set(10, 10, 10);
    scene.add(pointLight);
    
    // Create initial blocks
    createBlockchain3D();
    
    // Animation loop
    animate3D();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}

function createBlockchain3D() {
    // Clear existing blocks
    blocks.forEach(block => scene.remove(block));
    blocks = [];
    
    // Create blocks based on blockchain data
    const blockCount = Math.max(5, Math.min(10, parseInt(document.getElementById('stat-blocks')?.textContent || 5)));
    
    for (let i = 0; i < blockCount; i++) {
        const geometry = new THREE.BoxGeometry(2, 2, 2);
        const material = new THREE.MeshPhongMaterial({
            color: 0x667eea,
            emissive: 0x00d4ff,
            emissiveIntensity: 0.2,
            transparent: true,
            opacity: 0.8
        });
        
        const cube = new THREE.Mesh(geometry, material);
        cube.position.x = (i - blockCount / 2) * 3;
        cube.position.y = Math.sin(i * 0.5) * 2;
        
        // Add edges
        const edges = new THREE.EdgesGeometry(geometry);
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0x00d4ff });
        const wireframe = new THREE.LineSegments(edges, lineMaterial);
        cube.add(wireframe);
        
        scene.add(cube);
        blocks.push(cube);
        
        // Add connecting lines
        if (i > 0) {
            const points = [
                blocks[i - 1].position,
                cube.position
            ];
            const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(lineGeometry, new THREE.LineBasicMaterial({ color: 0x00d4ff }));
            scene.add(line);
        }
    }
}

function animate3D() {
    requestAnimationFrame(animate3D);
    
    // Rotate blocks
    blocks.forEach((block, index) => {
        block.rotation.x += 0.005;
        block.rotation.y += 0.005;
        block.position.y = Math.sin(Date.now() * 0.001 + index) * 0.5;
    });
    
    // Rotate camera slowly
    camera.position.x = Math.sin(Date.now() * 0.0002) * 15;
    camera.position.z = Math.cos(Date.now() * 0.0002) * 15;
    camera.lookAt(0, 0, 0);
    
    renderer.render(scene, camera);
}

// ========== DATA LOADING ==========
async function loadDashboardData() {
    try {
        const [stats, blockchain, results] = await Promise.all([
            apiRequest('/api/admin/stats').then(r => r.json()),
            apiRequest('/api/admin/blockchain').then(r => r.json()),
            apiRequest('/api/admin/results').then(r => r.json())
        ]);
        
        // Update stats
        document.getElementById('stat-votes').textContent = stats.total_votes || 0;
        document.getElementById('stat-voters').textContent = stats.total_voters || 0;
        document.getElementById('stat-candidates').textContent = stats.total_candidates || 0;
        document.getElementById('stat-blocks').textContent = stats.blockchain_blocks || 0;
        
        // Update charts
        updateCharts(results, stats);
        
        // Update 3D visualization
        createBlockchain3D();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// ========== CHARTS ==========
let resultsChart, participationChart;

function updateCharts(results, stats) {
    // Results Chart
    const ctx1 = document.getElementById('resultsChart');
    if (ctx1 && results.results) {
        if (resultsChart) resultsChart.destroy();
        
        resultsChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: results.results.map(r => r.name),
                datasets: [{
                    label: 'Votes',
                    data: results.results.map(r => r.votes),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(0, 212, 255, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
                    }
                }
            }
        });
    }
    
    // Participation Chart
    const ctx2 = document.getElementById('participationChart');
    if (ctx2 && stats) {
        if (participationChart) participationChart.destroy();
        
        const voted = stats.voters_who_voted || 0;
        const notVoted = (stats.total_voters || 0) - voted;
        
        participationChart = new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Voted', 'Not Voted'],
                datasets: [{
                    data: [voted, notVoted],
                    backgroundColor: [
                        'rgba(0, 212, 255, 0.8)',
                        'rgba(118, 75, 162, 0.5)'
                    ],
                    borderColor: [
                        'rgba(0, 212, 255, 1)',
                        'rgba(118, 75, 162, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: 'rgba(255, 255, 255, 0.7)' }
                    }
                }
            }
        });
    }
}

// ========== ELECTIONS MANAGEMENT ==========
async function loadElections() {
    const response = await apiRequest('/api/admin/elections');
    const data = await response.json();
    
    const container = document.getElementById('electionsList');
    if (data.elections.length === 0) {
        container.innerHTML = '<p class="text-gray-400">No elections created yet.</p>';
        return;
    }
    
    container.innerHTML = data.elections.map(e => `
        <div class="glass p-4 rounded-xl mb-4">
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="text-xl font-bold">${e.title}</h3>
                    <p class="text-gray-400 text-sm mt-1">${e.description || ''}</p>
                    <div class="mt-2 text-sm">
                        <span class="text-gray-500">Start:</span> ${new Date(e.start_time).toLocaleString()}
                        <span class="ml-4 text-gray-500">End:</span> ${new Date(e.end_time).toLocaleString()}
                    </div>
                    <span class="inline-block mt-2 px-3 py-1 rounded-full text-xs ${e.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}">
                        ${e.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="flex space-x-2">
                    <button onclick="deleteElection(${e.id})" class="px-3 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ========== CANDIDATES MANAGEMENT ==========
async function loadCandidates() {
    const response = await apiRequest('/api/admin/candidates');
    const data = await response.json();
    
    const container = document.getElementById('candidatesList');
    if (data.candidates.length === 0) {
        container.innerHTML = '<p class="text-gray-400">No candidates added yet.</p>';
        return;
    }
    
    container.innerHTML = data.candidates.map(c => `
        <div class="glass p-4 rounded-xl mb-4 flex justify-between items-center">
            <div>
                <h3 class="text-lg font-bold">${c.name}</h3>
                <p class="text-sm text-gray-400">${c.party || 'Independent'}</p>
                <p class="text-xs text-gray-500 mt-1">ID: ${c.candidate_id}</p>
            </div>
            <div class="flex space-x-2">
                <button onclick="deleteCandidate('${c.candidate_id}')" class="px-3 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// ========== VOTERS MANAGEMENT ==========
async function loadVoters() {
    const response = await apiRequest('/api/admin/voters');
    const data = await response.json();
    
    const container = document.getElementById('votersList');
    if (data.voters.length === 0) {
        container.innerHTML = '<p class="text-gray-400">No voters registered yet.</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="w-full">
            <thead>
                <tr class="border-b border-gray-700">
                    <th class="text-left py-3 px-4">Voter ID</th>
                    <th class="text-left py-3 px-4">Name</th>
                    <th class="text-left py-3 px-4">Status</th>
                    <th class="text-left py-3 px-4">Face Data</th>
                    <th class="text-left py-3 px-4">Actions</th>
                </tr>
            </thead>
            <tbody>
                ${data.voters.map(v => `
                    <tr class="border-b border-gray-800 hover:bg-gray-800/50">
                        <td class="py-3 px-4">${v.voter_id}</td>
                        <td class="py-3 px-4">${v.name}</td>
                        <td class="py-3 px-4">
                            <span class="${v.has_voted ? 'text-green-400' : 'text-yellow-400'}">
                                ${v.has_voted ? '✓ Voted' : '⏳ Not Voted'}
                            </span>
                        </td>
                        <td class="py-3 px-4">
                            <span class="${v.has_face_data ? 'text-green-400' : 'text-red-400'}">
                                ${v.has_face_data ? '✓ Yes' : '✗ No'}
                            </span>
                        </td>
                        <td class="py-3 px-4">
                            <button onclick="deleteVoter('${v.voter_id}')" class="px-2 py-1 bg-red-500/20 text-red-400 rounded text-sm hover:bg-red-500/30">
                                Delete
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ========== BLOCKCHAIN DATA ==========
async function loadBlockchainData() {
    const response = await apiRequest('/api/admin/blockchain');
    const data = await response.json();
    
    const container = document.getElementById('blockchainData');
    container.innerHTML = `
        <div class="glass rounded-2xl p-4 mb-4">
            <p class="text-lg">
                <span class="text-gray-400">Status:</span> 
                <span class="${data.is_valid ? 'text-green-400' : 'text-red-400'}">
                    ${data.is_valid ? '✓ Valid' : '✗ Invalid'}
                </span>
            </p>
            <p class="text-sm text-gray-400 mt-2">Total Blocks: ${data.length}</p>
        </div>
        ${data.chain.reverse().map(block => `
            <div class="glass rounded-xl p-6 mb-4">
                <div class="flex justify-between mb-4">
                    <h3 class="text-xl font-bold text-accent">Block #${block.index}</h3>
                    <span class="text-gray-400 text-sm">${new Date(block.timestamp).toLocaleString()}</span>
                </div>
                <div class="bg-gray-900/50 rounded-lg p-4 mb-3">
                    <p class="text-sm text-gray-400">Data:</p>
                    <pre class="text-xs mt-2 text-gray-300 overflow-x-auto">${JSON.stringify(block.data, null, 2)}</pre>
                </div>
                <div class="text-xs space-y-2">
                    <p><span class="text-gray-500">Hash:</span> <span class="text-accent font-mono">${block.hash}</span></p>
                    <p><span class="text-gray-500">Previous Hash:</span> <span class="text-purple-400 font-mono">${block.previous_hash}</span></p>
                </div>
            </div>
        `).join('')}
    `;
}

// ========== RESULTS ==========
async function loadResults() {
    const response = await apiRequest('/api/admin/results');
    const data = await response.json();
    
    const container = document.getElementById('resultsData');
    container.innerHTML = `
        <h3 class="text-2xl font-bold mb-4">Total Votes: ${data.total_votes}</h3>
        <table class="w-full">
            <thead>
                <tr class="border-b border-gray-700">
                    <th class="text-left py-3 px-4">Rank</th>
                    <th class="text-left py-3 px-4">Candidate</th>
                    <th class="text-left py-3 px-4">Party</th>
                    <th class="text-left py-3 px-4">Votes</th>
                    <th class="text-left py-3 px-4">Percentage</th>
                </tr>
            </thead>
            <tbody>
                ${data.results.map((r, i) => {
                    const percentage = data.total_votes > 0 ? ((r.votes / data.total_votes) * 100).toFixed(1) : 0;
                    return `
                        <tr class="border-b border-gray-800">
                            <td class="py-3 px-4 font-bold">#${i + 1}</td>
                            <td class="py-3 px-4">${r.name}</td>
                            <td class="py-3 px-4">${r.party || 'Independent'}</td>
                            <td class="py-3 px-4 font-bold text-accent">${r.votes}</td>
                            <td class="py-3 px-4">
                                <div class="flex items-center">
                                    <div class="w-32 bg-gray-700 rounded-full h-2 mr-2">
                                        <div class="gradient-bg h-2 rounded-full" style="width: ${percentage}%"></div>
                                    </div>
                                    <span>${percentage}%</span>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

// ========== DELETE FUNCTIONS ==========
async function deleteElection(id) {
    if (!confirm('Are you sure you want to delete this election?')) return;
    await apiRequest(`/api/admin/elections/${id}`, { method: 'DELETE' });
    loadElections();
}

async function deleteCandidate(id) {
    if (!confirm('Are you sure you want to delete this candidate?')) return;
    await apiRequest(`/api/admin/candidates/${id}`, { method: 'DELETE' });
    loadCandidates();
    loadDashboardData();
}

async function deleteVoter(id) {
    if (!confirm('Are you sure you want to delete this voter?')) return;
    await apiRequest(`/api/admin/voters/${id}`, { method: 'DELETE' });
    loadVoters();
    loadDashboardData();
}

// Placeholder modal functions (to be implemented)
function showCreateElectionModal() {
    const title = prompt('Election Title:');
    const description = prompt('Description:');
    if (title) {
        const start = new Date();
        const end = new Date(start.getTime() + 7 * 24 * 60 * 60 * 1000);
        apiRequest('/api/admin/elections', {
            method: 'POST',
            body: JSON.stringify({
                title, description,
                start_time: start.toISOString(),
                end_time: end.toISOString()
            })
        }).then(() => loadElections());
    }
}

function showCreateCandidateModal() {
    const id = prompt('Candidate ID:');
    const name = prompt('Candidate Name:');
    const party = prompt('Party:');
    if (id && name) {
        apiRequest('/api/admin/candidates', {
            method: 'POST',
            body: JSON.stringify({
                candidate_id: id,
                name, party
            })
        }).then(() => {
            loadCandidates();
            loadDashboardData();
        });
    }
}

// Sidebar toggle for mobile
document.getElementById('sidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('-translate-x-full');
});
