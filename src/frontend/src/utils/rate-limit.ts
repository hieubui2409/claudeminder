/**
 * Callback for retry attempts
 */
export type RetryCallback = (attempt: number, delay: number) => void;

/**
 * Rate limit handler with exponential backoff
 */
export class RateLimitHandler {
  private readonly maxRetries: number;
  private readonly baseDelay: number;

  /**
   * Create a new rate limit handler
   *
   * @param maxRetries - Maximum number of retry attempts (default: 4)
   * @param baseDelay - Base delay in milliseconds (default: 1000)
   */
  constructor(maxRetries: number = 4, baseDelay: number = 1000) {
    this.maxRetries = maxRetries;
    this.baseDelay = baseDelay;
  }

  /**
   * Calculate exponential backoff delay
   *
   * @param attempt - Current attempt number (0-indexed)
   * @returns Delay in milliseconds
   */
  private calculateDelay(attempt: number): number {
    return this.baseDelay * Math.pow(2, attempt);
  }

  /**
   * Check if error is a rate limit error
   */
  private isRateLimitError(error: any): boolean {
    if (!error) return false;

    // Check for common rate limit indicators
    const message = error.message?.toLowerCase() || "";
    const statusCode = error.status || error.statusCode || 0;

    return (
      statusCode === 429 ||
      message.includes("rate limit") ||
      message.includes("too many requests")
    );
  }

  /**
   * Execute a function with exponential backoff on rate limit errors
   *
   * @param fn - Async function to execute
   * @param onRetry - Optional callback for retry attempts
   * @returns Result of the function
   * @throws Last error if all retries fail
   */
  async executeWithBackoff<T>(
    fn: () => Promise<T>,
    onRetry?: RetryCallback,
  ): Promise<T> {
    let lastError: any;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;

        // Only retry on rate limit errors
        if (!this.isRateLimitError(error)) {
          throw error;
        }

        // Don't retry if we've exhausted attempts
        if (attempt >= this.maxRetries) {
          console.error(
            `Rate limit retry failed after ${this.maxRetries} attempts`,
          );
          throw error;
        }

        const delay = this.calculateDelay(attempt);
        console.warn(
          `Rate limited. Retrying in ${delay}ms (attempt ${attempt + 1}/${this.maxRetries})`,
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
   * Reset retry state (if needed for manual control)
   */
  reset(): void {
    // Currently stateless, but kept for future extensions
  }
}

/**
 * Default rate limit handler instance
 */
export const defaultRateLimitHandler = new RateLimitHandler();

/**
 * Convenience function using the default handler
 */
export async function executeWithBackoff<T>(
  fn: () => Promise<T>,
  onRetry?: RetryCallback,
): Promise<T> {
  return defaultRateLimitHandler.executeWithBackoff(fn, onRetry);
}
