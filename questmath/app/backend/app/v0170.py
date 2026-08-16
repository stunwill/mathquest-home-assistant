from __future__ import annotations

import json
import random
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0160, v090

app = v0160.app
app.version = legacy.APP_VERSION

_prior_make_question = legacy.make_question
_prior_hint_text = legacy.hint_text
_prior_mini_lesson = v090.mini_lesson
_prior_weights = legacy.weights
_focus_targets: ContextVar[dict[str, str]] = ContextVar('v0170_focus_targets', default={})

FOCUS_SKILLS = {
    'fact_recall_addition': 'addition',
    'fact_recall_subtraction': 'subtraction',
    'fact_recall_multiplication': 'multiplication',
    'fact_recall_division': 'division',
    'written_addition': 'addition',
    'written_subtraction': 'subtraction',
    'unknown_add_subtract': 'equations',
    'fact_families': 'fact families',
}


def _card(title: str, strategy: str, rule: str, steps: list[str], example: str, operation: str) -> dict[str, Any]:
    return {'title': title, 'strategy': strategy, 'rule': rule, 'steps': steps, 'example': example, 'operation': operation}


def _addition_fact(rng: random.Random):
    mode = rng.choice(['make_ten', 'double', 'near_double'])
    if mode == 'double':
        a = rng.randint(3, 10); b = a
        strategy = 'Use a known double'; rule = f'This is a double: {a} + {a}.'
        steps = ['Recall the matching doubles fact.', 'Say the whole fact aloud once after answering.']
    elif mode == 'near_double':
        a = rng.randint(3, 9); b = a + 1
        strategy = 'Use a near double'; rule = f'Use {a} + {a}, then add 1 more.'
        steps = ['Start with the easier doubles fact.', 'Adjust by the one extra.', 'Check that the answer is just one more than the double.']
    else:
        a = rng.randint(6, 9); to_ten = 10 - a; b = rng.randint(to_ten, 9)
        strategy = 'Make 10 first'; rule = f'Move {to_ten} from {b} to {a} to make 10.'
        steps = [f'Split {b} into {to_ten} and the amount left.', f'Combine {a} and {to_ten} to make 10.', 'Add the remaining part using the new 10 fact.']
    payload = {'operation': 'addition', 'fact_key': f'{min(a,b)}+{max(a,b)}', 'strategy_card': _card('Addition fact strategy', strategy, rule, steps, 'Example: 8 + 5 → 10 + 3', 'addition')}
    return legacy.q('VC2M4N06', 'fact_recall_addition', f'Calculate {a} + {b}.', 'number', payload, a + b, f'{strategy}: {a} + {b} = {a+b}.')


def _subtraction_fact(rng: random.Random):
    bottom = rng.randint(2, 10); difference = rng.randint(2, 10); top = bottom + difference
    payload = {'operation': 'subtraction', 'fact_key': f'{top}-{bottom}', 'strategy_card': _card('Subtraction fact strategy', 'Think addition', f'Ask: {bottom} + what makes {top}?', ['Start at the smaller number.', 'Use a known addition fact to reach the larger number.', 'Check by adding your answer to the number being subtracted.'], 'Example: 13 − 5 → think 5 + ? = 13', 'subtraction')}
    return legacy.q('VC2M4N06', 'fact_recall_subtraction', f'Calculate {top} − {bottom}.', 'number', payload, difference, f'Think addition: {bottom} + {difference} = {top}, so {top} − {bottom} = {difference}.')


def _multiplication_fact(rng: random.Random):
    a, b = rng.randint(2, 10), rng.randint(2, 10)
    if a == 5 or b == 5: strategy, rule = 'Use the 5s pattern', 'Products in the 5 times table end in 0 or 5.'
    elif a == 9 or b == 9:
        other = b if a == 9 else a; strategy, rule = 'Use 10 groups, then subtract one group', f'Think 10 × {other}, then subtract one {other}.'
    elif a in (4, 8) or b in (4, 8): strategy, rule = 'Double efficiently', 'Use repeated doubling instead of counting equal groups one by one.'
    else: strategy, rule = 'Use a known fact family', 'Turn the factors around if the reversed fact is easier to recall.'
    payload = {'operation': 'multiplication', 'fact_key': f'{min(a,b)}x{max(a,b)}', 'strategy_card': _card('Multiplication fact strategy', strategy, rule, ['Recall a related fact you know.', 'Use the pattern to adjust it.', 'Say the complete fact aloud after answering.'], 'Example: 9 × 6 → 10 × 6 − 6', 'multiplication')}
    return legacy.q('VC2M4A02', 'fact_recall_multiplication', f'Calculate {a} × {b}.', 'number', payload, a * b, f'{a} × {b} = {a*b}. Use the related pattern rather than counting each group.')


