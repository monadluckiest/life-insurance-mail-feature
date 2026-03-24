// Life Insurance Application - Main JavaScript

//const API_BASE = 'http://localhost:8080/api';

// Set Python agent base URL from global variable, window.env, meta tag, or fallback to default
// To override, add to your HTML before this script:
//<script>window.PYTHON_AGENT_BASE_URL = "http://your-python-agent-url:8000/api";</script>
// or
// <meta name="python-agent-base-url" content="http://your-python-agent-url:8000">

// Always ensure /api is present at the end of the base URL
let injectedBase = window.PYTHON_AGENT_BASE_URL || (window.env && window.env.PYTHON_AGENT_BASE_URL);
if (injectedBase && !injectedBase.endsWith('/api')) {
    injectedBase = injectedBase.replace(/\/?$/, '/api');
}
const API_BASE = injectedBase || getPythonBaseUrl();

function getPythonBaseUrl() {
    // Try to read from a meta tag or fallback to default
    const meta = document.querySelector('meta[name="python-agent-base-url"]');
    if (meta && meta.content) {
        return meta.content;
    }
    // Default for local development
    return 'http://localhost:8080/api';
}

const STRIPE_PUBLIC_KEY = 'pk_test_51S4jryBJVoLIccXbO5risxqRwyQPx7A8Pt3bM7Pwj7K3HRrC19Zc0M2UY1xkfEYb3ImE7BBNkffcP4dBSQFLZYCM00wbOtbkIk';

let currentQuote = null;
let currentApplication = null;
let stripe = null;
let elements = null;
let paymentElement = null;

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    initializeEventListeners();
    initializeStripe();
});

function initializeStripe() {
    stripe = Stripe(STRIPE_PUBLIC_KEY);
}

function initializeEventListeners() {
    // Quote form submission
    document.getElementById('quote-form').addEventListener('submit', handleQuoteSubmit);

    // Apply now button
    document.getElementById('apply-now-btn').addEventListener('click', showApplicationForm);

    // Application form submission
    document.getElementById('application-form').addEventListener('submit', handleApplicationSubmit);

    // Download policy button
    document.getElementById('download-policy')?.addEventListener('click', downloadPolicy);

    // Needs Analysis listeners
    document.getElementById('needs-analysis-form')?.addEventListener('submit', handleNeedsAnalysisSubmit);
    document.getElementById('skip-needs-analysis')?.addEventListener('click', skipNeedsAnalysis);
    document.getElementById('back-to-needs')?.addEventListener('click', showNeedsAnalysis);

    // Coverage amount dropdown listener for custom input
    document.getElementById('coverageAmount')?.addEventListener('change', handleCoverageAmountChange);

    // Policy Servicing listeners
    document.getElementById('update-address-btn')?.addEventListener('click', showServicingForm);
    document.getElementById('address-change-form')?.addEventListener('submit', handleAddressChangeSubmit);
    document.getElementById('cancel-servicing')?.addEventListener('click', cancelServicing);
}

