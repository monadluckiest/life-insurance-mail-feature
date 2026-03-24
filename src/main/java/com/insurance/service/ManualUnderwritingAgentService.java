package com.insurance.service;

import com.insurance.model.InsuranceApplication;
import com.insurance.repository.InsuranceApplicationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class ManualUnderwritingAgentService {
    
    private final InsuranceApplicationRepository applicationRepository;

    @Value("${python.base.url:http://localhost:8000}")
    private String pythonBaseUrl;

    private RestTemplate restTemplate() {
        org.springframework.http.client.SimpleClientHttpRequestFactory factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(15000);
        return new RestTemplate(factory);
    }
    
    /**
     * Manual Underwriting Agent
     * Analyzes evidence and provides recommendation for human underwriter
     */
    public Map<String, Object> analyzeEvidence(InsuranceApplication application) {
        log.info("🩺 Manual UW Agent: Analyzing evidence for {}...", 
                application.getApplicationNumber());
        
        try {
            // Prepare request for Python Manual UW Agent
            Map<String, Object> agentRequest = new HashMap<>();
            agentRequest.put("applicationNumber", application.getApplicationNumber());
            agentRequest.put("applicantName", application.getApplicantName());
            agentRequest.put("evidenceData", application.getEvidenceData());
            agentRequest.put("age", application.getQuote().getAge());
            agentRequest.put("coverageAmount", application.getQuote().getCoverageAmount());
            agentRequest.put("healthStatus", application.getQuote().getHealthStatus());
            
            String url = pythonBaseUrl + "/agent/manual-underwrite";
            log.info("🩺 Calling Manual UW Agent at URL: {} with request", url);
            
            // Call Python Manual UW Agent
            RestTemplate restTemplate = restTemplate();
            @SuppressWarnings("unchecked")
            Map<String, Object> agentResponse = restTemplate.postForObject(
                    url, agentRequest, Map.class);
            
            if (agentResponse != null) {
                log.info("🩺 Manual UW Agent Response: {}", agentResponse);
                
                // Update application with agent recommendation
                application.setAgentRecommendation((String) agentResponse.get("recommendation"));
                application.setRiskRating((String) agentResponse.get("riskRating"));
                application.setUnderwritingNotes((String) agentResponse.get("underwriterSummary"));
                application.setManualReviewStatus("PENDING");
                application.setStatus(InsuranceApplication.ApplicationStatus.AWAITING_HUMAN_DECISION);
                
                applicationRepository.save(application);
                
                Map<String, Object> result = new HashMap<>();
                result.put("success", true);
                result.put("message", "Evidence analysis complete - ready for human review");
                result.put("recommendation", agentResponse.get("recommendation"));
                result.put("riskRating", agentResponse.get("riskRating"));
                result.put("underwriterSummary", agentResponse.get("underwriterSummary"));
                result.put("keyFindings", agentResponse.get("keyFindings"));
                result.put("conditions", agentResponse.get("conditions"));
                
                // Include agent trace for frontend display
                @SuppressWarnings("unchecked")
                List<String> agentTrace = (List<String>) agentResponse.get("agentTrace");
                if (agentTrace != null) {
                    result.put("agentTrace", agentTrace);
                }
                
                return result;
            }
            
        } catch (Exception e) {
            log.error("🩺 Manual UW Agent error: {}", e.getMessage());
        }
        
        // Fallback
        log.info("🩺 Manual UW Agent: Using fallback mode");
        
        application.setManualReviewStatus("PENDING");
        application.setStatus(InsuranceApplication.ApplicationStatus.AWAITING_HUMAN_DECISION);
        applicationRepository.save(application);
        
        Map<String, Object> result = new HashMap<>();
        result.put("success", false);
        result.put("message", "Manual review required - fallback mode");
        return result;
    }
}
