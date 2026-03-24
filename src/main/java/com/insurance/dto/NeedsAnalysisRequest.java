package com.insurance.dto;

import lombok.Data;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Min;

@Data
public class NeedsAnalysisRequest {
    @NotNull(message = "Age is required")
    @Min(value = 18, message = "Age must be at least 18")
    private Integer age;

    @NotNull(message = "Number of dependents is required")
    @Min(value = 0, message = "Dependents cannot be negative")
    private Integer dependents;

    @NotNull(message = "Smoking status is required")
    private String isSmoker;
}
