package com.insurance.repository;

import com.insurance.model.InsuranceQuote;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface InsuranceQuoteRepository extends JpaRepository<InsuranceQuote, Long> {
    List<InsuranceQuote> findByStatus(InsuranceQuote.QuoteStatus status);
    List<InsuranceQuote> findByApplicantEmail(String email);
}
