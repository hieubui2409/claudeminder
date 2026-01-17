import { emit } from "@tauri-apps/api/event";

/**
 * Callback for retry attempts
 */
export type RetryCallback = (attempt: number, delay: number) => void;

/**
 * Offline mode detector with retry logic
 */
export class OfflineDetector {
  private readonly maxRetries: number;
  private readonly baseDelay: number;
  private isOffline: boolean = false;

  /**
   * Create a new offline detector
   *
   * @param maxRetries - Maximum number of retry attempts (default: 5)
   * @param baseDelay - Base delay in milliseconds (default: 2000)
   */
  constructor(maxRetries: number = 5, baseDelay: number = 2000) {
    this.maxRetries = maxRetries;
    this.baseDelay = baseDelay;
  }

  /**
   * Calculate exponential backoff delay
   *
   * @param attempt - Current attempt number (0-indexed)
   * @returns Delay in milliseconds (capped at 32s)
   */
  private calculateDelay(attempt: number): number {
    const delay = this.baseDelay * Math.pow(2, attempt);
    return Math.min(delay, 32000); // Cap at 32 seconds
  }

  /**
   * Check if error indicates network connectivity issue
   *
   * @param error - Error object to check
   * @returns true if network error detected
   */
  private isNetworkError(error: any): boolean {
    if (!error) return false;

    const message = error.message?.toLowerCase() || "";
    const errorCode = error.code?.toLowerCase() || "";
    const statusCode = error.status || error.statusCode || 0;

    // Common network error indicators
    const networkErrorPatterns = [
      "network",
      "offline",
      "connection",
      "timeout",
      "econnrefused",
      "enotfound",
      "enetunreach",
      "etimedout",
      "fetch failed",
      "failed to fetch",
    ];

    const hasNetworkError = networkErrorPatterns.some(
      (pattern) => message.includes(pattern) || errorCode.includes(pattern),
    );

    const isNetworkStatusCode = statusCode === 0 || statusCode >= 500;

    return hasNetworkError || isNetworkStatusCode;
  }

  /**
   * Emit offline mode event
   */
  private async emitOfflineMode(): Promise<void> {
    try {
      if (!this.isOffline) {
        this.isOffline = true;
        await emit("offline-mode", { offline: true });
        console.warn("Offline mode detected");
      }
    } catch (error) {
      console.error("Failed to emit offline mode event:", error);
    }
  }

  /**
   * Emit online mode event
   */
  private async emitOnlineMode(): Promise<void> {
    try {
      if (this.isOffline) {
        this.isOffline = false;
        await emit("offline-mode", { offline: false });
        console.log("Back online");
      }
    } catch (error) {
      console.error("Failed to emit online mode event:", error);
    }
  }

  /**
   * Check if error is a network error and emit offline event
   *
   * @param error - Error to check
   * @returns true if network error detected
   */
  async checkNetworkError(error: any): Promise<boolean> {
    const isNetwork = this.isNetworkError(error);

    if (isNetwork) {
      await this.emitOfflineMode();
    }

    return isNetwork;
  }

  /**
   * Retry a function with exponential backoff on network errors
   *
   * @param fn - Async function to execute
   * @param onRetry - Optional callback for retry attempts
   * @returns Result of the function
   * @throws Last error if all retries fail
   */
  async retryWithBackoff<T>(
    fn: () => Promise<T>,
    onRetry?: RetryCallback,
  ): Promise<T> {
    let lastError: any;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const result = await fn();

        // Success - mark as online
        await this.emitOnlineMode();

        return result;
      } catch (error) {
        lastError = error;

        const isNetwork = await this.checkNetworkError(error);

        // Only retry on network errors
        if (!isNetwork) {
          throw error;
        }

        // Don't retry if we've exhausted attempts
        if (attempt >= this.maxRetries) {
          console.error(
            `Network retry failed after ${this.maxRetries} attempts. Staying in offline mode.`,
          );
          throw error;
        }

        const delay = this.calculateDelay(attempt);
        console.warn(
          `Network error detected. Retrying in ${delay}ms (attempt ${attempt + 1}/${this.maxRetries})`,
        );

        // Call retry callback if provided
        if (onRetry) {
          onRetry(attempt + 1, delay);
        }

        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }

  /**
   * Get current offline status
   */
  getOfflineStatus(): boolean {
    return this.isOffline;
  }

  /**
   * Manually reset offline status
   */
  reset(): void {
    this.isOffline = false;
  }
}

/**
 * Default offline detector instance
 */
export const defaultOfflineDetector = new OfflineDetector();

/**
 * Convenience function using the default detector
 */
export async function checkNetworkError(error: any): Promise<boolean> {
  return defaultOfflineDetector.checkNetworkError(error);
}

/**
 * Convenience function using the default detector
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  onRetry?: RetryCallback,
): Promise<T> {
  return defaultOfflineDetector.retryWithBackoff(fn, onRetry);
}
