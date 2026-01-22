# History Compression Skill

## Purpose
Compress long conversation histories for efficient agent input while preserving essential context.

## Parameters/Returns
### Parameters
- `history` (array): Full conversation history with all messages

### Returns
- `compressed_history` (string): Compressed version optimized for agent consumption

## Logic Rules
1. Retain last 5 messages fully (most recent context is critical)
2. Summarize non-essential older messages into compact representations
3. Preserve key information:
   - User intents and decisions
   - Task state changes
   - Important entity mentions
4. Use semantic compression techniques to maintain meaning
5. Apply token budget constraints (target: 70% reduction for messages beyond last 5)
6. Maintain chronological order and conversation flow

## Integration Points
- **Pre-fetch in stateless request cycle**: Applied before passing history to agents
- **Memory-constrained environments**: Essential for token-limited models
- **Long-running conversations**: Automatically triggered when history exceeds threshold

## Re-usability Notes
- Portable to memory-constrained AI models (mobile, edge devices)
- Applicable to any conversational AI system with context limits
- Useful in chat applications requiring context summarization
- Can enhance real-time translation systems
- Adaptable for meeting transcription and summarization tools
