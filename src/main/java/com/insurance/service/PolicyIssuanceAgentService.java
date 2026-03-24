package com.insurance.service;

import com.insurance.model.InsuranceApplication;
import com.insurance.model.InsurancePolicy;
import com.insurance.repository.InsurancePolicyRepository;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.itextpdf.layout.properties.TextAlignment;
import com.itextpdf.layout.properties.UnitValue;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.ByteArrayOutputStream;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class PolicyIssuanceAgentService {
    
    private final InsurancePolicyRepository policyRepository;

    @Value("${python.base.url:http://localhost:8000}")
    private String pythonBaseUrl;

    private RestTemplate restTemplate() {
        org.springframework.http.client.SimpleClientHttpRequestFactory factory = new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(15000);
        return new RestTemplate(factory);
    }
    
    /**
     * Policy Issuance Agent generates and activates insurance policy
     * Calls Python Policy Issuance Agent for AI-powered processing
     */
    public Map<String, Object> issuePolicy(InsuranceApplication application) {
        log.info("🤖 Policy Issuance Agent: Starting policy generation for {}...", 
                application.getApplicationNumber());
        
        // Create policy entity
        InsurancePolicy policy = new InsurancePolicy();
        policy.setApplication(application);
        policy.setPolicyHolderName(application.getApplicantName());
        policy.setCoverageAmount(application.getQuote().getCoverageAmount());
        policy.setMonthlyPremium(application.getQuote().getMonthlyPremium());
        policy.setStatus(InsurancePolicy.PolicyStatus.ACTIVE);
        
        try {
            // Call Python Policy Issuance Agent
            Map<String, Object> agentRequest = new HashMap<>();
            agentRequest.put("applicationNumber", application.getApplicationNumber());
            agentRequest.put("policyHolderName", application.getApplicantName());
            agentRequest.put("coverageAmount", application.getQuote().getCoverageAmount());
            agentRequest.put("monthlyPremium", application.getQuote().getMonthlyPremium());
            
            String url = pythonBaseUrl + "/agent/issue-policy";
            log.info("🤖 Calling Policy Issuance Agent at URL: {} with request: {}", url, agentRequest);
            
            RestTemplate restTemplate = restTemplate();
            @SuppressWarnings("unchecked")
            Map<String, Object> agentResponse = restTemplate.postForObject(
                    url, agentRequest, Map.class);
            
            if (agentResponse != null) {
                log.info("🤖 Policy Issuance Agent Response: {}", agentResponse);
                
                // Extract agent-generated policy number and dates
                String agentPolicyNumber = (String) agentResponse.get("policyNumber");
                String issueDateStr = (String) agentResponse.get("issueDate");
                String effectiveDateStr = (String) agentResponse.get("effectiveDate");
                String expiryDateStr = (String) agentResponse.get("expiryDate");
                
                // Override auto-generated policy number with agent's number if available
                if (agentPolicyNumber != null && !agentPolicyNumber.isEmpty()) {
                    policy.setPolicyNumber(agentPolicyNumber);
                }
                
                log.info("🤖 Policy Issuance Agent: Generating PDF document...");
                
                // Generate PDF policy document
                String pdfBase64 = generatePolicyPDF(policy, application);
                policy.setPolicyDocument(pdfBase64);
                
                // Save policy
                InsurancePolicy savedPolicy = policyRepository.save(policy);
                
                log.info("🤖 Policy Issuance Agent: ✅ Policy {} ACTIVE", savedPolicy.getPolicyNumber());
                
                Map<String, Object> result = new HashMap<>();
                result.put("policyId", savedPolicy.getId());
                result.put("policyNumber", savedPolicy.getPolicyNumber());
                result.put("policyStatus", savedPolicy.getStatus().name());
                result.put("issueDate", savedPolicy.getIssueDate());
                result.put("effectiveDate", savedPolicy.getEffectiveDate());
                result.put("expiryDate", savedPolicy.getExpiryDate());
                result.put("pdfDocument", pdfBase64);
                result.put("agentStatus", "Policy Issuance Agent completed");
                result.put("message", "Your policy is now ACTIVE!");
                
                // Include agent trace for frontend display
                @SuppressWarnings("unchecked")
                List<String> agentTrace = (List<String>) agentResponse.get("agentTrace");
                if (agentTrace != null) {
                    result.put("agentTrace", agentTrace);
                }
                
                return result;
            }
            
        } catch (Exception e) {
            log.error("🤖 Policy Issuance Agent error - falling back to default processing: {}", 
                    e.getMessage());
        }
        
        // Fallback: Generate policy without agent
        log.info("🤖 Policy Issuance Agent: Generating PDF document...");
        String pdfBase64 = generatePolicyPDF(policy, application);
        policy.setPolicyDocument(pdfBase64);
        
        // Save policy
        InsurancePolicy savedPolicy = policyRepository.save(policy);
        
        log.info("🤖 Policy Issuance Agent: ✅ Policy {} ACTIVE", savedPolicy.getPolicyNumber());
        
        Map<String, Object> result = new HashMap<>();
        result.put("policyId", savedPolicy.getId());
        result.put("policyNumber", savedPolicy.getPolicyNumber());
        result.put("policyStatus", savedPolicy.getStatus().name());
        result.put("issueDate", savedPolicy.getIssueDate());
        result.put("effectiveDate", savedPolicy.getEffectiveDate());
        result.put("expiryDate", savedPolicy.getExpiryDate());
        result.put("pdfDocument", pdfBase64);
        result.put("agentStatus", "Policy Issuance completed (fallback mode)");
        result.put("message", "Your policy is now ACTIVE!");
        
        return result;
    }
    
    /**
     * Generate PDF Policy Document using iText
     */
    private String generatePolicyPDF(InsurancePolicy policy, InsuranceApplication application) {
        try {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            PdfWriter writer = new PdfWriter(baos);
            PdfDocument pdfDoc = new PdfDocument(writer);
            Document document = new Document(pdfDoc);
            
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMM dd, yyyy");
            
            // Title
            Paragraph title = new Paragraph("LIFE INSURANCE POLICY")
                    .setFontSize(24)
                    .setBold()
                    .setTextAlignment(TextAlignment.CENTER);
            document.add(title);
            
            document.add(new Paragraph("\n"));
            
            // Policy Number
            Paragraph policyNum = new Paragraph("Policy Number: " + policy.getPolicyNumber())
                    .setFontSize(16)
                    .setBold();
            document.add(policyNum);
            
            document.add(new Paragraph("\n"));
            
            // Policy Details Table
            Table table = new Table(UnitValue.createPercentArray(new float[]{1, 2}));
            table.setWidth(UnitValue.createPercentValue(100));
            
            addTableRow(table, "Policy Holder:", application.getApplicantName());
            addTableRow(table, "Email:", application.getApplicantEmail());
            addTableRow(table, "Phone:", application.getApplicantPhone());
            addTableRow(table, "Address:", application.getApplicantAddress());
            addTableRow(table, "Coverage Amount:", "$" + String.format("%,.2f", policy.getCoverageAmount()));
            addTableRow(table, "Monthly Premium:", "$" + String.format("%.2f", policy.getMonthlyPremium()));
            addTableRow(table, "Annual Premium:", "$" + String.format("%.2f", policy.getMonthlyPremium() * 12));
            addTableRow(table, "Issue Date:", policy.getIssueDate().format(formatter));
            addTableRow(table, "Effective Date:", policy.getEffectiveDate().format(formatter));
            addTableRow(table, "Expiry Date:", policy.getExpiryDate().format(formatter));
            addTableRow(table, "Policy Status:", policy.getStatus().name());
            
            document.add(table);
            
            document.add(new Paragraph("\n\n"));
            
            // Terms and Conditions
            document.add(new Paragraph("TERMS AND CONDITIONS").setBold().setFontSize(14));
            document.add(new Paragraph(
                    "1. This policy provides life insurance coverage as specified above.\n" +
                    "2. Premiums must be paid monthly to keep the policy active.\n" +
                    "3. Coverage becomes effective on the effective date listed above.\n" +
                    "4. Beneficiaries will receive the coverage amount upon valid claim.\n" +
                    "5. Policy may be cancelled with 30 days written notice.\n" +
                    "6. All information provided must be accurate and truthful.\n"
            ));
            
            document.add(new Paragraph("\n"));
            
            // Signature Section
            document.add(new Paragraph("This policy was generated electronically and is valid without physical signature.")
                    .setItalic()
                    .setFontSize(10));
            
            document.close();
            
            // Convert to Base64
            byte[] pdfBytes = baos.toByteArray();
            return Base64.getEncoder().encodeToString(pdfBytes);
            
        } catch (Exception e) {
            log.error("Error generating PDF", e);
            return "";
        }
    }
    
    private void addTableRow(Table table, String label, String value) {
        table.addCell(new Paragraph(label).setBold());
        table.addCell(new Paragraph(value));
    }
}
