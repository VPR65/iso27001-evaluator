/**
 * AI Status Monitor - On-Demand AI with Automatic Fallback
 * 
 * Polls the AI status endpoint every 5 seconds and updates the UI.
 * Shows visual indicators for:
 * - 🟢 Local AI (Ollama)
 * - 🟡 External AI (NVIDIA)
 * - 🔴 No AI Available
 */

// Configuration
const AI_STATUS_POLL_INTERVAL = 5000; // 5 seconds
const AI_STATUS_ENDPOINT = '/api/ai/status/detailed';

// State
let currentAIStatus = null;
let aiStatusPolling = false;

/**
 * Initialize AI status monitoring
 */
function initAIStatusMonitor() {
    // Create status indicator in sidebar
    createSidebarIndicator();
    
    // Initial check
    checkAIStatus();
    
    // Start polling
    startAIStatusPolling();
}

/**
 * Create sidebar indicator (always visible)
 */
function createSidebarIndicator() {
    const sidebar = document.querySelector('.sidebar nav') || document.querySelector('.sidebar');
    if (!sidebar) return;
    
    const indicator = document.createElement('div');
    indicator.id = 'ai-status-indicator';
    indicator.className = 'ai-status-badge';
    indicator.innerHTML = `
        <div class="ai-status-content">
            <span class="ai-status-icon" id="ai-status-icon">⏳</span>
            <span class="ai-status-text" id="ai-status-text">Cargando IA...</span>
            <span class="ai-status-model" id="ai-status-model"></span>
        </div>
        <div class="ai-status-details" id="ai-status-details" style="display: none;">
            <div class="ai-detail-row">
                <strong>Proveedor:</strong> <span id="ai-detail-provider">-</span>
            </div>
            <div class="ai-detail-row">
                <strong>Modelo:</strong> <span id="ai-detail-model">-</span>
            </div>
            <div class="ai-detail-row">
                <strong>Privacidad:</strong> <span id="ai-detail-privacy">-</span>
            </div>
            <div class="ai-detail-row" id="ai-instructions" style="display: none;">
                <strong>Instrucciones:</strong> <span id="ai-instructions-text">-</span>
            </div>
            <button onclick="toggleAIStatusDetails()" style="margin-top: 0.5rem; font-size: 0.8rem;">
                ▲ Ocultar detalles
            </button>
        </div>
    `;
    
    // Insert after navigation items
    const navItems = sidebar.querySelectorAll('.nav-item');
    if (navItems.length > 0) {
        navItems[navItems.length - 1].after(indicator);
    } else {
        sidebar.appendChild(indicator);
    }
    
    // Add click handler for details
    indicator.addEventListener('click', function(e) {
        if (!e.target.closest('button')) {
            toggleAIStatusDetails();
        }
    });
}

/**
 * Toggle AI status details visibility
 */
