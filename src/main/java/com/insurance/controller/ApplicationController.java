package com.insurance.controller;

import com.insurance.dto.ApplicationRequest;
import com.insurance.model.InsuranceApplication;
import com.insurance.model.InsuranceQuote;
import com.insurance.repository.InsuranceApplicationRepository;
import com.insurance.repository.InsuranceQuoteRepository;
import com.insurance.service.PolicyIssuanceAgentService;
import com.insurance.service.StripePaymentService;
import com.insurance.service.UnderwritingAgentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/applications")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class ApplicationController {
    
    private final InsuranceQuoteRepository quoteRepository;
    private final InsuranceApplicationRepository applicationRepository;
    private final UnderwritingAgentService underwritingAgentService;
    private final PolicyIssuanceAgentService policyIssuanceAgentService;
    private final StripePaymentService stripePaymentService;
    
    /**
     * Submit insurance application - triggers instant underwriting and policy issuance
     */
    @PostMapping("/submit")
    public ResponseEntity<Map<String, Object>> submitApplication(@Valid @RequestBody ApplicationRequest request) {
        log.info("Received application for quote ID: {}", request.getQuoteId());
        System.out.println("---------- DEBUG CONTROLLER ----------");
        System.out.println("RECEIVED MEDS: [" + request.getApplicantMedications() + "]");
        System.out.println("--------------------------------------");
        
        try {
            // Retrieve quote
            InsuranceQuote quote = quoteRepository.findById(request.getQuoteId())
                    .orElseThrow(() -> new RuntimeException("Quote not found"));
            
            // Create application
            InsuranceApplication application = new InsuranceApplication();
            application.setQuote(quote);
            application.setApplicantName(request.getApplicantName());
            application.setApplicantEmail(request.getApplicantEmail());
            application.setApplicantPhone(request.getApplicantPhone());
            application.setApplicantAddress(request.getApplicantAddress());
            application.setApplicantMedications(request.getApplicantMedications());
            application.setStatus(InsuranceApplication.ApplicationStatus.SUBMITTED);
            
            InsuranceApplication savedApplication = applicationRepository.save(application);
            
            // Update quote
            quote.setApplicantName(request.getApplicantName());
            quote.setApplicantEmail(request.getApplicantEmail());
            quote.setApplicantPhone(request.getApplicantPhone());
            quote.setStatus(InsuranceQuote.QuoteStatus.APPLIED);
            quoteRepository.save(quote);
            
            // Perform Instant Underwriting
            Map<String, Object> uwResult = underwritingAgentService.performInstantUnderwriting(savedApplication);
            
            Map<String, Object> response = new HashMap<>();
            response.put("applicationNumber", savedApplication.getApplicationNumber());
            response.put("applicationId", savedApplication.getId());
            response.put("underwritingResult", uwResult);
            
            // If approved, proceed with policy issuance
            if ("APPROVED".equals(uwResult.get("decision"))) {
                savedApplication.setApprovedAt(LocalDateTime.now());
                applicationRepository.save(savedApplication);
                
                // Create payment intent for first premium
                Double firstPremium = quote.getMonthlyPremium();
                Map<String, Object> paymentIntent = stripePaymentService.createPaymentIntent(
                        firstPremium,
                        "Life Insurance Policy - First Premium Payment",
                        savedApplication.getApplicationNumber()
                );
                
                savedApplication.setStripePaymentIntentId((String) paymentIntent.get("paymentIntentId"));
                savedApplication.setStatus(InsuranceApplication.ApplicationStatus.PAYMENT_PENDING);
                applicationRepository.save(savedApplication);
                
                response.put("paymentIntent", paymentIntent);
                response.put("status", "PAYMENT_PENDING");
                response.put("message", "Application approved! Please complete payment to activate policy.");
            } else {
                response.put("status", "REJECTED");
                response.put("message", "Application could not be approved at this time.");
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error processing application", e);
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to process application: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }
    
    /**
     * Confirm payment and issue policy
     */
    @PostMapping("/confirm-payment/{applicationId}")
    public ResponseEntity<Map<String, Object>> confirmPayment(@PathVariable Long applicationId) {
        log.info("Confirming payment for application ID: {}", applicationId);
        
        try {
            InsuranceApplication application = applicationRepository.findById(applicationId)
                    .orElseThrow(() -> new RuntimeException("Application not found"));
            
            // Verify payment with Stripe
            Map<String, Object> paymentStatus = stripePaymentService.verifyPayment(
                    application.getStripePaymentIntentId()
            );
            
            Map<String, Object> response = new HashMap<>();
            
            if (Boolean.TRUE.equals(paymentStatus.get("paid"))) {
                // Mark payment as completed
                application.setPaymentCompleted(true);
                application.setStatus(InsuranceApplication.ApplicationStatus.PAYMENT_COMPLETED);
                applicationRepository.save(application);
                
                // Issue Policy
                Map<String, Object> policyResult = policyIssuanceAgentService.issuePolicy(application);
                
                response.put("success", true);
                response.put("message", "Payment confirmed! Your policy is now ACTIVE.");
                response.put("policy", policyResult);
                
            } else {
                response.put("success", false);
                response.put("message", "Payment not completed. Status: " + paymentStatus.get("status"));
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error confirming payment", e);
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to confirm payment");
            error.put("message", e.getMessage());
            error.put("details", "The application may have been restarted or the application ID is invalid. Please start a new application.");
            return ResponseEntity.badRequest().body(error);
        }
    }
    
    /**
     * Get application status
     */
    @GetMapping("/{applicationNumber}")
    public ResponseEntity<Map<String, Object>> getApplicationStatus(@PathVariable String applicationNumber) {
        try {
            InsuranceApplication application = applicationRepository.findByApplicationNumber(applicationNumber)
                    .orElseThrow(() -> new RuntimeException("Application not found"));
            
            Map<String, Object> response = new HashMap<>();
            response.put("applicationNumber", application.getApplicationNumber());
            response.put("status", application.getStatus());
            response.put("applicantName", application.getApplicantName());
            response.put("submittedAt", application.getSubmittedAt());
            response.put("approvedAt", application.getApprovedAt());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Application not found");
            return ResponseEntity.notFound().build();
        }
    }
}