def _division_fact(rng: random.Random):
    divisor, answer = rng.randint(2, 10), rng.randint(2, 10); dividend = divisor * answer
    payload = {'operation': 'division', 'fact_key': f'{dividend}/{divisor}', 'strategy_card': _card('Division fact strategy', 'Use the matching multiplication fact', f'Ask: {divisor} × what makes {dividend}?', ['Name the divisor and the total.', 'Recall the multiplication fact with that total.', 'Use the missing factor as the quotient.'], 'Example: 42 ÷ 6 → think 6 × ? = 42', 'division')}
    return legacy.q('VC2M4A02', 'fact_recall_division', f'Calculate {dividend} ÷ {divisor}.', 'number', payload, answer, f'Use the inverse fact: {divisor} × {answer} = {dividend}, so {dividend} ÷ {divisor} = {answer}.')


def _written_addition(rng: random.Random):
    a = rng.randint(24, 89); b = rng.randint(15, 79); regroup = a % 10 + b % 10 >= 10
    strategy = 'Regroup the ones' if regroup else 'Add each place value'
    rule = 'Ten or more ones become 1 ten and the remaining ones.' if regroup else 'Fewer than 10 ones can stay in the ones place.'
    steps = ['Line up tens and ones.', 'Add the ones first.', 'Regroup 10 ones as 1 ten if needed.', 'Add the tens, including any regrouped ten.', 'Check with an estimate.']
    payload = {'operation': 'addition', 'strategy_card': _card('Written addition', strategy, rule, steps, 'Example: 47 + 38 → 7 + 8 = 15, write 5 and regroup 1 ten', 'addition')}
    return legacy.q('VC2M4N06', 'written_addition', f'Calculate {a} + {b}.', 'number', payload, a + b, f'Line up place values. Add ones, regroup if needed, then add tens: {a} + {b} = {a+b}.')


def _written_subtraction(rng: random.Random):
    case = rng.choice(['no_regroup', 'regroup', 'equal']); top_tens = rng.randint(3, 9); bottom_tens = rng.randint(0, top_tens - 1)
    if case == 'regroup':
        top_ones = rng.randint(0, 5); bottom_ones = rng.randint(top_ones + 1, 9)
        strategy = 'Regroup from the tens place'; rule = 'Less on top? Regroup next door and get 10 more.'
        case_step = f'Trade 1 ten for 10 ones, so {top_ones} ones becomes {top_ones+10} ones.'
    elif case == 'equal':
        top_ones = bottom_ones = rng.randint(1, 9); strategy = 'Write zero for equal digits'; rule = 'Digits the same? Zero is the game.'
        case_step = f'{top_ones} − {bottom_ones} is 0 in the ones place.'
    else:
        top_ones = rng.randint(2, 9); bottom_ones = rng.randint(0, top_ones - 1); strategy = 'Subtract without regrouping'; rule = 'More on top? No need to stop.'
        case_step = 'The top ones digit is large enough, so subtract the ones directly.'
    top = top_tens * 10 + top_ones; bottom = bottom_tens * 10 + bottom_ones
    steps = ['Line up tens and ones.', 'Start in the ones column.', case_step, 'Subtract the tens column.', 'Check by adding the difference and the smaller number.']
    payload = {'operation': 'subtraction', 'subtraction_case': case, 'strategy_card': _card('Column subtraction', strategy, rule, steps, 'Example: 81 − 8 → regroup 1 ten, making 7 tens and 11 ones', 'subtraction')}
    return legacy.q('VC2M4N06', 'written_subtraction', f'Calculate {top} − {bottom}.', 'number', payload, top - bottom, f'Line up place values and {strategy.lower()}: {top} − {bottom} = {top-bottom}.')


