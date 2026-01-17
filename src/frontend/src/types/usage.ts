export interface FiveHourUsage {
  utilization: number;
  resets_at: string;
  input_tokens_used?: number;
  input_tokens_limit?: number;
  output_tokens_used?: number;
  output_tokens_limit?: number;
}

export interface GoalsStatus {
  enabled: boolean;
  is_on_track: boolean;
  current_usage: number;
  expected_usage: number;
  message: string;
}

export interface FocusModeStatus {
  is_snoozed: boolean;
  snooze_remaining: number;
  is_quiet_hours: boolean;
  is_dnd: boolean;
  notifications_suppressed: boolean;
}

export interface UsageResponse {
  five_hour: FiveHourUsage | null;
  goals?: GoalsStatus;
  focus_mode?: FocusModeStatus;
  error?: string;
  token_expired?: boolean;
  rate_limited?: boolean;
  offline?: boolean;
}
