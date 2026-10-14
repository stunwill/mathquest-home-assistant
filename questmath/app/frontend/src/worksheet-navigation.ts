type Positioned = {id:number;position:number};

export function orderedQuestions<T extends Positioned>(questions:readonly T[]):T[]{
  return [...questions].sort((a,b)=>a.position-b.position||a.id-b.id);
}

export function isFinalQuestion(questions:readonly Positioned[],questionId?:number):boolean{
  return questions.length>0&&orderedQuestions(questions).at(-1)?.id===questionId;
}
