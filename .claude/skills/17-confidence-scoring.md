# Confidence Scoring Skill

## Purpose
Assign confidence scores to agent decisions to enable intelligent thresholding and fallback strategies.

## Parameters/Returns
### Parameters
- `decision` (JSON): Decision object containing:
  - `type` (string): Decision type (e.g., "intent_classification", "task_match")
  - `inputs` (object): Input data used for decision
  - `context` (object): Contextual information

### Returns
- `score` (float 0-1): Confidence score where:
  - 0.9-1.0: Very high confidence
  - 0.7-0.89: High confidence
  - 0.5-0.69: Medium confidence
  - 0.3-0.49: Low confidence
  - 0-0.29: Very low confidence

## Logic Rules
1. Base score on multiple factors:
   - Input quality and completeness
   - History match strength
   - Model certainty
   - Contextual coherence
2. Apply domain-specific scoring rules
3. Calibrate scores using validation data when available
4. Use ensemble methods for critical decisions
5. Provide score breakdown for transparency

## Integration Points
- **Applied across all agents**: Universal decision quality metric
- **Thresholding mechanism**: Triggers human-in-the-loop when score < 0.5
- **A/B testing**: Enables comparison of decision-making strategies

## Re-usability Notes
- Integrates with any decision-making framework
- Useful in fraud detection systems
- Applicable to medical diagnosis support tools
- Can enhance recommendation engines
- Portable to risk assessment platforms
- Adaptable for automated trading systems