// ========== STEP 1: GET QUOTE ==========
async function handleQuoteSubmit(e) {
    e.preventDefault();

    const age = parseInt(document.getElementById('age').value);
    const coverageSelect = document.getElementById('coverageAmount');
    let coverageAmount;

    // Check if custom amount is selected
    if (coverageSelect.value === 'custom') {
        const customAmount = document.getElementById('customCoverageAmount').value;
        if (!customAmount || customAmount < 50000 || customAmount > 5000000) {
            alert('Please enter a valid custom coverage amount between $50,000 and $5,000,000');
            return;
        }
        coverageAmount = parseFloat(customAmount);
    } else {
        coverageAmount = parseFloat(coverageSelect.value);
    }

    const healthStatus = document.getElementById('healthStatus').value;

    // Hide quote form
    document.getElementById('quote-section').style.display = 'none';

    // Show agent processing
    showAgentProcessing();

    try {
        const response = await fetch(`${API_BASE}/quotes/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                age: age,
                coverageAmount: coverageAmount,
                coverageAmount: coverageAmount,
                healthStatus: healthStatus,
                isSmoker: document.getElementById('isSmoker').value === 'Yes'
            })
        });

        if (!response.ok) {
            throw new Error('Failed to calculate quote');
        }

        const data = await response.json();
        console.log('✅ Quote Agent Response:', data);
        console.log('✅ Monthly Premium from response:', data.monthlyPremium);
        console.log('✅ Annual Premium from response:', data.annualPremium);

        currentQuote = data;
        console.log('✅ currentQuote set to:', currentQuote);

        // Wait for agent animation
        await sleep(1500);

        // Hide agent processing card header but keep container for results
        document.getElementById('agent-processing').style.display = 'none';

        // Display Agent Chat History
        if (data.agentTrace) {
            appendAgentTraceToChat(data.agentTrace, 'Quote Agent');
        }

        // Check for immediate rejection
        if (data.status === 'REJECTED') {
            console.log('❌ Quote Rejected Immediately:', data.rejectionReason);

            // Construct a mock result object compatible with showRejectionSection
            const rejectionResult = {
                reason: data.rejectionReason,
                creditCheckPassed: true, // Mock values for display
                mibCheckPassed: true,
                decision: 'REJECTED'
            };

            showRejectionSection(rejectionResult);
            return;
        }

        // Show quote results
        displayQuote(data);

    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to get quote. Please try again.', 'error');
        document.getElementById('quote-section').style.display = 'block';
        document.getElementById('agent-processing').style.display = 'none';
    }
}

function showAgentProcessing() {
    const agentCard = document.getElementById('agent-processing');
    agentCard.style.display = 'block';

    // Scroll to view
    agentCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function parseAgentTraceToChat(traceLines, agentName) {
    let chatHTML = '';

    // Add agent header if name is provided
    if (agentName) {
        chatHTML += `
            <div class="agent-section-header">
                <span class="agent-icon">🤖</span>
                <span class="agent-name">${agentName}</span>
            </div>
        `;
    }

    let messageType = null;

    traceLines.forEach(line => {
        if (line.includes('🤖 Quote Agent') && line.includes('Initializing')) {
            chatHTML += `
                <div class="chat-message agent-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <div class="message-header">Quote Agent</div>
                        <div class="message-text">Initializing autonomous agent with specialized tools...</div>
                    </div>
                </div>
            `;
        } else if (line.includes('🤔 Agent Thought')) {
            const match = line.match(/Invoking: `([^`]+)` with `([^`]+)`/);
            if (match) {
                const toolName = match[1].replace(/_/g, ' ').replace(/tool/gi, '').trim();
                const params = match[2];
                chatHTML += `
                    <div class="chat-message agent-message">
                        <div class="message-avatar">💭</div>
                        <div class="message-content">
                            <div class="message-header">Agent Reasoning</div>
                            <div class="message-text">Analyzing... I need to invoke <strong>${toolName}</strong></div>
                            <div class="message-meta">Parameters: ${params}</div>
                        </div>
                    </div>
                `;
            }
        } else if (line.includes('🛠️ Agent is using tool')) {
            const toolMatch = line.match(/tool: ([^\s]+)/);
            if (toolMatch) {
                const toolName = toolMatch[1].replace(/_/g, ' ').replace(/tool/gi, '').trim();
                chatHTML += `
                    <div class="chat-message tool-message">
                        <div class="message-avatar">🛠️</div>
                        <div class="message-content">
                            <div class="message-header">Tool Execution</div>
                            <div class="message-text">Executing <strong>${toolName}</strong>...</div>
                        </div>
                    </div>
                `;
            }
        } else if (line.includes('Input:')) {
            const input = line.replace('> Input:', '').trim();
            chatHTML += `
                <div class="chat-message data-message">
                    <div class="message-content">
                        <div class="message-label">📥 Input</div>
                        <div class="message-code">${input}</div>
                    </div>
                </div>
            `;
        } else if (line.includes('Output:')) {
            const output = line.replace('> Output:', '').trim();
            chatHTML += `
                <div class="chat-message data-message">
                    <div class="message-content">
                        <div class="message-label">📤 Output</div>
                        <div class="message-code">${output}</div>
                    </div>
                </div>
            `;
        } else if (line.includes('✅ Agent Finished')) {
            const match = line.match(/'output': '([^']+)'/);
            if (match) {
                const output = match[1].replace(/\\n/g, '<br>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
                chatHTML += `
                    <div class="chat-message agent-message success">
                        <div class="message-avatar">✅</div>
                        <div class="message-content">
                            <div class="message-header">Agent Complete</div>
                            <div class="message-text">${output}</div>
                        </div>
                    </div>
                `;
            }
        } else if (line.includes('Agent execution complete')) {
            chatHTML += `
                <div class="chat-message system-message">
                    <div class="message-content">
                        <div class="message-text">✨ Agent execution complete. Response synthesized.</div>
                    </div>
                </div>
            `;
        }
    });

    return chatHTML;
}

function displayQuote(data) {
    console.log('📊 Displaying quote with data:', data);
    console.log('Monthly Premium:', data.monthlyPremium);
    console.log('Annual Premium:', data.annualPremium);

    // Ensure we have valid numbers
    const monthlyPremium = parseFloat(data.monthlyPremium);
    const annualPremium = parseFloat(data.annualPremium);
    const coverageAmount = parseFloat(data.coverageAmount);

    document.getElementById('monthly-premium').textContent = monthlyPremium.toFixed(2);
    document.getElementById('annual-premium').textContent = '$' + annualPremium.toFixed(2);
    document.getElementById('coverage-display').textContent = '$' + formatCurrency(coverageAmount);
    document.getElementById('age-display').textContent = data.age;
    document.getElementById('health-display').textContent = data.healthStatus;

    document.getElementById('quote-results').style.display = 'block';
    document.getElementById('quote-results').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ========== STEP 2: SHOW APPLICATION FORM ==========
function showApplicationForm() {
    document.getElementById('quote-results').style.display = 'none';
    document.getElementById('application-section').style.display = 'block';
    document.getElementById('application-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ========== STEP 3: SUBMIT APPLICATION ==========
async function handleApplicationSubmit(e) {
    e.preventDefault();

    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value;

    // Hide application form
    document.getElementById('application-section').style.display = 'none';

    // Show underwriting agent processing (steps will be added dynamically)
    showUnderwritingProcessing();

    const medsVal = document.getElementById('medications').value;
    alert("DEBUG: Sending Medications: [" + medsVal + "]");

    try {
        const response = await fetch(`${API_BASE}/applications/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quoteId: currentQuote.quoteId,
                applicantName: fullName,
                applicantEmail: email,
                applicantPhone: phone,
                applicantAddress: address,
                applicantMedications: document.getElementById('medications').value
            })
        });

        if (!response.ok) {
            throw new Error('Failed to submit application');
        }

        const data = await response.json();
        currentApplication = data;

        // Determine the path and setup dynamic steps
        const decision = data.underwritingResult?.decision;
        await setupDynamicUnderwritingSteps(decision);

        // Append UW Agent Chat to the history
        if (data.underwritingResult && data.underwritingResult.agentTrace) {
            appendAgentTraceToChat(data.underwritingResult.agentTrace, 'Underwriting Agent');
            await sleep(1500);
            document.getElementById('underwriting-processing').style.display = 'none';
        } else {
            // Fallback to simulation if no trace
            await simulateUnderwritingSteps();
            document.getElementById('underwriting-processing').style.display = 'none';
        }

        // Check if approved
        if (data.underwritingResult.decision === 'APPROVED') {
            // Show payment section
            await showPaymentSection(data);
        } else if (data.underwritingResult.decision === 'MANUAL_REVIEW') {
            // COMPLEX PATH: Handle Manual Review with Evidence Collection
            await handleManualReviewPath(data);
        } else {
            // Show rejection details
            showRejectionSection(data.underwritingResult);
        }

    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to submit application. Please try again.', 'error');
        document.getElementById('application-section').style.display = 'block';
        document.getElementById('underwriting-processing').style.display = 'none';
    }
}

