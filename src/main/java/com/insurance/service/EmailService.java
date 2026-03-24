package com.insurance.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmailService {

    private final JavaMailSender mailSender;

    @Value("${notification.email.from:noreply@lifeinsurance.com}")
    private String fromEmail;

    @Value("${notification.email.to:test@example.com}")
    private String toEmail;

    @Value("${notification.email.enabled:true}")
    private boolean emailEnabled;

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm:ss");

    /**
     * Send New Prospect Welcome Package Email
     */
    public void sendNewProspectWelcome(String emailAddress, String firstName) {
        if (!emailEnabled) {
            log.info("📧 Email notifications disabled - skipping new prospect welcome email");
            return;
        }
        try {
            String subject = "Welcome! Let’s Protect What Matters Most";
            String body = buildProspectWelcomeEmailBody(firstName);
            
            // Note: in a real system we send to the customer's email (emailAddress)
            // But per PAS_v2 guidelines, it might go to an internal generic address or the specified 'toEmail'
            // We'll use the provided parameter here.
            sendEmail(subject, body, emailAddress);
            log.info("📧 New prospect welcome email sent successfully to: {}", emailAddress);
        } catch (Exception e) {
            log.error("❌ Failed to send new prospect welcome email to: {}", emailAddress, e);
        }
    }

    /**
     * Send Existing Customer Welcome Package Email (For Life Events)
     */
    public void sendExistingCustomerWelcome(String emailAddress, String firstName) {
        if (!emailEnabled) {
            log.info("📧 Email notifications disabled - skipping existing customer welcome email");
            return;
        }
        try {
            String subject = "Congratulations on Your Recent Life Event — Let’s Review Your Coverage";
            String body = buildCustomerWelcomeEmailBody(firstName);
            
            sendEmail(subject, body, emailAddress);
            log.info("📧 Existing customer welcome email sent successfully to: {}", emailAddress);
        } catch (Exception e) {
            log.error("❌ Failed to send existing customer welcome email to: {}", emailAddress, e);
        }
    }

    /**
     * Core email sending method
     */
    private void sendEmail(String subject, String body, String toAddress) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(fromEmail);
        message.setTo(toAddress); // Sending to the dynamic address per requirement
        message.setSubject(subject);
        message.setText(body);

        mailSender.send(message);
    }

    private String buildProspectWelcomeEmailBody(String firstName) {
        String name = (firstName == null || firstName.isEmpty()) ? "Valued Customer" : firstName;
        return "Hi " + name + ",\n\n" +
                "Thank you for showing interest in protecting your family’s financial future. " +
                "We’re excited to welcome you and provide a personalized experience as you explore your life insurance options.\n\n" +
                "Life insurance is one of the most meaningful financial decisions you can make. " +
                "It provides your loved ones with stability and peace of mind—no matter what the future brings. " +
                "With the right plan, you can ensure:\n\n" +
                "Financial security for your family\n" +
                "Income protection, mortgage coverage, and support for day to day living expenses.\n\n" +
                "Protection tailored to your stage of life\n" +
                "Whether you're starting a family, buying a home, building your career, or planning retirement, " +
                "there’s a flexible plan that fits your needs.\n\n" +
                "Affordable options that grow with you\n" +
                "You can begin with a basic policy and expand your coverage as your life evolves.\n\n" +
                "As part of your welcome package, we’ve included resources to help you explore your options:\n" +
                "• A short guide on choosing the right type of life insurance\n" +
                "• Personalized planning tools\n" +
                "• Access to a licensed specialist who can answer your questions\n\n" +
                "We’re here to make the process simple and stress free.\n\n" +
                "If you’d like to speak with someone right away, you can schedule a conversation at any time using the link below:\n" +
                "Schedule a Consultation: [Insert link]\n\n" +
                "We look forward to helping you build a stronger financial foundation for the people who matter most.\n\n" +
                "Warm regards,\n" +
                "Your Life Insurance Team\n" +
                "Life Insurance Company\n" +
                "[Contact Info]\n\n" +
                "--- \n" +
                "Click here to opt out from marketing communications: [Opt-out link]\n" +
                "Physical Address: 123 Assurance Blvd, Protectville, NY 10001\n";
    }

    private String buildCustomerWelcomeEmailBody(String firstName) {
        String name = (firstName == null || firstName.isEmpty()) ? "Valued Customer" : firstName;
        return "Hi " + name + ",\n\n" +
                "Congratulations again on your recent milestone. Moments like these—buying a home, welcoming a child, " +
                "getting married, or advancing in your career—are exciting, and they also change what financial protection your family may need.\n\n" +
                "Since you already have a life insurance policy with us, this is a great time to make sure your coverage still aligns with your new goals. " +
                "Many customers choose to adjust their protection after a major life event to ensure:\n\n" +
                "Increased financial support for growing responsibilities\n" +
                "New dependents, larger financial commitments, or long term planning.\n\n" +
                "Added benefits for income replacement and debt protection\n" +
                "Enhanced coverage to safeguard mortgages, tuition, or shared financial obligations.\n\n" +
                "Options to build cash value or expand to living benefits\n" +
                "Policies that can support health related needs, retirement strategy, or unexpected events.\n\n" +
                "As part of your enhanced welcome package, we’re including tools to help you assess your current coverage:\n" +
                "• A personalized coverage review\n" +
                "• A breakdown of upgrade or supplemental policy options\n" +
                "• Guidance from a licensed professional who already understands your plan\n\n" +
                "We’d love to walk you through your options and help ensure your loved ones are fully protected.\n\n" +
                "Schedule Your Coverage Review: [Insert link]\n\n" +
                "Thank you for trusting us with your family’s financial security. We’re honored to continue supporting you.\n\n" +
                "Warm regards,\n" +
                "Your Life Insurance Team\n" +
                "Life Insurance Company\n" +
                "[Contact Info]\n\n" +
                "--- \n" +
                "Click here to opt out from marketing communications: [Opt-out link]\n" +
                "Physical Address: 123 Assurance Blvd, Protectville, NY 10001\n";
    }
}
