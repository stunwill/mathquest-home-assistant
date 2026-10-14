"""Evidence-gated arithmetic families for newly composed learner worksheets."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from . import main as legacy, v0310, v0321, v0330

FAMILIES = {
    'subtraction': ['calculation', 'missing', 'context', 'estimate', 'error'],
    'multiplication': ['calculation', 'groups', 'missing', 'array'],
    'division': ['calculation', 'missing', 'sharing', 'inverse'],
    'equation': ['missing_start', 'missing_change', 'context'],
}


def generate(operation: str, rng: random.Random, *, challenge: bool = False, family: str | None = None) -> dict[str, Any]:
    family = family or rng.choice(FAMILIES[operation])
    answer_type = 'number'
    extra: dict[str, Any] = {}
    if operation == 'subtraction':
        across_zero = rng.random() < .5
        a = rng.randint(2, 9) * 1000 + rng.randint(1, 8) if across_zero else rng.randint(1200, 9500)
        b = rng.randint(137, min(a - 100, 2987))
        if across_zero:
            b = rng.randint(13,min((a-100)//10,298))*10 + rng.randint(a%10+1,9)
        answer = a - b
        rule = 'Line up place values. Regroup from the next non-zero place when a column has too few units.'
        steps = ['Start at the ones column.', 'If you regroup across zero, trade from the next non-zero place and rename each intervening place.', 'Subtract each column, then check with addition.']
        example = 'For 1026 − 487, rename 1026 as 9 hundreds, 11 tens and 16 ones. Subtract by place value to get 539; check 539 + 487 = 1026.'
        code = 'VC2M4N06'
        if challenge:
            c = rng.randint(220, 980); answer += c
            prompt = f'A shop has {a} items. It sells {b} and receives another {c}. How many items does it now have?'
            steps = ['Subtract the items sold.', 'Add the new items received.', 'Check each step against the story.']
            rule = 'Work in two steps: subtract what was sold, then add what arrived.'
            example = 'A library has 1026 books, lends 487 and receives 240. First 1026 − 487 = 539, then 539 + 240 = 779.'
            family = 'two_step'; extra['received'] = c
            working = f'{a} − {b} + {c} = {answer}.'
        elif family == 'missing':
            prompt = f'Find the missing number: {a} − □ = {a-b}.'; answer = b
            rule = 'Subtract the difference from the starting value to find the missing subtrahend.'
            example = 'For 1026 − □ = 539, calculate 1026 − 539 = 487, then substitute it back.'
            working = f'{a} − {a-b} = {b}; check {a} − {b} = {a-b}.'
        elif family == 'context':
            prompt = f'A library has {a} books. {b} are on loan. How many books remain in the library?'
            working = f'{a} − {b} = {answer} books.'
        elif family == 'estimate':
            rounded_a, rounded_b = (a+50)//100*100, (b+50)//100*100
            answer = rounded_a - rounded_b
            prompt = f'Estimate {a} − {b} by rounding each number to the nearest hundred.'
            rule = 'Round each number to the nearest hundred, then subtract the rounded values.'
            steps = ['Use the tens digit to round each number.', 'Subtract the rounded numbers.', 'Remember that this is an estimate.']
            example = 'Estimate 1026 − 487: round to 1000 − 500 = 500.'
            working = f'{a} rounds to {rounded_a}; {b} rounds to {rounded_b}. Estimate: {answer}.'
            code = 'VC2M5N08'
        elif family == 'error':
            error = rng.choice([100, 1000]); claimed = a-b+error; answer = error
            prompt = f'A pupil claims {a} − {b} = {claimed}. How much too large is the claimed answer?'
            rule = 'Check the claimed difference by adding back the subtracted number. Compare with the starting value.'
            example = 'A pupil claims 1026 − 487 = 564. Adding 487 gives 1051, which is 25 too large.'
            working = f'The correct difference is {a-b}. {claimed} − {a-b} = {error} too large.'
            extra['claimed'] = claimed; code = 'VC2M5N08'
        else:
            prompt = f'Calculate {a} − {b}.'; working = f'{a} − {b} = {answer}. Check: {answer} + {b} = {a}.'
        extra['regrouping_across_zero'] = across_zero
    elif operation == 'multiplication':
        a, b = (rng.randint(12, 29), rng.randint(12, 24)) if challenge else (rng.randint(16, 96), rng.randint(6, 9))
        answer = a*b; code = 'VC2M5N06'
        rule = 'Partition a factor by place value, multiply each part, then combine the partial products.'
        steps = ['Split a factor into tens and ones.', 'Multiply both parts by the other factor.', 'Add the partial products and check with an estimate.']
        example = 'For 36 × 14, calculate 36 × 10 = 360 and 36 × 4 = 144. Add 360 + 144 = 504.'
        if family == 'missing':
            prompt = f'Find the missing factor: □ × {b} = {a*b}.'; answer = a
            rule = 'Use division to undo multiplication, then check by multiplying back.'
            example = 'For □ × 14 = 504, divide 504 by 14 to get 36, then check 36 × 14 = 504.'
            steps = ['Identify the product and the known factor.', 'Divide the product by the known factor.', 'Substitute the missing factor and multiply to check.']
            working = f'{a*b} ÷ {b} = {a}.'; code = 'VC2M5A02'
        else:
            prompt = f'A school has {a} classrooms with {b} students in each. How many students are there?' if family == 'groups' else f'An array has {a} rows and {b} cells in each row. How many cells are there?' if family == 'array' else f'Calculate {a} × {b}.'
            working = f'{a} × {b} = {a//10*10} × {b} + {a%10} × {b} = {a//10*10*b} + {a%10*b} = {a*b}.' if b<10 else f'{a} × {b} = {a} × {b//10*10} + {a} × {b%10} = {a*(b//10*10)} + {a*(b%10)} = {a*b}.'
    elif operation == 'division':
        b = rng.choice([12, 15, 16, 18]) if challenge else rng.choice([6, 7, 8, 9, 12])
        quotient = rng.randint(18, 72) if challenge else rng.randint(12,45)
        a = b*quotient; answer = quotient; code = 'VC2M5N07'
        rule = 'Partition the dividend into multiples of the divisor. Add the partial quotients and check by multiplication.'
        steps = ['Find a useful multiple of the divisor.', 'Divide the remaining amount.', 'Combine the quotients and multiply back to check.']
        example = 'For 187 ÷ 11, split 187 into 110 + 77. Divide to get 10 + 7 = 17; check 17 × 11 = 187.'
        if challenge and family in ('sharing', 'inverse'):
            b = rng.choice([7, 8, 9]); remainder = rng.randint(1, b-1); a = b*quotient+remainder; answer = remainder
            prompt = f'{a} objects are packed into boxes holding {b} objects each. After filling as many complete boxes as possible, how many objects are left over?'
            family = 'remainder'; extra['quotient'] = quotient
            rule = 'Find the greatest multiple of the box size that fits in the total. Subtract it to find the leftovers.'
            steps = ['Find how many complete boxes fit.', 'Multiply the number of boxes by the box size.', 'Subtract the packed objects from the total.']
            example = 'For 397 objects in boxes of 6, fill 66 boxes: 66 × 6 = 396. There is 1 object left over.'
            working = f'{a} = {b} × {quotient} + {remainder}; {remainder} objects remain.'
        elif family == 'missing':
            prompt = f'Find the missing dividend: □ ÷ {b} = {quotient}.'; answer = a
            rule = 'Multiply the quotient by the divisor to recover the dividend.'
            example = 'For □ ÷ 11 = 17, multiply 17 × 11 = 187.'
            steps = ['Identify the quotient and the divisor.', 'Multiply the quotient by the divisor.', 'Substitute the dividend and divide to check.']
            working = f'{quotient} × {b} = {a}.'; code = 'VC2M5A02'
        else:
            prompt = f'{a} pencils are shared equally among {b} classes. How many pencils does each class get?' if family == 'sharing' else f'What number makes {b} × □ = {a}?' if family == 'inverse' else f'Calculate {a} ÷ {b}.'
            working = f'{a} ÷ {b} = {quotient}; check {quotient} × {b} = {a}.'
    else:
        a, b = rng.randint(120, 980), rng.randint(25, 270)
        answer = a; code = 'VC2M4A01'
        rule = 'Use the inverse operation to find the unknown, then substitute it into the original equation.'
        steps = ['Identify the starting value and the change.', 'Undo the change using the inverse operation.', 'Substitute the result and check both sides agree.']
        example = 'For □ − 175 = 925, add 175 to get 1100. Check 1100 − 175 = 925.'
        if challenge:
            c = rng.randint(21, 99); extra['received'] = c
            prompt = f'Find the missing number: □ − {b} + {c} = {a-b+c}.'
            working = f'Undo + {c}, then undo − {b}: {a-b+c} − {c} + {b} = {a}.'
            example = 'For □ − 175 + 40 = 965, undo +40, then undo −175: 965 − 40 + 175 = 1100.'
            family = 'two_step'
        elif family == 'missing_change':
            prompt = f'Find the missing number: {a+b} − □ = {a}.'; answer = b
            working = f'{a+b} − {a} = {b}.'
            example = 'For 1275 − □ = 1100, subtract 1100 from 1275 to get 175. Check 1275 − 175 = 1100.'
        elif family == 'context':
            prompt = f'A library lends {b} books and has {a} left. How many books did it have before lending them?'; answer = a+b
            working = f'{a} + {b} = {a+b}.'
            example = 'A library lends 175 books and has 1100 left. It started with 1100 + 175 = 1275 books.'
        else:
            prompt = f'Find the missing number: □ + {b} = {a+b}.'
            working = f'{a+b} − {b} = {a}.'
            example = 'For □ + 175 = 1275, subtract 175 to get 1100. Check 1100 + 175 = 1275.'
    support = {'strategy':rule,'hints':[rule,steps[0]+' '+steps[1],steps[2]],
               'teach_steps':[{'label':f'Step {i+1}','text':step} for i,step in enumerate(steps)],'worked_example':example}
    payload = {'operation':operation,'operands':[a,b],**extra,'arithmetic_extension':1,
               'question_family':f'grade5_{operation}_{family}','representation':'context' if family in ('context','groups','sharing','remainder','two_step') else 'equation' if 'missing' in family or operation=='equation' else 'symbolic',
               'evidence_type':'transfer' if family in ('context','groups','sharing','remainder','two_step','error') else 'procedural',
               'curriculum_alignment':code,'grade_band':5,'curriculum_level':5,
               'difficulty_band':'challenge' if challenge else 'instructional','grade5_support':support,
               'strategy_card':{'title':'Choose an efficient strategy','strategy':rule,'rule':rule,'steps':steps,'example':example}}
    return {'prompt':prompt,'answer_type':answer_type,'payload':payload,'answer':str(answer),'working':working}


def operation_for(question: legacy.Question) -> str | None:
    skill = (question.skill or '').split(':')[-1]
    if skill in ('written_subtraction', 'fact_recall_subtraction'):
        return 'subtraction'
    if skill == 'unknown_add_subtract':
        return 'equation'
    if skill in ('fact_recall_multiplication', 'equal_groups_total'):
        return 'multiplication'
    if skill == 'fact_recall_division':
        return 'division'
    if skill == 'efficient_multiply_divide':
        payload = v0330._payload(question)
        return 'division' if payload.get('operation') == 'division' or '÷' in question.prompt else 'multiplication'
    return None


def improve_worksheet(session: Session, worksheet: legacy.Worksheet, student_id: int, plan: dict[str, Any] | None = None) -> legacy.Worksheet:
    if worksheet.completed_at or worksheet.session_kind in ('diagnostic', 'parent_test'):
        return worksheet
    if any(q.attempts or q.hint_count or q.mentor_started or q.mentor_example_seen for q in worksheet.questions):
        return worksheet  # Resumed work retains its original mathematical content.
    if plan and (plan.get('purpose') in ('learn','prerequisite','review') or plan.get('evidence_focus') or plan.get('follow_through') in ('reteach','gather_more_evidence','check_independence')):
        return worksheet
    cache: dict[str, dict[str, Any]] = {}
    family_counts: dict[str, int] = defaultdict(int)
    challenge_used = False
    changed = False
    questions = sorted(worksheet.questions,key=lambda q:q.position)
    identities = {legacy.question_identity(q.prompt,v0330._payload(q)) for q in questions}
    for question in questions:
        payload = v0330._payload(question)
        operation = operation_for(question)
        if not operation or payload.get('arithmetic_extension') or question.attempts or question.hint_count or question.mentor_started:
            continue
        if plan and 'fact_recall' in question.skill:
            continue  # A targeted fact check remains a fact check.
        if question.skill not in cache:
            cache[question.skill] = v0330._question_evidence(session, student_id, question.skill)
        evidence = cache[question.skill]
        state = v0330._progression_state(evidence)
        if state not in ('secure','ready_to_progress'):
            continue
        if v0330._misconception_count(session,student_id,question.skill) >= v0330.THRESHOLDS.prerequisite_misconceptions:
            continue
        index = family_counts[operation]; family_counts[operation] += 1
        if index % 6 == 0:
            continue  # Retain a foundation/reconnect item in each six eligible items.
        challenge = state == 'ready_to_progress' and 'fact_recall' not in question.skill and not challenge_used and len(questions)>=5 and (not plan or plan.get('follow_through') not in ('check_independence','consolidate'))
        family = FAMILIES[operation][(worksheet.id+index-1)%len(FAMILIES[operation])]
        rng = random.Random(f'v0500:{worksheet.id}:{question.position}:{operation}')
        generated = None
        for _ in range(80):
            candidate = generate(operation,rng,challenge=challenge,family=family)
            identity = legacy.question_identity(candidate['prompt'],candidate['payload'])
            if identity not in identities:
                generated = candidate; identities.add(identity); break
        if generated is None:
            continue
        retained = {k:v for k,v in payload.items() if k in ('targeted_session','targeted_session_plan','adventure','story','mission','visual_key')}
        question.prompt = generated['prompt']; question.answer_type = generated['answer_type']
        question.correct_answer = generated['answer']; question.working = generated['working']
        readiness_skill = question.skill
        if 'fact_recall' in question.skill:
            question.skill = 'VC2M4N06:written_subtraction' if operation == 'subtraction' else 'VC2M4N06:efficient_multiply_divide'
        recorded_evidence = evidence if question.skill == readiness_skill else v0330._question_evidence(session,student_id,question.skill)
        recorded_state = state if question.skill == readiness_skill else v0330._progression_state(recorded_evidence)
        question.payload = json.dumps({**retained,**generated['payload'],
            'learning_purpose':'challenge' if challenge else 'current','learning_purpose_label':'Today’s challenge' if challenge else 'Practising this skill',
            'readiness_basis':{'skill':readiness_skill,'state':state},
            'progression_state':recorded_state,'adaptive_evidence':{'questions':recorded_evidence['questions'],'independent_accuracy':round(recorded_evidence['independent']*100),'support_dependency':round(recorded_evidence['support']*100)}})
        v0321._restore_runtime_annotations(question,worksheet)
        refreshed = v0330._payload(question)
        refreshed['mentor_context'] = v0310._question_context(question)
        question.payload = json.dumps(refreshed)
        challenge_used |= challenge; changed = True
    if changed:
        session.commit(); session.refresh(worksheet)
    return worksheet
