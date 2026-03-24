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
public class EvidenceAgentService {
    
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
     * Evidence Collection Agent
     * Requests and collects medical evidence for manual underwriting
     */
    public Map<String, Object> requestEvidence(InsuranceApplication application) {
        log.info("📋 Evidence Agent: Requesting evidence for {}...", 
                application.getApplicationNumber());
        
        try {
            // Prepare request for Python Evidence Agent
            Map<String, Object> agentRequest = new HashMap<>();
            agentRequest.put("applicationNumber", application.getApplicationNumber());
            agentRequest.put("applicantName", application.getApplicantName());
            agentRequest.put("evidenceType", application.getEvidenceType() != null ? 
                    application.getEvidenceType() : "APS");
            agentRequest.put("healthStatus", application.getQuote().getHealthStatus());
            agentRequest.put("age", application.getQuote().getAge());
            
            String url = pythonBaseUrl + "/agent/request-evidence";
            log.info("📋 Calling Evidence Agent at URL: {} with request: {}", url, agentRequest);
            
            // Call Python Evidence Agent
            RestTemplate restTemplate = restTemplate();
            @SuppressWarnings("unchecked")
            Map<String, Object> agentResponse = restTemplate.postForObject(
                    url, agentRequest, Map.class);
            
            if (agentResponse != null) {
                log.info("📋 Evidence Agent Response: {}", agentResponse);
                
                // Update application with evidence data
                application.setEvidenceRequested(true);
                application.setEvidenceReceived(
                        Boolean.TRUE.equals(agentResponse.get("evidenceReceived")));
                application.setEvidenceData((String) agentResponse.get("evidenceData"));
                application.setEvidenceReceivedAt(LocalDateTime.now());
                application.setStatus(InsuranceApplication.ApplicationStatus.AWAITING_HUMAN_DECISION);
                
                applicationRepository.save(application);
                
                Map<String, Object> result = new HashMap<>();
                result.put("success", true);
                result.put("message", "Evidence collected successfully");
                result.put("evidenceType", agentResponse.get("evidenceType"));
                result.put("evidenceReceived", agentResponse.get("evidenceReceived"));
                
                // Include agent trace for frontend display
                @SuppressWarnings("unchecked")
                List<String> agentTrace = (List<String>) agentResponse.get("agentTrace");
                if (agentTrace != null) {
                    result.put("agentTrace", agentTrace);
                }
                
                return result;
            }
            
        } catch (Exception e) {
            log.error("📋 Evidence Agent error: {}", e.getMessage());
        }
        
        // Fallback
        log.info("📋 Evidence Agent: Using fallback mode");
        
        application.setEvidenceRequested(true);
        application.setEvidenceReceived(false);
        application.setStatus(InsuranceApplication.ApplicationStatus.EVIDENCE_COLLECTION);
        applicationRepository.save(application);
        
        Map<String, Object> result = new HashMap<>();
        result.put("success", false);
        result.put("message", "Evidence collection initiated - fallback mode");
        return result;
    }
}
