package com.insurance.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "insurance_quotes")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class InsuranceQuote {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Integer age;

    @Column(nullable = false)
    private Double coverageAmount;

    @Column(nullable = false)
    private String healthStatus;

    @Column(name = "is_smoker")
    private Boolean isSmoker;

    @Column(nullable = false)
    private Double monthlyPremium;

    @Column(nullable = false)
    private Double annualPremium;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column
    private String applicantName;

    @Column
    private String applicantEmail;

    @Column
    private String applicantPhone;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private QuoteStatus status;

    public enum QuoteStatus {
        QUOTED, APPLIED, APPROVED, ISSUED, REJECTED
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (status == null) {
            status = QuoteStatus.QUOTED;
        }
    }
}
