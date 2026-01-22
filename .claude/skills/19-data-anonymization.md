# Data Anonymization Skill

## Purpose
Anonymize sensitive data in logs and responses to ensure privacy compliance and security.

## Parameters/Returns
### Parameters
- `data` (string): Raw data that may contain Personally Identifiable Information (PII)

### Returns
- `anonymized_data` (string): Data with PII masked or replaced

## Logic Rules
1. Identify and mask PII categories:
   - Names: Replace with `[USER_NAME]`
   - Email addresses: Replace with `[EMAIL]`
   - Phone numbers: Replace with `[PHONE]`
   - Addresses: Replace with `[ADDRESS]`
   - ID numbers: Replace with `[ID]`
2. Use consistent placeholders for the same entity within a session
3. Preserve data structure and format for debugging purposes
4. Apply different strategies based on use case:
   - Logs: Full anonymization
   - Analytics: Pseudonymization with hashing
   - User-facing: Partial masking (e.g., `j***@example.com`)
5. Support configurable sensitivity levels

## Integration Points
- **In Feedback Loop Optimizer logging**: Ensures privacy in learning data
- **Error reporting**: Sanitizes error messages before external logging
- **Data export**: Applies before sharing data with third parties

## Re-usability Notes
- Compliance tool for GDPR, CCPA, and HIPAA applications
- Essential for healthcare data processing
- Useful in financial services applications
- Applicable to HR and recruitment systems
- Can enhance secure logging frameworks
- Portable to any system handling sensitive user data
