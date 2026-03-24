package com.insurance.dto;

import lombok.Data;

@Data
public class WelcomeTriggerRequest {
    
    // Type of trigger: PROSPECT or EXISTING_CUSTOMER
    private String triggerType;
    
    // The specific event triggering this: e.g. "LEAD_ORIGIN", "NEW_CHILD", "MARRIAGE"
    private String eventType;
    
    private String email;
    private String firstName;
    private String lastName;
    
    // Explicit consent flag captured during the journey
    private Boolean consentToEmail = true;
}
