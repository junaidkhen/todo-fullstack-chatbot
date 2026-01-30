'use client';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Make an authenticated API request to Next.js API routes
 * The Next.js API routes will handle cookie-based authentication
 */
export async function authenticatedFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Important: Include cookies in requests
    });

    if (response.ok) {
      const data = await response.json();
      return { data };
    } else if (response.status === 401) {
      // Session expired or not authenticated, redirect to signin
      window.location.href = '/signin';
      return { error: 'Unauthorized' };
    } else {
      const errorData = await response.json();
      return { error: errorData.detail || 'Request failed' };
    }
  } catch (error) {
    console.error('API request error:', error);
    return { error: error instanceof Error ? error.message : 'Request failed' };
  }
}

/**
 * Fetch all tasks from Next.js API route
 */
export async function fetchTasks(): Promise<ApiResponse<any[]>> {
  return authenticatedFetch('/api/tasks');
}

/**
 * Create a new task via Next.js API route
 */
export async function createTask(taskData: {
  title: string;
  description?: string | null;
  priority?: string;
  category?: string | null;
  due_date?: string | null;
}): Promise<ApiResponse<any>> {
  return authenticatedFetch('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(taskData),
  });
}

/**
 * Update a task via Next.js API route
 */
export async function updateTask(
  id: number,
  taskData: {
    title?: string;
    description?: string | null;
    priority?: string;
    category?: string | null;
    due_date?: string | null;
  }
): Promise<ApiResponse<any>> {
  return authenticatedFetch(`/api/tasks/${id}`, {
    method: 'PUT',
    body: JSON.stringify(taskData),
  });
}

/**
 * Delete a task via Next.js API route
 */
export async function deleteTask(id: number): Promise<ApiResponse<any>> {
  return authenticatedFetch(`/api/tasks/${id}`, {
    method: 'DELETE',
  });
}

/**
 * Toggle task completion status via Next.js API route
 */
export async function toggleTaskCompletion(id: number): Promise<ApiResponse<any>> {
  return authenticatedFetch(`/api/tasks/${id}`, {
    method: 'PATCH',
  });
}

/**
 * Send a chat message to the AI assistant via Next.js API route
 */
export async function sendChatMessage(
  message: string,
  conversationId: number | null
): Promise<ApiResponse<{
  conversation_id: number;
  response: string;
  tool_calls: Array<{
    name: string;
    arguments: Record<string, unknown>;
    result: Record<string, unknown>;
  }> | null;
}>> {
  return authenticatedFetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });
}