package com.insurance.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "insurance_policies")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class InsurancePolicy {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String policyNumber;
    
    @OneToOne
    @JoinColumn(name = "application_id", nullable = false)
    private InsuranceApplication application;
    
    @Column(nullable = false)
    private String policyHolderName;
    
    @Column(nullable = false)
    private Double coverageAmount;
    
    @Column(nullable = false)
    private Double monthlyPremium;
    
    @Column(nullable = false)
    private LocalDateTime issueDate;
    
    @Column(nullable = false)
    private LocalDateTime effectiveDate;
    
    @Column(nullable = false)
    private LocalDateTime expiryDate;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PolicyStatus status;
    
    @Column
    private String pdfFilePath;
    
    @Lob
    @Column(columnDefinition = "CLOB")
    private String policyDocument;
    
    public enum PolicyStatus {
        ACTIVE, SUSPENDED, CANCELLED, EXPIRED
    }
    
    @PrePersist
    protected void onCreate() {
        issueDate = LocalDateTime.now();
        effectiveDate = LocalDateTime.now();
        expiryDate = LocalDateTime.now().plusYears(1);
        if (status == null) {
            status = PolicyStatus.ACTIVE;
        }
        if (policyNumber == null) {
            policyNumber = "POL-" + System.currentTimeMillis();
        }
    }
}
