package com.insurance.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "insurance_applications")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class InsuranceApplication {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String applicationNumber;
    
    @OneToOne
    @JoinColumn(name = "quote_id", nullable = false)
    private InsuranceQuote quote;
    
    @Column(nullable = false)
    private String applicantName;
    
    @Column(nullable = false)
    private String applicantEmail;
    
    @Column(nullable = false)
    private String applicantPhone;
    
    @Column(nullable = false)
    private String applicantAddress;

    @Column(length = 1000)
    private String applicantMedications;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ApplicationStatus status;
    
    @Column(length = 2000)
    private String underwritingNotes;
    
    @Column
    private Boolean creditCheckPassed;
    
    @Column
    private Boolean mibCheckPassed;
    
    @Column(nullable = false)
    private LocalDateTime submittedAt;
    
    @Column
    private LocalDateTime approvedAt;
    
    @Column
    private String stripePaymentIntentId;
    
    @Column
    private Boolean paymentCompleted;
    
    // Manual Review Fields
    @Column
    private Boolean requiresManualReview;
    
    @Column
    private Boolean evidenceRequested;
    
    @Column
    private Boolean evidenceReceived;
    
    @Column(length = 50)
    private String evidenceType;  // "APS", "Financial Review", etc.
    
    @Column(length = 5000)
    private String evidenceData;  // Store evidence text
    
    @Column(length = 50)
    private String manualReviewStatus;  // "PENDING", "APPROVED", "REJECTED"
    
    @Column(length = 2000)
    private String underwriterComments;  // Comments from human underwriter
    
    @Column(length = 2000)
    private String agentRecommendation;  // AI agent's recommendation
    
    @Column(length = 50)
    private String riskRating;  // "STANDARD", "MODERATE", "HIGH"
    
    @Column
    private LocalDateTime evidenceReceivedAt;
    
    @Column
    private LocalDateTime manualReviewCompletedAt;
    
    public enum ApplicationStatus {
        SUBMITTED, 
        UNDER_REVIEW, 
        MANUAL_REVIEW_PENDING,     // New status
        EVIDENCE_COLLECTION,       // New status
        AWAITING_HUMAN_DECISION,   // New status
        APPROVED, 
        REJECTED, 
        PAYMENT_PENDING, 
        PAYMENT_COMPLETED
    }
    
    @PrePersist
    protected void onCreate() {
        submittedAt = LocalDateTime.now();
        if (status == null) {
            status = ApplicationStatus.SUBMITTED;
        }
        if (applicationNumber == null) {
            applicationNumber = "APP-" + System.currentTimeMillis();
        }
        paymentCompleted = false;
    }
}