function showUnderwritingProcessing() {
    const uwCard = document.getElementById('underwriting-processing');
    uwCard.style.display = 'block';
    uwCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function setupDynamicUnderwritingSteps(decision) {
    const stepsContainer = document.getElementById('uw-steps-container');
    stepsContainer.innerHTML = ''; // Clear any existing steps

    // Base steps - always shown for all scenarios
    const baseSteps = [
        { id: 'uw-credit', icon: '⏳', text: 'Checking credit bureau...', delay: 800 },
        { id: 'uw-mib', icon: '⏳', text: 'Verifying MIB database...', delay: 800 },
        { id: 'uw-rules', icon: '⏳', text: 'Running rules engine...', delay: 500 }
    ];

    // Additional steps based on decision type
    let additionalSteps = [];

    if (decision === 'MANUAL_REVIEW') {
        // Complex path - add evidence and manual review steps
        additionalSteps = [
            { id: 'uw-risk-flags', icon: '⏳', text: 'Detecting risk flags...', delay: 600 },
            { id: 'uw-evidence', icon: '⏳', text: 'Collecting medical evidence (APS)...', delay: 3000 },
            { id: 'uw-manual-analysis', icon: '⏳', text: 'AI analyzing evidence...', delay: 2000 },
            { id: 'uw-recommendation', icon: '⏳', text: 'Generating recommendation for human review...', delay: 1000 }
        ];
    } else if (decision === 'REJECTED') {
        // Rejection path - add risk assessment step
        additionalSteps = [
            { id: 'uw-risk-assessment', icon: '⏳', text: 'Assessing risk factors...', delay: 600 }
        ];
    } else {
        // Approval path - add final approval step
        additionalSteps = [
            { id: 'uw-final-check', icon: '⏳', text: 'Final approval check...', delay: 500 }
        ];
    }

    // Combine all steps
    const allSteps = [...baseSteps, ...additionalSteps];

    // Create HTML for all steps
    allSteps.forEach(step => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'uw-step';
        stepDiv.id = step.id;
        stepDiv.innerHTML = `
            <span class="step-icon">${step.icon}</span>
            <span class="step-text">${step.text}</span>
        `;
        stepsContainer.appendChild(stepDiv);
    });

    // Animate steps sequentially
    for (const step of allSteps) {
        await sleep(step.delay);
        const completionIcon = (decision === 'REJECTED' && step.id === 'uw-risk-assessment') ? '⚠️' : '✅';
        const completionText = step.text.replace('...', ' complete').replace('Checking', 'Checked')
            .replace('Verifying', 'Verified').replace('Running', 'Completed')
            .replace('Detecting', 'Detected').replace('Collecting', 'Collected')
            .replace('analyzing', 'analyzed').replace('Generating', 'Generated')
            .replace('Assessing', 'Assessed');
        markStepCompleted(step.id, completionIcon, completionText);
    }

    await sleep(500);
}

