// Admin Dashboard JavaScript

// Load all data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadResults();
    loadVoters();
    loadBlockchain();
});

// Load voting results
async function loadResults() {
    try {
        const response = await fetch('/api/results');
        const data = await response.json();
        
        document.getElementById('totalVotes').textContent = data.total_votes;
        
        const resultsTable = document.getElementById('resultsTable');
        
        if (data.results.length === 0) {
            resultsTable.innerHTML = '<p>No votes cast yet</p>';
            return;
        }
        
        let tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Candidate</th>
                        <th>Party</th>
                        <th>Votes</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.results.forEach((result, index) => {
            const percentage = data.total_votes > 0 
                ? ((result.votes / data.total_votes) * 100).toFixed(1) 
                : 0;
            
            tableHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${result.name}</td>
                    <td>${result.party || 'Independent'}</td>
                    <td>${result.votes}</td>
                    <td>${percentage}%</td>
                </tr>
            `;
        });
        
        tableHTML += '</tbody></table>';
        resultsTable.innerHTML = tableHTML;
        
        document.getElementById('totalCandidates').textContent = data.results.length;
        
    } catch (error) {
        console.error('Error loading results:', error);
        document.getElementById('resultsTable').innerHTML = '<p>Error loading results</p>';
    }
}

// Load registered voters
async function loadVoters() {
    try {
        const response = await fetch('/api/voters');
        const data = await response.json();
        
        document.getElementById('totalVoters').textContent = data.total_voters;
        
        const votersTable = document.getElementById('votersTable');
        
        if (data.voters.length === 0) {
            votersTable.innerHTML = '<p>No voters registered yet</p>';
            return;
        }
        
        let tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Voter ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Registered At</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.voters.forEach(voter => {
            const status = voter.has_voted 
                ? '<span style="color: green;">✓ Voted</span>' 
                : '<span style="color: orange;">⏳ Not Voted</span>';
            
            const regDate = voter.registered_at 
                ? new Date(voter.registered_at).toLocaleString() 
                : 'N/A';
            
            tableHTML += `
                <tr>
                    <td>${voter.voter_id}</td>
                    <td>${voter.name}</td>
                    <td>${status}</td>
                    <td>${regDate}</td>
                </tr>
            `;
        });
        
        tableHTML += '</tbody></table>';
        votersTable.innerHTML = tableHTML;
        
    } catch (error) {
        console.error('Error loading voters:', error);
        document.getElementById('votersTable').innerHTML = '<p>Error loading voters</p>';
    }
}

// Load blockchain data
async function loadBlockchain() {
    try {
        const response = await fetch('/api/chain');
        const data = await response.json();
        
        document.getElementById('blockchainLength').textContent = data.length;
        
        const statusElement = document.getElementById('blockchainStatus');
        const blockchainStatusDiv = statusElement.closest('.blockchain-status');
        
        if (data.is_valid) {
            statusElement.textContent = '✓ Valid and Secure';
            blockchainStatusDiv.classList.remove('invalid');
        } else {
            statusElement.textContent = '✗ Invalid - Chain Compromised';
            blockchainStatusDiv.classList.add('invalid');
        }
        
        const blockchainData = document.getElementById('blockchainData');
        blockchainData.innerHTML = '';
        
        // Reverse to show latest first
        const reversedChain = [...data.chain].reverse();
        
        reversedChain.forEach(block => {
            const blockDiv = document.createElement('div');
            blockDiv.className = 'block';
            
            const timestamp = new Date(block.timestamp).toLocaleString();
            
            let dataContent = '';
            if (block.data.message) {
                dataContent = `<p><strong>Message:</strong> ${block.data.message}</p>`;
            } else if (block.data.candidate_id) {
                dataContent = `
                    <p><strong>Voter ID:</strong> ${block.data.voter_id}</p>
                    <p><strong>Candidate:</strong> ${block.data.candidate_name} (${block.data.candidate_id})</p>
                    <p><strong>Vote Time:</strong> ${new Date(block.data.timestamp).toLocaleString()}</p>
                `;
            }
            
            blockDiv.innerHTML = `
                <div class="block-header">
                    <span class="block-index">Block #${block.index}</span>
                    <span class="block-time">${timestamp}</span>
                </div>
                <div class="block-data">
                    ${dataContent}
                </div>
                <div class="block-hash">
                    <strong>Hash:</strong> ${block.hash}
                </div>
                <div class="block-hash" style="margin-top: 5px;">
                    <strong>Previous Hash:</strong> ${block.previous_hash}
                </div>
            `;
            
            blockchainData.appendChild(blockDiv);
        });
        
    } catch (error) {
        console.error('Error loading blockchain:', error);
        document.getElementById('blockchainData').innerHTML = '<p>Error loading blockchain</p>';
    }
}

// Auto-refresh every 10 seconds
setInterval(() => {
    loadResults();
    loadVoters();
    loadBlockchain();
}, 10000);
