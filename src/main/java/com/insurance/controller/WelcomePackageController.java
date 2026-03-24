package com.insurance.controller;

import com.insurance.dto.WelcomeTriggerRequest;
import com.insurance.service.WelcomePackageService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/welcome")
@RequiredArgsConstructor
@Slf4j
public class WelcomePackageController {

    private final WelcomePackageService welcomePackageService;

    /**
     * Endpoint to simulate trigging a welcome package
     * Expected payload example:
     * {
     *   "triggerType": "PROSPECT",
     *   "eventType": "LEAD_ORIGIN",
     *   "email": "test@example.com",
     *   "firstName": "Alex",
     *   "consentToEmail": true
     * }
     */
    @PostMapping("/trigger")
    public ResponseEntity<String> triggerWelcomePackage(@RequestBody WelcomeTriggerRequest request) {
        log.info("API request to trigger welcome package for {}", request.getEmail());
        
        try {
            welcomePackageService.processWelcomeTrigger(request);
            return ResponseEntity.ok("Welcome Package Triggered (if eligible). Checked logs for details.");
        } catch (Exception e) {
            log.error("Failed to process welcome trigger", e);
            return ResponseEntity.internalServerError().body("Error processing trigger: " + e.getMessage());
        }
    }
}
