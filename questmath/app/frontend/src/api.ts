const API = 'api';
const ACTIVE_WORKSHEET_KEY = 'mq_active_worksheet_id';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiRequest<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token');
  let response: Response;
  try {
    response = await fetch(API + path, {
      ...options,
      headers: {
        ...(options.body instanceof FormData ? {} : {'Content-Type': 'application/json'}),
        ...(token ? {Authorization: `Bearer ${token}`} : {}),
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new ApiError('MathQuest could not connect. Check Home Assistant and try again.', 0);
  }

  const contentType = response.headers.get('content-type') || '';
  if (!response.ok) {
    let message = response.status === 401
      ? 'Your MathQuest session has expired. Sign in again to continue.'
      : 'MathQuest could not complete that action.';
    if (contentType.includes('json')) {
      const data = await response.json().catch(() => null);
      if (data?.detail) message = String(data.detail);
    }
    throw new ApiError(message, response.status);
  }
  return (contentType.includes('json') ? response.json() : response.blob()) as Promise<T>;
}

export function activeWorksheetId(): number | null {
  const value = localStorage.getItem(ACTIVE_WORKSHEET_KEY);
  return value && /^\d+$/.test(value) ? Number(value) : null;
}

export function rememberActiveWorksheet(id: number | null): void {
  if (id) localStorage.setItem(ACTIVE_WORKSHEET_KEY, String(id));
  else localStorage.removeItem(ACTIVE_WORKSHEET_KEY);
}

export async function loadActiveWorksheet<T = any>(): Promise<T | null> {
  const id = activeWorksheetId();
  if (id) {
    try {
      const worksheet: any = await apiRequest<T>(`/worksheets/${id}/view`);
      if (!worksheet?.completed_at) return worksheet;
      rememberActiveWorksheet(null);
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 404) throw error;
      rememberActiveWorksheet(null);
    }
  }
  return apiRequest<T | null>('/worksheets/active/latest');
}

export async function createWorksheet<T = any>(topic: string): Promise<T> {
  const worksheet = await apiRequest<T & {id: number}>('/worksheets/new', {
    method: 'POST',
    body: JSON.stringify({topic}),
  });
  rememberActiveWorksheet(worksheet.id);
  return worksheet;
}

export async function createSession<T = any>(kind: 'practice' | 'diagnostic', minutes: 5 | 10 | 15, topic = 'number_algebra'): Promise<T> {
  const worksheet = await apiRequest<T & {id: number}>('/sessions/new', {
    method: 'POST',
    body: JSON.stringify({kind, minutes, topic}),
  });
  rememberActiveWorksheet(worksheet.id);
  return worksheet;
}
