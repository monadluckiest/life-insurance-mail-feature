package com.insurance.service;

import com.stripe.Stripe;
import com.stripe.exception.StripeException;
import com.stripe.model.PaymentIntent;
import com.stripe.param.PaymentIntentCreateParams;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
public class StripePaymentService {
    
    @Value("${stripe.api.key}")
    private String stripeApiKey;
    
    @PostConstruct
    public void init() {
        Stripe.apiKey = stripeApiKey;
    }
    
    /**
     * Create a Stripe Payment Intent for policy purchase
     */
    public Map<String, Object> createPaymentIntent(Double amount, String description, 
                                                    String applicationNumber) throws StripeException {
        log.info("💳 Creating Stripe Payment Intent for {} - Amount: ${}", applicationNumber, amount);
        
        // Convert to cents (Stripe expects amount in smallest currency unit)
        long amountInCents = Math.round(amount * 100);
        
        PaymentIntentCreateParams params = PaymentIntentCreateParams.builder()
                .setAmount(amountInCents)
                .setCurrency("usd")
                .setDescription(description)
                .putMetadata("applicationNumber", applicationNumber)
                .setAutomaticPaymentMethods(
                        PaymentIntentCreateParams.AutomaticPaymentMethods.builder()
                                .setEnabled(true)
                                .build()
                )
                .build();
        
        PaymentIntent intent = PaymentIntent.create(params);
        
        Map<String, Object> response = new HashMap<>();
        response.put("clientSecret", intent.getClientSecret());
        response.put("paymentIntentId", intent.getId());
        response.put("amount", amount);
        response.put("status", intent.getStatus());
        
        log.info("✅ Stripe Payment Intent created: {} - Status: {}", intent.getId(), intent.getStatus());
        
        return response;
    }
    
    /**
     * Verify payment status
     */
    public Map<String, Object> verifyPayment(String paymentIntentId) throws StripeException {
        log.info("💳 Verifying payment with Stripe: {}", paymentIntentId);
        
        PaymentIntent intent = PaymentIntent.retrieve(paymentIntentId);
        
        Map<String, Object> response = new HashMap<>();
        response.put("paymentIntentId", intent.getId());
        response.put("status", intent.getStatus());
        response.put("amount", intent.getAmount() / 100.0);
        response.put("paid", "succeeded".equals(intent.getStatus()));
        
        if ("succeeded".equals(intent.getStatus())) {
            log.info("✅ Payment SUCCEEDED in Stripe - ${}", intent.getAmount() / 100.0);
        } else {
            log.warn("⚠️ Payment status in Stripe: {}", intent.getStatus());
        }
        
        return response;
    }
}
