# Follow-Up Suggestion Skill

## Purpose
Suggest proactive follow-ups after actions to guide users toward optimal workflows and task completion.

## Parameters/Returns
### Parameters
- `action_result` (JSON): Result of completed action containing:
  - `action_type` (string): Type of action performed
  - `outcome` (string): Success/failure status
  - `affected_entities` (array): Tasks/items affected

### Returns
- `suggestions` (array): Array of suggestion objects containing:
  - `suggestion_text` (string): User-facing suggestion
  - `action_type` (string): Suggested action type
  - `priority` (string): "high", "medium", "low"

## Logic Rules
1. Generate contextually relevant suggestions based on outcomes:
   - After add: "Want to set a reminder?"
   - After complete: "Archive this task?"
   - After delete: "Undo deletion?" (if supported)
   - After bulk update: "Review changes?"
2. Limit to 2-3 suggestions to avoid overwhelming users
3. Prioritize high-value suggestions (time-saving, error-prevention)
4. Consider user's historical behavior patterns
5. Avoid suggesting actions just completed

## Integration Points
- **Appends to assistant responses**: Enhances final output with proactive guidance
- **Notification system**: Can trigger follow-up reminders
- **Workflow optimization**: Learns from accepted/rejected suggestions

## Re-usability Notes
- Enhances CRM (Customer Relationship Management) bots
- Useful in e-commerce checkout flows
- Applicable to productivity coaching applications
- Can improve onboarding experiences
- Adaptable for health and fitness tracking apps
- Portable to financial planning tools
