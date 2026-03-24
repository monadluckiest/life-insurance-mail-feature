package com.insurance.dto;

import lombok.Data;
import jakarta.validation.constraints.*;

@Data
public class QuoteRequest {

    @NotNull(message = "Age is required")
    @Min(value = 18, message = "Minimum age is 18")
    @Max(value = 80, message = "Maximum age is 80")
    private Integer age;

    @NotNull(message = "Coverage amount is required")
    @Min(value = 50000, message = "Minimum coverage is $50,000")
    @Max(value = 5000000, message = "Maximum coverage is $5,000,000")
    private Double coverageAmount;

    @NotBlank(message = "Health status is required")
    @Pattern(regexp = "(?i)excellent|good|fair|poor", message = "Health status must be: Excellent, Good, Fair, or Poor")
    private String healthStatus;

    private Boolean isSmoker;
}
