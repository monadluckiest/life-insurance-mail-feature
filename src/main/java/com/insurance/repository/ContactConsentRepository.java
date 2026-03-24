package com.insurance.repository;

import com.insurance.model.ContactConsent;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ContactConsentRepository extends JpaRepository<ContactConsent, Long> {
    Optional<ContactConsent> findByEmail(String email);
}
