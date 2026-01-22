# Workflow Templating Skill

## Purpose
Create reusable templates for common task workflows to accelerate repetitive operations.

## Parameters/Returns
### Parameters
- `workflow_type` (string): Type of workflow (e.g., "daily_review", "weekly_planning", "project_kickoff")

### Returns
- `template` (JSON): Workflow template containing:
  - `steps` (array): Ordered sequence of actions
  - `tools` (array): Required MCP tools
  - `defaults` (object): Default parameter values
  - `customization_points` (array): User-configurable elements

## Logic Rules
1. Predefine patterns for common workflows:
   - "daily_review": list tasks + filter by due date + remind
   - "weekly_planning": create weekly tasks + set priorities + schedule
   - "project_kickoff": create milestone tasks + assign team + set deadlines
2. Allow parameterization for flexibility
3. Support nested workflows (workflows can include sub-workflows)
4. Validate template compatibility with available tools
5. Provide clear documentation for each template

## Integration Points
- **Used by Multi-Tool Composer**: Provides pre-built orchestration patterns
- **User customization**: Allows users to save and modify personal templates
- **Automation triggers**: Can be scheduled or triggered by events

## Re-usability Notes
- Adaptable for Business Process Management (BPM) tools
- Useful in workflow automation platforms (Zapier-like systems)
- Can enhance project management software
- Applicable to DevOps automation (CI/CD templates)
- Portable to RPA (Robotic Process Automation) systems