def _unknown_equation(rng: random.Random):
    unknown = rng.randint(21, 50); change = rng.randint(2, 20); form = rng.choice(['add', 'subtract_from_unknown', 'missing_subtrahend'])
    if form == 'add':
        total = unknown + change; prompt = f'Find the missing number: □ + {change} = {total}.'; rule = f'Undo + {change} by subtracting {change} from {total}.'; inverse = f'{total} − {change}'
    elif form == 'subtract_from_unknown':
        result = unknown - change; prompt = f'Find the missing number: □ − {change} = {result}.'; rule = f'Undo − {change} by adding {change} to {result}.'; inverse = f'{result} + {change}'
    else:
        total = unknown + change; prompt = f'Find the missing number: {total} − □ = {change}.'; rule = f'Ask what must be subtracted from {total} to leave {change}.'; inverse = f'{total} − {change}'
    payload = {'operation': 'equation', 'strategy_card': _card('Solve an unknown equation', 'Use the inverse operation', rule, ['Identify what happened to the box.', 'Use the opposite operation to undo it.', 'Substitute your answer into the original equation to check both sides match.'], 'Example: □ + 8 = 23 → 23 − 8', 'equation')}
    return legacy.q('VC2M4A01', 'unknown_add_subtract', prompt, 'number', payload, unknown, f'Use the inverse operation: {inverse} = {unknown}.')


FOCUS_GENERATORS = {
    'number': {
        'fact_recall_addition': _addition_fact,
        'fact_recall_subtraction': _subtraction_fact,
        'written_addition': _written_addition,
        'written_subtraction': _written_subtraction,
    },
    'algebra': {
        'unknown_add_subtract': _unknown_equation,
        'fact_recall_multiplication': _multiplication_fact,
        'fact_recall_division': _division_fact,
    },
}


def weights_v0170(session: Session, sid: int, topics: list[str]) -> list[float]:
    result = _prior_weights(session, sid, topics)
    targets: dict[str, str] = {}
    now = datetime.utcnow()
    for topic in topics:
        generators = FOCUS_GENERATORS.get(topic)
        if not generators:
            continue
        rows = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Question.topic == topic, legacy.Question.answered_at.is_not(None)).order_by(legacy.Question.answered_at.desc()).limit(300)).all())
        scored: list[tuple[float, str]] = []
        for skill in generators:
            relevant = [q for q in rows if q.skill.split(':', 1)[-1] == skill][:30]
            if not relevant:
                scored.append((4.0, skill))
                continue
            independent = sum(1 for q in relevant if any(a.correct for a in q.attempts) and not (q.hint_count or 0))
            hint_rate = sum(1 for q in relevant if q.hint_count) / len(relevant)
            days_since = max(0, (now - (relevant[0].answered_at or now)).days)
            due_boost = 1.5 if days_since >= 3 and independent / len(relevant) < .9 else 0.0
            scored.append(((1 - independent / len(relevant)) * 2 + hint_rate + due_boost, skill))
        targets[topic] = max(scored)[1]
    _focus_targets.set(targets)
    return result


def make_question_v0170(topic: str, level: int, rng: random.Random):
    target = _focus_targets.get().get(topic)
    if target and target in FOCUS_GENERATORS.get(topic, {}) and rng.random() < .55:
        return FOCUS_GENERATORS[topic][target](rng)
    if topic == 'number' and rng.random() < 0.78: return rng.choice([_addition_fact, _subtraction_fact, _written_addition, _written_subtraction])(rng)
    if topic == 'algebra' and rng.random() < 0.85: return rng.choice([_unknown_equation, _multiplication_fact, _division_fact])(rng)
    return _prior_make_question(topic, level, rng)


def hint_text_v0170(question: legacy.Question, hint_number: int) -> str:
    skill = question.skill.split(':', 1)[-1]
    if skill not in FOCUS_SKILLS: return _prior_hint_text(question, hint_number)
    try: card = json.loads(question.payload or '{}').get('strategy_card', {})
    except (TypeError, ValueError): card = {}
    if hint_number == 1: return str(card.get('rule') or 'Choose a known fact or inverse operation that makes this calculation easier.')
    steps = card.get('steps') or []
    return 'Next steps: ' + ' '.join(str(step) for step in steps[:3]) if steps else _prior_hint_text(question, hint_number)