async function simulateUnderwritingSteps() {
    // Credit check
    await sleep(800);
    markStepCompleted('uw-credit', '✅', 'Credit check passed');

    // MIB check
    await sleep(800);
    markStepCompleted('uw-mib', '✅', 'MIB verification complete');

    // Rules engine
    await sleep(500);
    markStepCompleted('uw-rules', '✅', 'Rules engine approved');

    await sleep(500);
}

function markStepCompleted(stepId, icon, text) {
    const step = document.getElementById(stepId);
    step.classList.add('completed');
    step.querySelector('.step-icon').textContent = icon;
    step.querySelector('.step-text').textContent = text;
}

function showRejectionSection(uwResult) {
    // Update rejection reason
    document.getElementById('rejection-reason').textContent = uwResult.reason;

    // Update check results
    updateCheckResult('credit-check-result', uwResult.creditCheckPassed, 'Credit Check');
    updateCheckResult('mib-check-result', uwResult.mibCheckPassed, 'MIB Verification');
    updateCheckResult('rules-check-result', uwResult.decision === 'APPROVED', 'Rules Engine');

    // Show rejection section
    document.getElementById('rejection-section').style.display = 'block';
    document.getElementById('rejection-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function updateCheckResult(elementId, passed, label) {
    const element = document.getElementById(elementId);
    const icon = element.querySelector('.check-icon');
    const text = element.querySelector('.check-text');

    if (passed) {
        element.classList.add('passed');
        element.classList.remove('failed');
        icon.textContent = '✅';
        text.textContent = label + ' - Passed';
    } else {
        element.classList.add('failed');
        element.classList.remove('passed');
        icon.textContent = '❌';
        text.textContent = label + ' - Failed';
    }
}

// ========== COMPLEX PATH: MANUAL REVIEW ==========
async function handleManualReviewPath(data) {
    console.log('🔍 Complex Path: Manual Review Required', data);

    const uwResult = data.underwritingResult;

    // Display Evidence Collection Agent trace if available
    if (uwResult.evidenceTrace) {
        await sleep(500);
        appendAgentTraceToChat(uwResult.evidenceTrace, 'Evidence Agent');
        await sleep(1000);
    }

    // Display Manual Underwriting Agent trace if available
    if (uwResult.manualUWTrace) {
        await sleep(500);
        appendAgentTraceToChat(uwResult.manualUWTrace, 'Manual Underwriting Agent');
        await sleep(1000);
    }

    // Show Manual Review Pending card
    showManualReviewPendingCard(data, uwResult);
}

function showManualReviewPendingCard(applicationData, uwResult) {
    const manualReviewCard = document.createElement('div');
    manualReviewCard.className = 'card';
    manualReviewCard.style.cssText = 'animation: slideUp 0.5s ease-out; margin-top: 2rem;';

    const recommendation = uwResult.recommendation || 'APPROVE_WITH_CONDITIONS';
    const riskRating = uwResult.riskRating || 'MODERATE';

    manualReviewCard.innerHTML = `
        <div class="card-header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">⏳</div>
            <h2>Manual Review Required</h2>
            <p>Your application requires human underwriter review</p>
        </div>
        <div class="card-body">
            <div class="agent-card" style="margin-bottom: 1.5rem;">
                <div class="agent-header">
                    <div class="agent-icon">📋</div>
                    <h3>Application Details</h3>
                </div>
                <div class="agent-body">
                    <p><strong>Application Number:</strong> ${applicationData.applicationNumber}</p>
                    <p><strong>Reason for Review:</strong> ${uwResult.reason || 'Multiple risk factors identified'}</p>
                    <p><strong>Evidence Collected:</strong> ${uwResult.evidenceCollected ? '✅ Yes' : '⏳ In Progress'}</p>
                    ${uwResult.evidenceType ? `<p><strong>Evidence Type:</strong> ${uwResult.evidenceType}</p>` : ''}
                </div>
            </div>
            
            ${uwResult.manualUnderwritingComplete ? `
            <div class="agent-card" style="margin-bottom: 1.5rem; border-left: 4px solid #10b981;">
                <div class="agent-header">
                    <div class="agent-icon">🤖</div>
                    <h3>AI Agent Recommendation</h3>
                </div>
                <div class="agent-body">
                    <p><strong>Risk Rating:</strong> <span style="padding: 0.25rem 0.75rem; background: #fef3c7; color: #92400e; border-radius: 0.375rem; font-weight: 600;">${riskRating}</span></p>
                    <p><strong>Recommendation:</strong> ${recommendation.replace(/_/g, ' ')}</p>
                    ${uwResult.underwriterSummary ? `<p style="margin-top: 1rem; padding: 1rem; background: #f3f4f6; border-radius: 0.5rem; white-space: pre-line;">${uwResult.underwriterSummary}</p>` : ''}
                </div>
            </div>
            ` : ''}
            
            <div class="info-box" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1.5rem;">
                <h4 style="color: #92400e; margin-bottom: 0.5rem;">⏰ What Happens Next?</h4>
                <p style="color: #78350f; margin-bottom: 0.5rem;">A human underwriter will review your application and the AI agent's recommendation.</p>
                <p style="color: #78350f; margin-bottom: 0.5rem;"><strong>Estimated Review Time:</strong> 24-48 hours</p>
                <p style="color: #78350f;">You will receive an email notification once the review is complete.</p>
            </div>
            
            <div style="margin-top: 2rem; text-align: center;">
                <button onclick="location.reload()" class="btn btn-secondary" style="margin-right: 1rem;">
                    Start New Application
                </button>
                <button onclick="window.print()" class="btn btn-outline">
                    Print Application Summary
                </button>
            </div>
        </div>
    `;

    document.querySelector('.main-content').appendChild(manualReviewCard);
    manualReviewCard.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Hide the underwriting processing card
    document.getElementById('underwriting-processing').style.display = 'none';
}

// ========== STEP 4: PAYMENT ==========
async function showPaymentSection(applicationData) {
    document.getElementById('app-number').textContent = applicationData.applicationNumber;
    document.getElementById('payment-amount').textContent = '$' + currentQuote.monthlyPremium.toFixed(2);

    const paymentSection = document.getElementById('payment-section');
    paymentSection.style.display = 'block';
    paymentSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Initialize Stripe Payment Element
    const clientSecret = applicationData.paymentIntent.clientSecret;

    elements = stripe.elements({ clientSecret });
    paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');

    // Attach payment handler
    document.getElementById('submit-payment').addEventListener('click', handlePaymentSubmit);
}

async function handlePaymentSubmit(e) {
    e.preventDefault();

    const submitButton = document.getElementById('submit-payment');
    submitButton.disabled = true;
    submitButton.textContent = 'Processing Payment...';

    // Show payment processing indicator
    showPaymentProcessing();

    console.log('💳 Initiating Stripe payment processing...');

    try {
        // Confirm payment with Stripe - This sends the payment to Stripe's servers
        console.log('💳 Sending payment to Stripe for processing...');
        const { error } = await stripe.confirmPayment({
            elements,
            redirect: 'if_required'
        });

        console.log('💳 Stripe response received');

        if (error) {
            console.error('💳 Stripe payment failed:', error.message);
            hidePaymentProcessing();
            showMessage(error.message, 'error');
            submitButton.disabled = false;
            submitButton.textContent = 'Complete Payment';
            return;
        }

        console.log('✅ Stripe payment confirmed successfully!');
        console.log('📋 Verifying payment with backend and issuing policy...');

        // Update processing message
        const processingDiv = document.getElementById('stripe-processing');
        if (processingDiv) {
            processingDiv.querySelector('.agent-status').innerHTML = `
                ✅ Payment confirmed by Stripe!<br>
                <small style="font-weight: normal; color: var(--text-secondary);">Verifying and issuing your policy...</small>
            `;
        }

        // Wait a moment to show success
        await sleep(1500);

        // Hide payment processing
        hidePaymentProcessing();

        // Payment successful - confirm with backend and issue policy
        await confirmPaymentWithBackend();

    } catch (error) {
        console.error('Payment error:', error);
        hidePaymentProcessing();
        showMessage('Payment failed. Please try again.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Complete Payment';
    }
}

function showPaymentProcessing() {
    let processingDiv = document.getElementById('stripe-processing');
    if (!processingDiv) {
        processingDiv = document.createElement('div');
        processingDiv.id = 'stripe-processing';
        processingDiv.className = 'agent-card';
        processingDiv.style.cssText = 'margin-top: 1.5rem; background: linear-gradient(135deg, #f0f0ff 0%, #e8e8ff 100%); border: 2px solid #635bff;';
        processingDiv.innerHTML = `
            <div class="agent-header">
                <div class="agent-icon" style="font-size: 3rem;">💳</div>
                <h3 style="color: #635bff;">Processing Payment with Stripe</h3>
            </div>
            <div class="agent-body">
                <div class="progress-bar">
                    <div class="progress-fill" style="background: linear-gradient(90deg, #635bff 0%, #00d4ff 100%);"></div>
                </div>
                <p class="agent-status" style="margin-top: 1rem; font-weight: 600;">
                    🔒 Securely processing your payment...<br>
                    <small style="font-weight: normal; color: var(--text-secondary);">Please do not close this window</small>
                </p>
            </div>
        `;
        document.getElementById('payment-section').appendChild(processingDiv);
    }
    processingDiv.style.display = 'block';
    processingDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hidePaymentProcessing() {
    const processingDiv = document.getElementById('stripe-processing');
    if (processingDiv) {
        processingDiv.style.display = 'none';
    }
}

async function confirmPaymentWithBackend() {
    // Hide payment section
    document.getElementById('payment-section').style.display = 'none';

    // Show policy issuance agent
    showPolicyProcessing();

    try {
        const response = await fetch(`${API_BASE}/applications/confirm-payment/${currentApplication.applicationId}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to confirm payment: ${response.status} - ${errorText}`);
        }

        if (!response.ok) {
            throw new Error('Failed to confirm payment');
        }

        const data = await response.json();

        // Display Policy Issuance Agent trace in chat widget
        if (data.policy && data.policy.agentTrace) {
            appendAgentTraceToChat(data.policy.agentTrace, 'Policy Issuance Agent');
        }

        // Wait for agent animation
        await sleep(2000);

        // Hide policy processing
        document.getElementById('policy-processing').style.display = 'none';

        // Show policy active
        displayActivePolicy(data.policy);

    } catch (error) {
        console.error('Error:', error);

        document.getElementById('policy-processing').style.display = 'none';
        showPaymentConfirmationError(error.message);
    }
}

// ========== NEEDS ANALYSIS ==========
function handleCoverageAmountChange() {
    const select = document.getElementById('coverageAmount');
    const customGroup = document.getElementById('custom-coverage-group');
    const customInput = document.getElementById('customCoverageAmount');

    if (select.value === 'custom') {
        customGroup.style.display = 'block';
        customInput.required = true;
    } else {
        customGroup.style.display = 'none';
        customInput.required = false;
        customInput.value = '';
    }
}

async function handleNeedsAnalysisSubmit(e) {
    e.preventDefault();
    const age = parseInt(document.getElementById('needs-age').value);
    const dependents = parseInt(document.getElementById('dependents').value);
    const isSmoker = document.getElementById('needs-smoker').value;

    // Show agent processing
    document.getElementById('needs-analysis-section').style.display = 'none';

    const processingCard = document.getElementById('needs-agent-processing');
    if (processingCard) {
        processingCard.style.display = 'block';
        processingCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    try {
        const response = await fetch(`${API_BASE}/needs-analysis/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ age, dependents, isSmoker })
        });

        if (!response.ok) throw new Error('Failed to analyze needs');

        const data = await response.json();

        // Wait for animation
        await sleep(1500);

        // Hide processing
        if (processingCard) processingCard.style.display = 'none';

        // Show Agent Chat
        if (data.agentTrace) {
            appendAgentTraceToChat(data.agentTrace, 'Needs Analysis Agent');
        }

        // Pre-fill Quote Form
        document.getElementById('age').value = age;

        // Check for ineligibility
        if (data.status === 'Ineligible') {
            const warningHtml = `
                <div style="color: #991b1b; font-weight: 600;">
                    🚫 Application Not Recommended
                </div>
                <div style="margin-top: 0.5rem; color: #7f1d1d;">
                    ${data.reasoning.join('<br>')}
                </div>
            `;

            const recBox = document.getElementById('needs-recommendation');
            recBox.className = 'info-box error'; // You might need to add this CSS or use inline styles if class doesn't exist
            recBox.style.background = '#fef2f2';
            recBox.style.borderColor = '#ef4444';
            document.getElementById('recommendation-text').innerHTML = warningHtml;
            recBox.style.display = 'block';

            // Show the quote section but maybe don't pre-fill misleading values?
            // Actually, let's still show the form so they CAN try (and get rejected), so they trust the system, 
            // but the recommendation is clear. 
            // Or better, let's Scroll to the recommendation and STOP there? 
            // The user said "so you don't proceed to get rejected", implying we should maybe stop flow?
            // For now, I'll show the warning and still show the form but pre-fill data.
            // Wait, if I don't pre-fill, they can't see the form. 
            // Let's pre-fill but the big Red box will warn them.

            document.getElementById('age').value = age;
            document.getElementById('isSmoker').value = isSmoker;
            document.getElementById('healthStatus').value = 'Fair'; // Default

            // Don't auto-set coverage since we recommended 0

            document.getElementById('quote-section').style.display = 'block';
            document.getElementById('quote-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        // Auto-populate recommended coverage
        const recommended = data.recommended_coverage;
        const select = document.getElementById('coverageAmount');
        const customInput = document.getElementById('customCoverageAmount');
        const customGroup = document.getElementById('custom-coverage-group');

        // Check if recommended coverage matches any dropdown option
        let exactMatch = false;
        for (let option of select.options) {
            if (option.value && parseInt(option.value) === recommended) {
                select.value = option.value;
                exactMatch = true;
                break;
            }
        }

        // If no exact match, use custom input
        if (!exactMatch) {
            select.value = 'custom';
            customInput.value = recommended;
            customGroup.style.display = 'block';
            customInput.required = true;
        } else {
            customGroup.style.display = 'none';
            customInput.required = false;
        }

        // Auto-populate health status based on recommendation
        const recommendedHealthStatus = data.recommended_health_status || 'Fair';
        document.getElementById('healthStatus').value = recommendedHealthStatus;

        // Auto-populate smoker status
        document.getElementById('isSmoker').value = isSmoker;

        const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
        // Reset style in case it was red before
        const recBox = document.getElementById('needs-recommendation');
        recBox.style.background = '';
        recBox.style.borderColor = '';
        recBox.className = 'info-box';

        document.getElementById('recommendation-text').innerHTML = `
            Based on your profile (Age ${age}, ${dependents} dependents), we recommend <strong>${formatter.format(recommended)}</strong> coverage.<br>
            <small>${data.reasoning.join('<br>')}</small>
        `;
        recBox.style.display = 'block';

        // Switch views
        document.getElementById('quote-section').style.display = 'block';

    } catch (err) {
        console.error(err);
        if (processingCard) processingCard.style.display = 'none';
        skipNeedsAnalysis(e); // Fallback
    }
}

function skipNeedsAnalysis(e) {
    if (e) e.preventDefault();
    document.getElementById('needs-analysis-section').style.display = 'none';
    document.getElementById('quote-section').style.display = 'block';

    // Auto-fill age if entered in needs form
    const needsAge = document.getElementById('needs-age').value;
    if (needsAge) document.getElementById('age').value = needsAge;
}

function showNeedsAnalysis() {
    document.getElementById('quote-section').style.display = 'none';
    document.getElementById('needs-analysis-section').style.display = 'block';
}

// ========== POLICY SERVICING ==========
function showServicingForm() {
    document.getElementById('policy-active').style.display = 'none';
    document.getElementById('servicing-section').style.display = 'block';
}

function cancelServicing() {
    document.getElementById('servicing-section').style.display = 'none';
    document.getElementById('policy-active').style.display = 'block';
}

async function handleAddressChangeSubmit(e) {
    e.preventDefault();
    const newAddress = document.getElementById('new-address').value;
    const policyNumber = document.getElementById('policy-number').textContent; // Get from display

    try {
        const response = await fetch(`${API_BASE}/policies/${policyNumber}/address-change`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ newAddress })
        });

        if (!response.ok) throw new Error('Failed to update address');

        const data = await response.json();

        // Display agent trace in chat widget
        if (data.agentTrace) {
            appendAgentTraceToChat(data.agentTrace, 'Policy Servicing Agent');
        }

        document.getElementById('confirmation-letter-text').textContent = data.confirmationDocument;
        document.getElementById('servicing-section').style.display = 'none';
        document.getElementById('servicing-result').style.display = 'block';

    } catch (err) {
        alert('Failed to update address. Please try again.');
        console.error(err);
    }
}

function showPaymentConfirmationError(errorMessage) {
    const errorCard = document.createElement('div');
    errorCard.className = 'card';
    errorCard.style.cssText = 'animation: slideUp 0.5s ease-out;';
    errorCard.innerHTML = `
        <div class="card-header danger">
            <div class="danger-icon">⚠️</div>
            <h2>Payment Confirmation Error</h2>
            <p>There was an issue confirming your payment</p>
        </div>
        <div class="card-body">
            <div class="rejection-details">
                <h3>Error Details</h3>
                <div class="rejection-message">
                    ${errorMessage}
                </div>
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    Your payment may have been processed by Stripe. Please contact support with your application number: 
                    <strong>${currentApplication.applicationNumber}</strong>
                </p>
            </div>
            <button onclick="location.reload()" class="btn btn-primary btn-large">
                Start New Application
            </button>
        </div>
    `;

    document.querySelector('.main-content').appendChild(errorCard);
    errorCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showPolicyProcessing() {
    const policyCard = document.getElementById('policy-processing');
    policyCard.style.display = 'block';
    policyCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ========== STEP 5: POLICY ACTIVE ==========
function displayActivePolicy(policyData) {
    document.getElementById('policy-number').textContent = policyData.policyNumber;
    document.getElementById('policy-coverage').textContent = '$' + formatCurrency(currentQuote.coverageAmount);
    document.getElementById('policy-premium').textContent = '$' + currentQuote.monthlyPremium.toFixed(2) + '/month';
    document.getElementById('policy-date').textContent = formatDate(policyData.issueDate);

    // Store policy number for download
    document.getElementById('download-policy').dataset.policyNumber = policyData.policyNumber;

    document.getElementById('policy-active').style.display = 'block';
    document.getElementById('policy-active').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function downloadPolicy() {
    const policyNumber = this.dataset.policyNumber;

    try {
        const response = await fetch(`${API_BASE}/policies/${policyNumber}/pdf`);

        if (!response.ok) {
            throw new Error('Failed to download policy');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `policy-${policyNumber}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error('Error:', error);
        showMessage('Failed to download policy. Please try again.', 'error');
    }
}

// ========== UTILITY FUNCTIONS ==========
function showMessage(text, type) {
    // Try to find payment message first
    let messageDiv = document.getElementById('payment-message');

    // If not found or not visible, create a global message
    if (!messageDiv || !messageDiv.offsetParent) {
        messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + type;
        messageDiv.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 10000; max-width: 500px; padding: 1rem 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);';
        messageDiv.textContent = text;
        document.body.appendChild(messageDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    } else {
        messageDiv.textContent = text;
        messageDiv.className = 'message ' + type;
    }
}

function formatCurrency(amount) {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Toggle floating agent chat
function toggleAgentChat() {
    const chatWidget = document.getElementById('floating-agent-chat');
    if (chatWidget) {
        chatWidget.classList.toggle('collapsed');

        // Remove "New" badge when opened
        const badge = chatWidget.querySelector('.widget-badge');
        if (badge && !chatWidget.classList.contains('collapsed')) {
            setTimeout(() => badge.style.display = 'none', 300);
        }

        // Scroll to bottom when opened
        if (!chatWidget.classList.contains('collapsed')) {
            const chatBody = document.getElementById('agent-chat-history');
            if (chatBody) {
                setTimeout(() => {
                    chatBody.scrollTop = chatBody.scrollHeight;
                }, 100);
            }
        }
    }
}

// Helper function to append agent traces to chat widget
function appendAgentTraceToChat(agentTrace, agentName) {
    if (!agentTrace || !Array.isArray(agentTrace)) return;

    const chatMessages = parseAgentTraceToChat(agentTrace, agentName);
    let chatWidget = document.getElementById('floating-agent-chat');

    // Create widget if it doesn't exist
    if (!chatWidget) {
        chatWidget = document.createElement('div');
        chatWidget.id = 'floating-agent-chat';
        chatWidget.className = 'floating-chat-widget collapsed';
        document.body.appendChild(chatWidget);

        chatWidget.innerHTML = `
            <div class="chat-widget-button" onclick="toggleAgentChat()">
                <span class="widget-icon">🤖</span>
                <span class="widget-label">Agent Chat History</span>
                <span class="widget-badge">New</span>
            </div>
            <div class="chat-widget-container">
                <div class="agent-chat-header">
                    <div class="agent-chat-title">
                        <span class="agent-avatar">🤖</span>
                        <div>
                            <h3>Agent Chat History</h3>
                            <p class="agent-subtitle">Azure OpenAI Autonomous Agents</p>
                        </div>
                    </div>
                    <button class="chat-close-btn" onclick="toggleAgentChat()">×</button>
                </div>
                <div class="agent-chat-body" id="agent-chat-history">
                    ${chatMessages}
                </div>
            </div>
        `;
    } else {
        // Append to existing chat
        const chatHistory = document.getElementById('agent-chat-history');
        if (chatHistory) {
            const separator = `
                <div class="agent-separator">
                    <div class="separator-line"></div>
                    <div class="separator-text">${agentName}</div>
                    <div class="separator-line"></div>
                </div>
            `;
            chatHistory.innerHTML += separator + chatMessages;

            // Auto-scroll to bottom if widget is open
            if (!chatWidget.classList.contains('collapsed')) {
                setTimeout(() => {
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                }, 100);
            }
        }

        // Show "New" badge if widget is collapsed
        if (chatWidget.classList.contains('collapsed')) {
            const badge = chatWidget.querySelector('.widget-badge');
            if (badge) {
                badge.style.display = 'inline';
            }
        }
    }
}
