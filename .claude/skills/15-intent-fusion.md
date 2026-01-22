# Intent Fusion Skill

## Purpose
Merge similar intents from multi-message inputs to create a unified, coherent action plan.

## Parameters/Returns
### Parameters
- `intents` (array): Array of detected intent objects, each containing:
  - `intent_type` (string): Type of intent (e.g., "add_task", "create_task")
  - `confidence` (float): Confidence score 0-1
  - `parameters` (object): Extracted parameters

### Returns
- `fused_intent` (string): Unified intent with merged parameters

## Logic Rules
1. Group synonym intents (e.g., "add", "create", "new")
2. Resolve conflicts by priority:
   - Higher confidence scores take precedence
   - More specific intents override generic ones
   - Recent messages override older ones in case of contradiction
3. Merge compatible parameters from related intents
4. Detect and flag truly conflicting intents that cannot be merged
5. Preserve user intent accuracy over aggressive merging

## Integration Points
- **Enhances Intent Detection**: Post-processing step in intent classification pipeline
- **Multi-turn dialogue**: Critical for conversations where users refine requests
- **Batch operations**: Useful when processing multiple related commands

## Re-usability Notes
- Re-usable in semantic search engines for query understanding
- Applicable to voice assistants processing compound commands
- Useful in email parsing for action item extraction
- Adaptable for business process automation
- Can enhance natural language SQL query builders
