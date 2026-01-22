# Performance Metrics Skill

## Purpose
Calculate session metrics like response time, accuracy, and user satisfaction to drive continuous improvement.

## Parameters/Returns
### Parameters
- `session_data` (JSON): Session information containing:
  - `start_time` (timestamp): Session start
  - `end_time` (timestamp): Session end
  - `interactions` (array): All user-agent interactions
  - `outcomes` (array): Action results

### Returns
- `metrics` (JSON): Comprehensive metrics object containing:
  - `response_time_avg` (float): Average response time in milliseconds
  - `response_time_p95` (float): 95th percentile response time
  - `accuracy` (float): Percentage of successful operations
  - `user_satisfaction_score` (float): Inferred satisfaction 0-1
  - `tool_usage` (object): Breakdown of tool invocations
  - `error_rate` (float): Percentage of failed operations

## Logic Rules
1. Aggregate data from timestamps and outcomes
2. Calculate statistical measures (mean, median, percentiles)
3. Infer user satisfaction from:
   - Task completion rate
   - Retry/correction frequency
   - Explicit feedback when available
4. Track tool-specific performance metrics
5. Identify performance bottlenecks
6. Compare against baseline/historical data

## Integration Points
- **End-of-session processing**: Triggered in stateless architecture after session completion
- **Continuous monitoring**: Real-time metrics for active sessions
- **Feedback loop**: Feeds into Feedback Loop Optimizer

## Re-usability Notes
- Re-usable in analytics dashboards
- Applicable to API performance monitoring
- Useful in SLA (Service Level Agreement) tracking
- Can enhance application performance monitoring (APM) tools
- Adaptable for user experience research platforms
- Portable to any system requiring performance insights
