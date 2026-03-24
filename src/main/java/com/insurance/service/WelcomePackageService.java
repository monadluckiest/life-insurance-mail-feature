package com.insurance.service;

import com.insurance.dto.WelcomeTriggerRequest;
import com.insurance.model.ContactConsent;
import com.insurance.repository.ContactConsentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class WelcomePackageService {

    private final EmailService emailService;
    private final ContactConsentRepository consentRepository;

    // SLA Configurable (in a real app these come from properties)
    private static final int PROSPECT_COOLDOWN_DAYS = 30;
    private static final int CUSTOMER_COOLDOWN_DAYS = 180;

    public void processWelcomeTrigger(WelcomeTriggerRequest request) {
        log.info("Received WelcomeTriggerRequest: {}", request);

        // 1. Validate email address
        if (request.getEmail() == null || request.getEmail().isBlank() || !isValidEmail(request.getEmail())) {
            log.warn("Invalid email address: {}. Aborting welcome package.", request.getEmail());
            return;
        }

        // 2. Lookup or create consent profile
        ContactConsent consent = consentRepository.findByEmail(request.getEmail())
                .orElseGet(() -> {
                    ContactConsent newConsent = new ContactConsent();
                    newConsent.setEmail(request.getEmail());
                    newConsent.setOptedOut(false);
                    return consentRepository.save(newConsent);
                });

        // Update explicit consent if provided by the journey
        if (Boolean.FALSE.equals(request.getConsentToEmail())) {
            consent.setOptedOut(true);
            consentRepository.save(consent);
        }

        // 3. Check Global Opt-Out (CAN SPAM compliance)
        if (consent.getOptedOut()) {
            log.info("Contact {} is opted out of marketing emails. Suppressing welcome package.", consent.getEmail());
            return;
        }

        // 4. Process based on Trigger Category
        if ("PROSPECT".equalsIgnoreCase(request.getTriggerType())) {
            processProspectWelcome(request, consent);
        } else if ("EXISTING_CUSTOMER".equalsIgnoreCase(request.getTriggerType())) {
            processCustomerWelcome(request, consent);
        } else {
            log.warn("Unknown trigger type: {}", request.getTriggerType());
        }
    }

    private void processProspectWelcome(WelcomeTriggerRequest request, ContactConsent consent) {
        // Frequency check
        if (consent.getLastProspectWelcomeSent() != null &&
            consent.getLastProspectWelcomeSent().plusDays(PROSPECT_COOLDOWN_DAYS).isAfter(LocalDateTime.now())) {
            log.info("Suppressed New Prospect Welcome for {} - Sent within the last {} days.", 
                consent.getEmail(), PROSPECT_COOLDOWN_DAYS);
            return;
        }

        // Fire Email
        log.info("Triggering New Prospect Welcome Package for {}", consent.getEmail());
        emailService.sendNewProspectWelcome(consent.getEmail(), request.getFirstName());

        // Update Log
        consent.setLastProspectWelcomeSent(LocalDateTime.now());
        consentRepository.save(consent);
    }

    private void processCustomerWelcome(WelcomeTriggerRequest request, ContactConsent consent) {
        // Frequency check
        if (consent.getLastCustomerWelcomeSent() != null &&
            consent.getLastCustomerWelcomeSent().plusDays(CUSTOMER_COOLDOWN_DAYS).isAfter(LocalDateTime.now())) {
            log.info("Suppressed Existing Customer Welcome for {} - Sent within the last {} days.", 
                consent.getEmail(), CUSTOMER_COOLDOWN_DAYS);
            return;
        }

        // Fire Email
        log.info("Triggering Existing Customer Welcome Package for {} (Event: {})", 
            consent.getEmail(), request.getEventType());
        emailService.sendExistingCustomerWelcome(consent.getEmail(), request.getFirstName());

        // Update Log
        consent.setLastCustomerWelcomeSent(LocalDateTime.now());
        consentRepository.save(consent);
    }

    private boolean isValidEmail(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@(.+)$");
    }
}
