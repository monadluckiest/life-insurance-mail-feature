package com.insurance.service;

import com.insurance.model.InsuranceApplication;
import com.insurance.repository.InsuranceApplicationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

@Service
@RequiredArgsConstructor
@Slf4j
public class UnderwritingAgentService {

    private final Random random = new Random();
    private final InsuranceApplicationRepository applicationRepository;
    private final EvidenceAgentService evidenceAgentService;
    private final ManualUnderwritingAgentService manualUnderwritingAgentService;

    @Value("${python.base.url:http://localhost:8000}")
    private String pythonBaseUrl;

    private RestTemplate restTemplate() {
        org.springframework.http.client.SimpleClientHttpRequestFactory factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(15000);
        return new RestTemplate(factory);
    }

    /**
     * Instant Underwriting Agent simulates automated underwriting decision
     * This includes mocked Credit/MIB API checks and rules engine
     * Will be extended to integrate with actual AI agents
     */
    public Map<String, Object> performInstantUnderwriting(InsuranceApplication application) {
        log.info("🤖 Underwriting Agent: Delegating to Python Agent for {}...", application.getApplicationNumber());

        try {
            String url = pythonBaseUrl + "/agent/underwrite";
            log.info("🤖 Underwriting Agent: Calling Python Agent at URL: {}", url);
            RestTemplate restTemplate = restTemplate();

            Map<String, Object> request = new HashMap<>();
            request.put("applicationNumber", application.getApplicationNumber());
            request.put("applicantName", application.getApplicantName());
            request.put("applicantMedications", application.getApplicantMedications());

            // Construct nested quote object
            Map<String, Object> quoteMap = new HashMap<>();
            quoteMap.put("age", application.getQuote().getAge());
            quoteMap.put("coverageAmount", application.getQuote().getCoverageAmount());
            quoteMap.put("healthStatus", application.getQuote().getHealthStatus());
            quoteMap.put("isSmoker", application.getQuote().getIsSmoker());

            request.put("quote", quoteMap);

            Map<String, Object> response = restTemplate.postForObject(url, request, Map.class);
            log.info("🤖 Underwriting Agent: Received response from Python Agent: {}", response);

            // Process decision
            String decision = (String) response.get("decision");

            if ("MANUAL_REVIEW".equalsIgnoreCase(decision)) {
                // COMPLEX PATH: Requires Evidence Collection and Manual Review
                log.info("🔍 Underwriting Agent: Application flagged for MANUAL REVIEW");

                application.setRequiresManualReview(true);
                application.setStatus(InsuranceApplication.ApplicationStatus.MANUAL_REVIEW_PENDING);
                application.setUnderwritingNotes((String) response.get("reason"));
                application.setEvidenceType((String) response.get("evidenceType"));
                applicationRepository.save(application);

                // Trigger Evidence Collection Agent
                log.info("📋 Triggering Evidence Collection Agent...");
                Map<String, Object> evidenceResult = evidenceAgentService.requestEvidence(application);

                // Refresh application to get updated evidence data
                application = applicationRepository.findById(application.getId()).orElse(application);

                // If evidence received, trigger Manual UW Agent
                if (Boolean.TRUE.equals(application.getEvidenceReceived())) {
                    log.info("🩺 Triggering Manual Underwriting Agent...");
                    Map<String, Object> manualUWResult = manualUnderwritingAgentService.analyzeEvidence(application);

                    // Combine all responses for frontend
                    response.put("requiresManualReview", true);
                    response.put("evidenceCollected", true);
                    response.put("manualUnderwritingComplete", true);
                    response.put("evidenceTrace", evidenceResult.get("agentTrace"));
                    response.put("manualUWTrace", manualUWResult.get("agentTrace"));
                    response.put("underwriterSummary", manualUWResult.get("underwriterSummary"));
                    response.put("recommendation", manualUWResult.get("recommendation"));
                    response.put("riskRating", manualUWResult.get("riskRating"));

                    log.info("✅ Complex Path Complete: Evidence collected and analyzed");
                }

            } else if ("APPROVED".equalsIgnoreCase(decision)) {
                // HAPPY PATH: Auto-approved
                application.setStatus(InsuranceApplication.ApplicationStatus.APPROVED);
                application.setCreditCheckPassed((Boolean) response.get("creditCheckPassed"));
                application.setMibCheckPassed((Boolean) response.get("mibCheckPassed"));
                application.setUnderwritingNotes((String) response.get("reason"));
                applicationRepository.save(application);
                log.info("🤖 Underwriting Agent: ✅ Application APPROVED by Python Agent");
            } else {
                // REJECT PATH
                application.setStatus(InsuranceApplication.ApplicationStatus.REJECTED);
                application.setCreditCheckPassed((Boolean) response.get("creditCheckPassed"));
                application.setMibCheckPassed((Boolean) response.get("mibCheckPassed"));
                application.setUnderwritingNotes((String) response.get("reason"));
                applicationRepository.save(application);
                log.info("🤖 Underwriting Agent: ❌ Application REJECTED by Python Agent");
            }

            // Ensure agentTrace is correct
            if (!response.containsKey("agentTrace")) {
                response.put("agentTrace", java.util.Collections.singletonList("Agent trace unavailable"));
            }

            return response;

        } catch (Exception e) {
            log.error("Failed to call Python Agent", e);
            throw new RuntimeException("Python Agent unavailable", e);
        }
    }

    /**
     * Simulate Credit Bureau API check
     * In production: Would call Experian/Equifax/TransUnion APIs
     */
    private boolean performCreditCheck(InsuranceApplication application) {
        // Mock logic - assumes excellent credit for demo
        Integer age = application.getQuote().getAge();
        String healthStatus = application.getQuote().getHealthStatus();

        // In happy path, everyone gets approved
        return age >= 18 && age <= 70;
    }

    /**
     * Simulate MIB (Medical Information Bureau) check
     * In production: Would call actual MIB API
     */
    private boolean performMIBCheck(InsuranceApplication application) {
        // Mock logic - returns "Clean" for happy path
        String healthStatus = application.getQuote().getHealthStatus();

        log.info("🤖 Underwriting Agent: Health Status = {}", healthStatus);

        // Happy path: Excellent and Good health always pass
        boolean passed = healthStatus.equalsIgnoreCase("excellent") ||
                healthStatus.equalsIgnoreCase("good");

        if (!passed) {
            log.warn("🤖 Underwriting Agent: ❌ MIB Check FAILED - Health status '{}' requires manual review",
                    healthStatus);
        }

        return passed;
    }

    /**
     * Simulate Rules Engine evaluation
     * In production: Would use Drools or similar rules engine
     */
    private boolean evaluateRulesEngine(InsuranceApplication application,
            boolean creditPassed, boolean mibPassed) {
        Integer age = application.getQuote().getAge();
        Double coverage = application.getQuote().getCoverageAmount();

        // Business rules
        boolean ageInRange = age >= 18 && age <= 70;
        boolean coverageInRange = coverage >= 50000 && coverage <= 5000000;
        boolean allChecksPassed = creditPassed && mibPassed;

        log.info("🤖 Underwriting Agent: Age in range (18-70): {}", ageInRange);
        log.info("🤖 Underwriting Agent: Coverage in range ($50k-$5M): {}", coverageInRange);
        log.info("🤖 Underwriting Agent: All checks passed: {}", allChecksPassed);

        return ageInRange && coverageInRange && allChecksPassed;
    }

    private void simulateAgentProcessing(long milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
