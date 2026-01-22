# Ambiguity Resolution Skill

## Purpose
Resolve vague user inputs by generating clarifying questions to ensure accurate task execution.

## Parameters/Returns
### Parameters
- `message` (string): The user's input message that may contain ambiguities
- `context` (JSON): Contextual information including conversation history, user state, and current tasks

### Returns
- `clarifications` (array of strings): 1-2 targeted clarifying questions to resolve ambiguities

## Logic Rules
1. Identify ambiguities in user input (e.g., multiple matching tasks, unclear pronouns, missing parameters)
2. Generate 1-2 targeted questions that directly address the ambiguity
3. Prioritize the most critical ambiguity if multiple exist
4. Frame questions in a user-friendly, conversational manner
5. Avoid asking for information already available in context

## Integration Points
- **Pre-tool invocation**: Used by Dialogue Flow Coordinator before executing MCP tool calls
- **Intent Detection**: Triggered when intent confidence score is below threshold
- **Multi-match scenarios**: Activated when multiple tasks match user criteria

## Re-usability Notes
- Applicable to any NLP system requiring user disambiguation
- Can be adapted for chatbots, voice assistants, and conversational AI platforms
- Useful in search interfaces where query refinement is needed
- Portable across domains (e-commerce, customer support, productivity apps)
