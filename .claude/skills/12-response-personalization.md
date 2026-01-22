# Response Personalization Skill

## Purpose
Tailor responses based on user history patterns to improve engagement and satisfaction.

## Parameters/Returns
### Parameters
- `user_id` (string): Unique identifier for the user
- `response_template` (string): Base response content to be personalized

### Returns
- `personalized_response` (string): Customized response incorporating user preferences

## Logic Rules
1. Incorporate past preferences (e.g., verbose vs. concise communication style)
2. Adjust tone based on user interaction history
3. Reference relevant past actions when contextually appropriate
4. Avoid over-personalization that may feel intrusive
5. Maintain professional boundaries while being friendly
6. Default to neutral style for new users or when preferences are unclear

## Integration Points
- **Post-tool execution**: Applied by Response Formatter after tool results are obtained
- **Multi-turn conversations**: Enhances continuity across dialogue turns
- **User profile system**: Reads from user preference storage

## Re-usability Notes
- Re-usable in marketing bots for improved user engagement
- Adaptable for customer service platforms
- Can enhance email automation systems
- Applicable to personalized notification systems
- Useful in educational apps for adaptive learning experiences
