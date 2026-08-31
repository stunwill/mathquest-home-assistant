import React from 'react';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {Answer, App, Login, NumberLineAnswer} from './main';

beforeEach(()=>{
  localStorage.clear();
  sessionStorage.clear();
  vi.restoreAllMocks();
});

afterEach(()=>{
  document.body.innerHTML='';
});

describe('v0.36.0 login experience',()=>{
  it('defaults the editable username to sienna and leaves password blank',()=>{
    render(<Login onLogin={()=>{}}/>);
    const username=screen.getByLabelText('Username') as HTMLInputElement;
    const password=screen.getByLabelText('Password') as HTMLInputElement;
    expect(username.value).toBe('sienna');
    expect(password.value).toBe('');
    expect(document.activeElement).toBe(password);
    fireEvent.change(username,{target:{value:'parent'}});
    expect(username.value).toBe('parent');
  });

  it('recovers an expired MathQuest JSON session directly to login',async()=>{
    localStorage.setItem('token','expired-token');
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({detail:'Invalid session'}),{status:401,headers:{'content-type':'application/json'}})));
    render(<App/>);
    await waitFor(()=>expect((screen.getByLabelText('Username') as HTMLInputElement).value).toBe('sienna'));
    expect(localStorage.getItem('token')).toBeNull();
    expect(screen.queryByText('Something went wrong')).toBeNull();
  });

  it('does not destroy a valid MathQuest token for a plain-text ingress 401',async()=>{
    localStorage.setItem('token','valid-mathquest-token');
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response('Unauthorized',{status:401,headers:{'content-type':'text/plain'}})));
    render(<App/>);
    await waitFor(()=>expect(screen.getByText(/Home Assistant could not validate this MathQuest session/i)).toBeTruthy());
    expect(localStorage.getItem('token')).toBe('valid-mathquest-token');
  });
});

describe('interactive number line answers',()=>{
  const question={
    id:99,
    answer_type:'number_line',
    payload:{visual:{type:'number_line',interactive:true,min:20,max:50,interval:5,steps:6,label_indices:[0,2,6]}},
  };

  it('selects a tick on the line instead of rendering numerical choice buttons',()=>{
    const setValue=vi.fn();
    render(<Answer q={question} value="" setValue={setValue}/>);
    expect(screen.queryByRole('button',{name:'35'})).toBeNull();
    const target=screen.getByRole('button',{name:'Unlabelled tick 4'});
    fireEvent.click(target);
    expect(setValue).toHaveBeenCalledWith('35');
  });

  it('marks the selected position without revealing an unlabelled target value',()=>{
    render(<NumberLineAnswer q={question} value="35" setValue={()=>{}}/>);
    const target=screen.getByRole('button',{name:'Unlabelled tick 4'});
    expect(target.getAttribute('aria-pressed')).toBe('true');
    expect(target.classList.contains('selected')).toBe(true);
    expect(target.textContent).toBe('');
  });
});
