package com.insurance.model;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Entity
@Table(name = "contact_consents")
@Data
public class ContactConsent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private Boolean optedOut = false;

    // Track when the last welcome package was sent
    private LocalDateTime lastProspectWelcomeSent;
    private LocalDateTime lastCustomerWelcomeSent;

}
