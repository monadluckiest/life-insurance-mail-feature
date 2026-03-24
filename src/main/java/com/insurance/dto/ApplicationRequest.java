package com.insurance.dto;

import lombok.Data;
import jakarta.validation.constraints.*;

@Data
public class ApplicationRequest {
    
    @NotNull(message = "Quote ID is required")
    private Long quoteId;
    
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    private String applicantName;
    
    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String applicantEmail;
    
    @NotBlank(message = "Phone is required")
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Invalid phone number")
    private String applicantPhone;
    
    @NotBlank(message = "Address is required")
    @Size(min = 10, max = 200, message = "Address must be between 10 and 200 characters")
    private String applicantAddress;

    private String applicantMedications; // Optional field
}
