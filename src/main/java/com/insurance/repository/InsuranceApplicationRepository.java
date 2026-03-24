package com.insurance.repository;

import com.insurance.model.InsuranceApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface InsuranceApplicationRepository extends JpaRepository<InsuranceApplication, Long> {
    Optional<InsuranceApplication> findByApplicationNumber(String applicationNumber);
    Optional<InsuranceApplication> findByStripePaymentIntentId(String stripePaymentIntentId);
}