function toggleAIStatusDetails() {
    const details = document.getElementById('ai-status-details');
    if (details) {
        details.style.display = details.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Check AI status from server
 */
async function checkAIStatus() {
    try {
        const response = await fetch(AI_STATUS_ENDPOINT, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const status = await response.json();
            updateAIStatusUI(status);
            currentAIStatus = status;
        } else {
            console.error('AI status check failed:', response.status);
        }
    } catch (error) {
        console.error('AI status check error:', error);
        // Don't update UI on error, keep last known state
    }
}

/**
 * Update UI with AI status
 */
function updateAIStatusUI(status) {
    // Update sidebar indicator
    const iconEl = document.getElementById('ai-status-icon');
    const textEl = document.getElementById('ai-status-text');
    const modelEl = document.getElementById('ai-status-model');
    
    if (iconEl) iconEl.textContent = status.icon || '⏳';
    if (textEl) textEl.textContent = status.message || 'Desconocido';
    if (modelEl) modelEl.textContent = status.model ? `(${status.model})` : '';
    
    // Update details
    const providerEl = document.getElementById('ai-detail-provider');
    const modelDetailEl = document.getElementById('ai-detail-model');
    const privacyEl = document.getElementById('ai-detail-privacy');
    const instructionsEl = document.getElementById('ai-instructions');
    const instructionsTextEl = document.getElementById('ai-instructions-text');
    
    if (providerEl) providerEl.textContent = status.provider || 'Desconocido';
    if (modelDetailEl) modelDetailEl.textContent = status.model || 'N/A';
    if (privacyEl) privacyEl.textContent = status.privacy || 'N/A';
    
    if (instructionsEl && instructionsTextEl && status.instructions) {
        instructionsEl.style.display = 'block';
        instructionsTextEl.textContent = status.instructions;
    } else if (instructionsEl) {
        instructionsEl.style.display = 'none';
    }
    
    // Add CSS class based on status
    const badge = document.getElementById('ai-status-indicator');
    if (badge) {
        badge.className = `ai-status-badge ai-status-${status.status || 'unknown'}`;
    }
    
    // Dispatch event for other components to react
    window.dispatchEvent(new CustomEvent('ai-status-changed', { detail: status }));
}

/**
 * Start polling AI status
 */
function startAIStatusPolling() {
    if (aiStatusPolling) return;
    
    aiStatusPolling = true;
    setInterval(checkAIStatus, AI_STATUS_POLL_INTERVAL);
}

/**
 * Check if AI is available for a specific action
 * Returns true if AI is available, false otherwise
 */
function isAIAvailable() {
    return currentAIStatus ? currentAIStatus.available : false;
}

/**
 * Get current AI provider
 */
function getCurrentAIProvider() {
    return currentAIStatus ? currentAIStatus.provider : 'none';
}

/**
 * Show AI status in evaluation pages
 */
function showAIStatusInEvaluation() {
    const evaluationHeader = document.querySelector('.evaluation-header') || 
                            document.querySelector('.page-header') ||
                            document.querySelector('h1')?.parentElement;
    
    if (evaluationHeader && !document.querySelector('.evaluation-ai-status')) {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'evaluation-ai-status';
        statusDiv.innerHTML = `
            <div class="ai-status-inline">
                <span id="eval-ai-icon">⏳</span>
                <span id="eval-ai-text">Verificando IA...</span>
            </div>
        `;
        evaluationHeader.appendChild(statusDiv);
        
        // Update with current status
        if (currentAIStatus) {
            updateEvaluationAIStatus(currentAIStatus);
        }
    }
}

/**
 * Update evaluation page AI status
 */
function updateEvaluationAIStatus(status) {
    const iconEl = document.getElementById('eval-ai-icon');
    const textEl = document.getElementById('eval-ai-text');
    
    if (iconEl) iconEl.textContent = status.icon || '⏳';
    if (textEl) textEl.textContent = status.message || 'Desconocido';
}

// Listen for AI status changes
window.addEventListener('ai-status-changed', (event) => {
    const status = event.detail;
    updateEvaluationAIStatus(status);
    
    // If no AI available, show message
    if (!status.available) {
        showAINotAvailableMessage(status);
    }
});

/**
 * Show message when AI is not available
 */
function showAINotAvailableMessage(status) {
    const container = document.querySelector('.evaluation-content') || 
                     document.querySelector('.main-content') ||
                     document.querySelector('main');
    
    if (container && !document.querySelector('.ai-not-available-alert')) {
        const alert = document.createElement('div');
        alert.className = 'ai-not-available-alert alert alert-warning';
        alert.innerHTML = `
            <strong>⚠️ IA No Disponible</strong>
            <p>${status.instructions || 'Ollama no está ejecutándose. Para usar IA local, ejecuta: ollama serve'}</p>
            <p>Puedes continuar la evaluación manualmente. El sistema guardará tu trabajo para cuando la IA esté disponible.</p>
        `;
        container.insertBefore(alert, container.firstChild);
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAIStatusMonitor);
} else {
    initAIStatusMonitor();
}

// Export functions for use in other scripts
window.aiStatus = {
    isAvailable: isAIAvailable,
    getProvider: getCurrentAIProvider,
    getStatus: () => currentAIStatus,
    checkNow: checkAIStatus
};
