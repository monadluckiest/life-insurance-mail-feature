package com.insurance.controller;

import com.insurance.dto.QuoteRequest;
import com.insurance.service.QuoteAgentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/quotes")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class QuoteController {

    private final QuoteAgentService quoteAgentService;

    /**
     * Calculate insurance quote using Quote Agent
     */
    @PostMapping("/calculate")
    public ResponseEntity<Map<String, Object>> calculateQuote(@Valid @RequestBody QuoteRequest request) {
        log.info("Received quote request for age: {}, coverage: ${}",
                request.getAge(), request.getCoverageAmount());

        Map<String, Object> quote = quoteAgentService.calculateQuote(
                request.getAge(),
                request.getCoverageAmount(),
                request.getHealthStatus(),
                request.getIsSmoker());

        return ResponseEntity.ok(quote);
    }
}
