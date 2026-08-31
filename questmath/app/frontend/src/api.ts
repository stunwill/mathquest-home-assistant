const API = 'api';
const ACTIVE_WORKSHEET_KEY = 'mq_active_worksheet_id';
const DRAFT_PREFIX = 'mq_answer_draft:';

export type ApiFailureCategory = 'network'|'mathquest_auth'|'ingress_or_proxy_auth'|'server'|'client';

export class ApiError extends Error {
  status: number;
  path: string;
  category: ApiFailureCategory;

  constructor(message: string, status: number, path = '', category: ApiFailureCategory = 'client') {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.path = path;
    this.category = category;
  }
}

function failureCategory(status:number, contentType:string):ApiFailureCategory {
  if(status===401) return contentType.includes('json') ? 'mathquest_auth' : 'ingress_or_proxy_auth';
  if(status>=500) return 'server';
  return 'client';
}

function logFailure(path:string,status:number,category:ApiFailureCategory){
  console.error('[MathQuest] API request failed',{path,status,category});
}

function broadcastAuthExpiry(path:string,category:ApiFailureCategory){
  if(category==='mathquest_auth'&&path!=='/auth/login'&&typeof window!=='undefined'){
    window.dispatchEvent(new CustomEvent('mathquest-auth-expired'));
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
    logFailure(path,0,'network');
    throw new ApiError('MathQuest could not connect. Check Home Assistant and try again.', 0, path, 'network');
  }

  const contentType = response.headers.get('content-type') || '';
  if (!response.ok) {
    const category=failureCategory(response.status,contentType);
    let message = response.status === 401
      ? (category==='ingress_or_proxy_auth'
        ? 'Home Assistant could not validate this MathQuest session. Reopen MathQuest from the Home Assistant sidebar and try again.'
        : 'Your MathQuest session has expired. Sign in again to continue.')
      : 'MathQuest could not complete that action.';
    if (contentType.includes('json')) {
      const data = await response.json().catch(() => null);
      if (data?.detail) message = String(data.detail);
    }
    logFailure(path,response.status,category);
    broadcastAuthExpiry(path,category);
    throw new ApiError(message, response.status, path, category);
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

export function questionDraft(worksheetId: number, questionId: number): string {
  return localStorage.getItem(`${DRAFT_PREFIX}${worksheetId}:${questionId}`) || '';
}

export function rememberQuestionDraft(worksheetId: number, questionId: number, value: string): void {
  const key = `${DRAFT_PREFIX}${worksheetId}:${questionId}`;
  if (value) localStorage.setItem(key, value);
  else localStorage.removeItem(key);
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

export async function createIntervention<T = any>(minutes: 5 | 10 | 15, focus = 'auto'): Promise<T> {
  const worksheet = await apiRequest<T & {id: number}>('/interventions/new', {
    method: 'POST',
    body: JSON.stringify({minutes, focus}),
  });
  rememberActiveWorksheet(worksheet.id);
  return worksheet;
}
