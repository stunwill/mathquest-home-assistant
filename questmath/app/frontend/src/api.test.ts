import {afterEach, describe, expect, it, vi} from 'vitest';
import {apiRequest, ApiError} from './api';

afterEach(()=>{
  vi.restoreAllMocks();
  localStorage.clear();
});

describe('apiRequest failure classification',()=>{
  it('classifies a JSON 401 as MathQuest authentication failure',async()=>{
    vi.spyOn(globalThis,'fetch').mockResolvedValue(new Response(JSON.stringify({detail:'Not authenticated'}),{status:401,headers:{'content-type':'application/json'}}));
    await expect(apiRequest('/me')).rejects.toMatchObject({status:401,path:'/me',category:'mathquest_auth'} satisfies Partial<ApiError>);
  });

  it('classifies a plain-text 401 as ingress or proxy authentication failure',async()=>{
    vi.spyOn(globalThis,'fetch').mockResolvedValue(new Response('Unauthorized',{status:401,headers:{'content-type':'text/plain; charset=utf-8'}}));
    await expect(apiRequest('/dashboard/parent')).rejects.toMatchObject({status:401,path:'/dashboard/parent',category:'ingress_or_proxy_auth'} satisfies Partial<ApiError>);
  });

  it('keeps API paths relative for Home Assistant ingress',async()=>{
    const fetchMock=vi.spyOn(globalThis,'fetch').mockResolvedValue(new Response(JSON.stringify({ok:true}),{status:200,headers:{'content-type':'application/json'}}));
    await apiRequest('/me');
    expect(fetchMock).toHaveBeenCalledWith('api/me',expect.any(Object));
  });
});
