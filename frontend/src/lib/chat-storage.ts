/**
 * Chat Storage Utility
 *
 * Manages localStorage persistence for conversation ID per user.
 * Feature: 009-frontend-chat-ui
 * Fix: Store conversation_id per user to prevent 403 errors when switching users
 */

import { CHAT_CONSTANTS } from '@/types/chat';

/**
 * Get user ID from JWT token in cookie
 * @returns The user ID or null if not found
 */
function getUserIdFromToken(): string | null {
  if (typeof document === 'undefined') {
    return null;
  }

  try {
    // Get auth-token cookie
    const cookies = document.cookie.split(';');
    const authCookie = cookies.find(c => c.trim().startsWith('auth-token='));

    if (!authCookie) {
      return null;
    }

    const token = authCookie.split('=')[1];

    // Decode JWT payload (base64)
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));

    return decoded.sub || decoded.user_id || decoded.id || null;
  } catch {
    return null;
  }
}

/**
 * Get storage key for current user
 * @returns User-specific storage key or fallback to default
 */
function getStorageKey(): string {
  const userId = getUserIdFromToken();

  if (userId) {
    return `${CHAT_CONSTANTS.STORAGE_KEY}_${userId}`;
  }

  // Fallback to default key if user ID not available
  return CHAT_CONSTANTS.STORAGE_KEY;
}

/**
 * Get stored conversation ID from localStorage for current user
 * @returns The conversation ID or null if not found
 */
export function getConversationId(): number | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const key = getStorageKey();
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = parseInt(stored, 10);
      return isNaN(parsed) ? null : parsed;
    }
    return null;
  } catch {
    // localStorage may not be available in some contexts
    return null;
  }
}

/**
 * Store conversation ID in localStorage for current user
 * @param id - The conversation ID to store
 */
export function setConversationId(id: number): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const key = getStorageKey();
    localStorage.setItem(key, id.toString());
  } catch {
    // localStorage may not be available or full
    console.warn('Failed to store conversation ID');
  }
}

/**
 * Clear stored conversation ID from localStorage for current user
 */
export function clearConversationId(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const key = getStorageKey();
    localStorage.removeItem(key);
  } catch {
    // localStorage may not be available
    console.warn('Failed to clear conversation ID');
  }
}

/**
 * Clear all conversation IDs from localStorage (useful on logout)
 */
export function clearAllConversationIds(): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    // Remove all keys that start with the storage key prefix
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(CHAT_CONSTANTS.STORAGE_KEY)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key));
  } catch {
    console.warn('Failed to clear conversation IDs');
  }
}
