package com.insurance.service;

import com.insurance.model.InsuranceQuote;
import com.insurance.repository.InsuranceQuoteRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class QuoteAgentService {

    private final InsuranceQuoteRepository quoteRepository;

    @Value("${python.base.url:http://localhost:8000}")
    private String pythonBaseUrl;

    /**
     * Quote Agent simulates AI agent calculating premium based on risk factors
     * This method will be extended later to integrate with actual AI agents
     */
    public Map<String, Object> calculateQuote(Integer age, Double coverageAmount, String healthStatus,
            Boolean isSmoker) {
        log.info("🤖 Quote Agent: Delegating to Python Agent...");

        try {
            org.springframework.web.client.RestTemplate restTemplate = new org.springframework.web.client.RestTemplate();
            String url = pythonBaseUrl + "/agent/quote";

            Map<String, Object> request = new HashMap<>();
            request.put("age", age);
            request.put("coverageAmount", coverageAmount);
            request.put("healthStatus", healthStatus);
            request.put("isSmoker", isSmoker);

            Map<String, Object> response = restTemplate.postForObject(url, request, Map.class);
            log.info("🤖 Quote Agent: Received response from Python Agent: {}", response);

            // Save quote to database
            Double monthlyPremium = Double.valueOf(response.get("monthlyPremium").toString());
            Double annualPremium = Double.valueOf(response.get("annualPremium").toString());

            InsuranceQuote quote = new InsuranceQuote();
            quote.setAge(age);
            quote.setCoverageAmount(coverageAmount);
            quote.setHealthStatus(healthStatus);
            quote.setIsSmoker(isSmoker);
            quote.setMonthlyPremium(monthlyPremium);
            quote.setAnnualPremium(annualPremium);

            // Check for rejection from Python Agent
            if (response.containsKey("isEligible") && Boolean.FALSE.equals(response.get("isEligible"))) {
                quote.setStatus(InsuranceQuote.QuoteStatus.REJECTED);
                response.put("status", "REJECTED");
                response.put("rejectionReason", response.get("rejectionReason"));
            } else {
                quote.setStatus(InsuranceQuote.QuoteStatus.QUOTED);
                response.put("status", "QUOTED");
            }

            InsuranceQuote savedQuote = quoteRepository.save(quote);
            response.put("quoteId", savedQuote.getId());

            if (!response.containsKey("agentTrace")) {
                response.put("agentTrace", java.util.Collections.singletonList("Agent trace unavailable"));
            }

            return response;

        } catch (Exception e) {
            log.error("Failed to call Python Agent", e);
            log.info("Falling back to internal logic...");
            // Fallback logic could go here, but for now we re-throw to ensure agent is used
            throw new RuntimeException("Python Agent unavailable", e);
        }
    }

    private void simulateAgentProcessing(long milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
