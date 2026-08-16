export type SpeechResult = {supported: true} | {supported: false; message: string};

export function speakText(text: string, lang = 'en-AU'): SpeechResult {
  if (!('speechSynthesis' in window) || typeof SpeechSynthesisUtterance === 'undefined') {
    return {supported: false, message: 'Read aloud is not available in this browser. You can still use all Math Mentor support.'};
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = .92;
  window.speechSynthesis.speak(utterance);
  return {supported: true};
}
