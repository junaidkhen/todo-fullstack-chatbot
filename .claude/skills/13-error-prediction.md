# Error Prediction Skill

## Purpose
Predict potential errors in tool calls before execution to prevent failures and improve reliability.

## Parameters/Returns
### Parameters
- `planned_calls` (array): List of planned tool invocations with parameters

### Returns
- `risks` (JSON array): Array of risk objects containing:
  - `tool_name` (string): Name of the tool
  - `risk_description` (string): Description of potential error
  - `score` (integer 1-10): Risk severity score
  - `mitigation` (string): Suggested mitigation strategy

## Logic Rules
1. Check for common pitfalls:
   - Missing required parameters
   - Invalid parameter types or formats
   - Dependency violations (e.g., delete before create)
   - Resource conflicts (e.g., concurrent modifications)
2. Score risks on scale of 1-10 based on likelihood and impact
3. Prioritize critical risks (score >= 7) for immediate attention
4. Suggest specific mitigation strategies for each identified risk
5. Consider tool-specific validation rules

## Integration Points
- **Pre-execution validation**: Integrated with Tool Invocation Strategist
- **Workflow planning**: Used during multi-tool orchestration
- **Error handling**: Feeds into preventive error handling strategies

## Re-usability Notes
- Useful in QA automation for API testing
- Adaptable for CI/CD pipeline validation
- Can enhance infrastructure-as-code deployment safety
- Applicable to database migration planning
- Portable to any system with chained operations
