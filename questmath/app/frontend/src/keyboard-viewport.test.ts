import {afterEach,describe,expect,it} from 'vitest';
import {keyboardVisible} from './keyboard-viewport';

afterEach(()=>{document.body.innerHTML='';});

describe('keyboard viewport detection',()=>{
  it('activates only for a substantially reduced viewport and answer control',()=>{
    const input=document.createElement('input');
    expect(keyboardVisible(768,500,input)).toBeTruthy();
    expect(keyboardVisible(768,700,input)).toBeFalsy();
    expect(keyboardVisible(768,500,document.createElement('button'))).toBeFalsy();
  });
});
