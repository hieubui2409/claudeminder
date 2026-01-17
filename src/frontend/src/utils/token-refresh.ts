import { open } from "@tauri-apps/plugin-shell";
import { notifyTokenExpired } from "./notifications";

/**
 * Claude login URL
 */
export const CLAUDE_LOGIN_URL = "https://claude.ai/login";

/**
 * Handle token expiration
 * Sends notification and prepares for login flow
 */
export async function handleTokenExpired(): Promise<void> {
  try {
    console.warn("Claude authentication token has expired");
    await notifyTokenExpired();
  } catch (error) {
    console.error("Failed to handle token expiration:", error);
    throw error;
  }
}

/**
 * Open Claude login page in the default browser
 *
 * @returns Promise that resolves when browser is opened
 */
export async function openClaudeLogin(): Promise<void> {
  try {
    console.log("Opening Claude login page...");
    await open(CLAUDE_LOGIN_URL);
  } catch (error) {
    console.error("Failed to open Claude login page:", error);
    throw error;
  }
}

/**
 * Watch token file for changes (placeholder for file watcher)
 *
 * This function is a placeholder for implementing file system watching
 * of ~/.claude/.credentials.json. The actual implementation will depend
 * on the backend providing file watch events.
 *
 * @param onTokenAvailable - Callback when new token is detected
 * @returns Cleanup function to stop watching
 */
export function watchTokenFile(_onTokenAvailable: () => void): () => void {
  console.warn("Token file watching not yet implemented");

  // TODO: Implement file watching via backend events
  // This could be done through:
  // 1. Backend polling the credentials file
  // 2. OS-level file system events (via Tauri plugin)
  // 3. Manual refresh trigger from UI

  // Return cleanup function
  return () => {
    console.log("Stopped watching token file");
  };
}

/**
 * Check if error indicates token expiration
 *
 * @param error - Error object to check
 * @returns true if error indicates expired token
 */
export function isTokenExpiredError(error: any): boolean {
  if (!error) return false;

  const message = error.message?.toLowerCase() || "";
  const statusCode = error.status || error.statusCode || 0;

  // Common token expiration indicators
  const tokenErrorPatterns = [
    "unauthorized",
    "authentication",
    "token expired",
    "invalid token",
    "session expired",
  ];

  const hasTokenError = tokenErrorPatterns.some((pattern) =>
    message.includes(pattern),
  );

  return statusCode === 401 || hasTokenError;
}

/**
 * Handle potential token expiration error
 * Checks if error is token-related and triggers appropriate handling
 *
 * @param error - Error to check
 * @returns true if token expiration was handled
 */
export async function handlePotentialTokenExpiration(
  error: any,
): Promise<boolean> {
  if (isTokenExpiredError(error)) {
    await handleTokenExpired();
    return true;
  }
  return false;
}
