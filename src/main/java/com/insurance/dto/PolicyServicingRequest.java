package com.insurance.dto;

import lombok.Data;
import jakarta.validation.constraints.NotEmpty;

@Data
public class PolicyServicingRequest {
    @NotEmpty(message = "Policy number is required")
    private String policyNumber;

    @NotEmpty(message = "New address is required")
    private String newAddress;
}
