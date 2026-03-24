package com.insurance.controller;

import com.insurance.dto.NeedsAnalysisRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import jakarta.validation.Valid;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/needs-analysis")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class NeedsAnalysisController {

    @Value("${python.base.url:http://localhost:8000}")
    private String pythonBaseUrl;

    private RestTemplate restTemplate() {
        org.springframework.http.client.SimpleClientHttpRequestFactory factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(15000);
        return new RestTemplate(factory);
    }

    @PostMapping("/calculate")
    public ResponseEntity<Map<String, Object>> calculateNeeds(@Valid @RequestBody NeedsAnalysisRequest request) {
        log.info("Received needs analysis request for age: {}, dependents: {}",
                request.getAge(), request.getDependents());

        try {
            String url = pythonBaseUrl + "/agent/needs-analysis";
            log.info("Calling Needs Analysis Agent at URL: {}", url);

            // Forward request to Python agent
            Map<String, Object> agentRequest = new HashMap<>();
            agentRequest.put("age", request.getAge());
            agentRequest.put("dependents", request.getDependents());
            agentRequest.put("isSmoker", request.getIsSmoker());

            RestTemplate restTemplate = restTemplate();
            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(url, agentRequest, Map.class);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("Error calling Needs Analysis Agent", e);
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