def mini_lesson_v0170(question: legacy.Question) -> dict[str, Any]:
    skill = question.skill.split(':', 1)[-1]
    if skill == 'written_subtraction':
        return {'title': 'Column subtraction with place value', 'explanation': 'Work from right to left. Regroup only when the top digit in a column is smaller than the digit below it.', 'steps': ['Line up ones under ones and tens under tens.', 'Start with the ones column.', 'If the top digit is smaller, trade 1 ten for 10 ones.', 'Subtract each column.', 'Check using addition.'], 'example': '81 − 8: trade 1 ten, so 8 tens becomes 7 tens and 1 one becomes 11 ones. 11 − 8 = 3, then 7 tens remain, giving 73.', 'misconception': None}
    if skill == 'written_addition':
        return {'title': 'Column addition with regrouping', 'explanation': 'Ten ones are the same as one ten, so regroup when a column totals 10 or more.', 'steps': ['Line up place values.', 'Add the ones.', 'Write the ones digit and regroup a ten if needed.', 'Add the tens and check with an estimate.'], 'example': '47 + 38: 7 + 8 = 15, write 5 ones and regroup 1 ten. Then 4 + 3 + 1 = 8 tens, giving 85.', 'misconception': None}
    if skill.startswith('fact_recall_'):
        operation = FOCUS_SKILLS[skill]; examples = {'addition': '8 + 5 → make 10, then add 3.', 'subtraction': '13 − 5 → think 5 + ? = 13.', 'multiplication': '9 × 6 → 10 × 6 − 6.', 'division': '42 ÷ 6 → think 6 × ? = 42.'}
        return {'title': f'Efficient {operation} fact recall', 'explanation': 'Use a known relationship or pattern, then rehearse the complete fact. The goal is to move from strategy use toward quick recall without counting one-by-one.', 'steps': ['Notice the useful pattern.', 'Use the related known fact.', 'Answer and check with the inverse operation.', 'Say the full fact once to strengthen recall.'], 'example': examples[operation], 'misconception': None}
    if skill == 'unknown_add_subtract':
        return {'title': 'Solve the missing number', 'explanation': 'An equation is balanced. Use the inverse operation to isolate the box, then check the original equation.', 'steps': ['Identify the operation beside the box.', 'Undo it with the inverse operation.', 'Calculate the unknown.', 'Substitute it back and check both sides are equal.'], 'example': '□ + 8 = 23, so 23 − 8 = 15. Check: 15 + 8 = 23.', 'misconception': None}
    return _prior_mini_lesson(question)


def _focus_progress(session: Session, sid: int) -> dict[str, Any]:
    rows = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Question.answered_at.is_not(None)).order_by(legacy.Question.answered_at.desc()).limit(400)).all())
    operations = []
    for skill_name, label in FOCUS_SKILLS.items():
        relevant = [q for q in rows if q.skill.split(':', 1)[-1] == skill_name][:30]
        correct = [q for q in relevant if any(a.correct for a in q.attempts)]; independent = [q for q in correct if not (q.hint_count or 0)]
        seconds = [a.seconds for q in relevant for a in q.attempts if a.seconds > 0]; last_seen = relevant[0].answered_at if relevant else None
        independent_accuracy = round(len(independent) / len(relevant) * 100) if relevant else None; days_since = max(0, (datetime.utcnow() - last_seen).days) if last_seen else None
        operations.append({'skill': skill_name, 'label': label, 'questions': len(relevant), 'independent_accuracy': independent_accuracy, 'hints': sum(q.hint_count or 0 for q in relevant), 'average_seconds': round(sum(seconds) / len(seconds), 1) if seconds else None, 'last_practised': last_seen.isoformat() if last_seen else None, 'review_due': bool(relevant and days_since is not None and days_since >= 3 and (independent_accuracy or 0) < 90), 'status': 'not assessed' if len(relevant) < 3 else 'secure' if (independent_accuracy or 0) >= 85 else 'building recall'})
    return {'recommended_quest': 'number_algebra', 'focus': ['number', 'algebra'], 'operations': operations, 'review_due': [item['label'] for item in operations if item['review_due']]}


@app.get('/api/learning/focus-v0170')
def focus_progress(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    return _focus_progress(session, sid)


@app.get('/api/v0170/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {'version': legacy.APP_VERSION, 'number_algebra_focus_quest': True, 'fact_recall_operations': ['addition', 'subtraction', 'multiplication', 'division'], 'contextual_strategy_cards': True, 'written_subtraction_regrouping': True, 'unknown_addition_subtraction_equations': True, 'retention_review': True, 'finger_counting_replacement_strategies': True}


legacy.make_question = make_question_v0170
legacy.weights = weights_v0170
legacy.hint_text = hint_text_v0170
v090.mini_lesson = mini_lesson_v0170
v0120._move_spa_fallback_to_end()
