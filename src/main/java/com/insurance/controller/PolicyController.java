package com.insurance.controller;

import com.insurance.model.InsurancePolicy;
import com.insurance.repository.InsurancePolicyRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/policies")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class PolicyController {

    private final InsurancePolicyRepository policyRepository;

    @Value("${python.base.url:http://localhost:8000}")
    private String pythonBaseUrl;

    private org.springframework.web.client.RestTemplate restTemplate() {
        org.springframework.http.client.SimpleClientHttpRequestFactory factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(15000);
        return new org.springframework.web.client.RestTemplate(factory);
    }

    /**
     * Get policy details
     */
    @GetMapping("/{policyNumber}")
    public ResponseEntity<Map<String, Object>> getPolicyDetails(@PathVariable String policyNumber) {
        try {
            InsurancePolicy policy = policyRepository.findByPolicyNumber(policyNumber)
                    .orElseThrow(() -> new RuntimeException("Policy not found"));

            Map<String, Object> response = new HashMap<>();
            response.put("policyNumber", policy.getPolicyNumber());
            response.put("policyHolderName", policy.getPolicyHolderName());
            response.put("coverageAmount", policy.getCoverageAmount());
            response.put("monthlyPremium", policy.getMonthlyPremium());
            response.put("status", policy.getStatus());
            response.put("issueDate", policy.getIssueDate());
            response.put("effectiveDate", policy.getEffectiveDate());
            response.put("expiryDate", policy.getExpiryDate());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Policy not found");
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Download policy PDF
     */
    @GetMapping("/{policyNumber}/pdf")
    public ResponseEntity<byte[]> downloadPolicyPDF(@PathVariable String policyNumber) {
        try {
            InsurancePolicy policy = policyRepository.findByPolicyNumber(policyNumber)
                    .orElseThrow(() -> new RuntimeException("Policy not found"));

            byte[] pdfBytes = Base64.getDecoder().decode(policy.getPolicyDocument());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDispositionFormData("attachment", "policy-" + policyNumber + ".pdf");

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(pdfBytes);

        } catch (Exception e) {
            log.error("Error downloading PDF", e);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Update policy address
     */
    @PostMapping("/{policyNumber}/address-change")
    public ResponseEntity<Map<String, Object>> updateAddress(
            @PathVariable String policyNumber,
            @RequestBody Map<String, String> request) {

        log.info("Received address update request for policy: {}", policyNumber);

        try {
            // Verify policy exists
            InsurancePolicy policy = policyRepository.findByPolicyNumber(policyNumber)
                    .orElseThrow(() -> new RuntimeException("Policy not found"));

            String newAddress = request.get("newAddress");
            if (newAddress == null || newAddress.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "New address is required"));
            }

            // Call Policy Servicing Agent
            String url = pythonBaseUrl + "/agent/policy-servicing";
            log.info("Calling Policy Servicing Agent at URL: {}", url);

            Map<String, Object> agentRequest = new HashMap<>();
            agentRequest.put("policyNumber", policyNumber);
            agentRequest.put("newAddress", newAddress);

            org.springframework.web.client.RestTemplate restTemplate = restTemplate();
            @SuppressWarnings("unchecked")
            Map<String, Object> agentResponse = restTemplate.postForObject(url, agentRequest, Map.class);

            // Return agent response which includes the confirmation letter
            return ResponseEntity.ok(agentResponse);

        } catch (Exception e) {
            log.error("Error updating address", e);
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
