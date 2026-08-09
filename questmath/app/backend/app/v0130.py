from __future__ import annotations

import json
import re
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120

app = v0120.app
app.version = '0.13.0'


FRACTION_RE = re.compile(r'(?<!\d)(\d{1,2})\s*/\s*(\d{1,2})(?!\d)')
DECIMAL_RE = re.compile(r'(?<!\d)(\d+\.\d+)(?!\d)')
DEGREE_RE = re.compile(r'(?<!\d)(\d{1,3})\s*°')


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _fractions(prompt: str) -> list[dict[str, int | str]]:
    result: list[dict[str, int | str]] = []
    seen: set[tuple[int, int]] = set()
    for numerator_text, denominator_text in FRACTION_RE.findall(prompt or ''):
        numerator = int(numerator_text)
        denominator = int(denominator_text)
        if denominator <= 0 or numerator < 0 or numerator > denominator or denominator > 12:
            continue
        key = (numerator, denominator)
        if key in seen:
            continue
        seen.add(key)
        result.append({'numerator': numerator, 'denominator': denominator, 'label': f'{numerator}/{denominator}'})
        if len(result) == 2:
            break
    return result


def visual_hint_for(question: legacy.Question, hint_level: int | None = None) -> dict[str, Any] | None:
    level = min(2, max(1, hint_level or question.hint_count or 1))
    prompt = question.prompt or ''
    skill = question.skill.split(':', 1)[-1]
    payload = _payload(question)
    visual = payload.get('visual') if isinstance(payload.get('visual'), dict) else {}

    fractions = _fractions(prompt)
    if len(fractions) >= 2:
        return {
            'type': 'fraction_pies',
            'hint_level': level,
            'items': fractions,
            'show_bars': level >= 2,
            'instruction': 'Compare the shaded amount in each equal-sized whole. Which one covers more of the circle?',
            'accessibility_text': 'Two equal-sized fraction circles are divided into the denominators shown. The numerator number of slices is shaded in each circle.',
        }
    if len(fractions) == 1 and 'fraction' in skill:
        return {
            'type': 'fraction_pie',
            'hint_level': level,
            'item': fractions[0],
            'show_bar': level >= 2,
            'instruction': 'Use the shaded slices to picture how much of one whole this fraction represents.',
            'accessibility_text': 'A fraction circle is divided into equal slices and the numerator number of slices is shaded.',
        }

    if visual.get('type') == 'number_line':
        return {
            'type': 'number_line',
            'hint_level': level,
            'min': visual.get('min', 0),
            'max': visual.get('max', 1),
            'steps': max(1, int(visual.get('steps', 1))),
            'instruction': 'Count the equal spaces first, then locate the value one step at a time.',
        }
    if visual.get('type') == 'clock':
        return {
            'type': 'clock',
            'hint_level': level,
            'hour': int(visual.get('hour', 12)),
            'minute': int(visual.get('minute', 0)),
            'instruction': 'Read the minute hand first, then use the shorter hour hand to identify the hour.',
        }
    if visual.get('type') == 'angle':
        return {
            'type': 'angle',
            'hint_level': level,
            'degrees': int(visual.get('degrees', 90)),
            'instruction': 'Compare this angle with a right angle (90°) and a straight angle (180°).',
        }
    if visual.get('type') == 'grid':
        return {
            'type': 'grid',
            'hint_level': level,
            'columns': visual.get('columns', ['A', 'B', 'C', 'D', 'E']),
            'rows': int(visual.get('rows', 6)),
            'target': visual.get('target'),
            'instruction': 'Find the column first, then move to the row.',
        }

    decimal_match = DECIMAL_RE.search(prompt)
    if decimal_match and ('place' in skill or 'decimal' in skill):
        value = decimal_match.group(1)
        whole, decimal = value.split('.', 1)
        digits = [
            {'place': 'ones', 'digit': whole[-1] if whole else '0'},
            {'place': 'tenths', 'digit': decimal[0] if len(decimal) > 0 else '0'},
            {'place': 'hundredths', 'digit': decimal[1] if len(decimal) > 1 else '0'},
        ]
        return {
            'type': 'place_value',
            'hint_level': level,
            'value': value,
            'digits': digits,
            'instruction': 'Start at the decimal point. Move one place right for tenths and two places right for hundredths.',
        }

    degree_match = DEGREE_RE.search(prompt)
    if degree_match and 'angle' in skill:
        return {
            'type': 'angle',
            'hint_level': level,
            'degrees': int(degree_match.group(1)),
            'instruction': 'Compare the angle with the 90° and 180° landmarks before naming it.',
        }

    if skill in {'area', 'perimeter'}:
        numbers = [int(x) for x in re.findall(r'(?<!\d)(\d{1,3})(?!\d)', prompt)[:2]]
        if len(numbers) == 2:
            return {
                'type': 'rectangle',
                'hint_level': level,
                'length': numbers[0],
                'width': numbers[1],
                'mode': skill,
                'instruction': 'Area is the space inside the rectangle. Perimeter is the distance around the outside.',
            }

    if skill == 'number_sequences':
        numbers = [int(x) for x in re.findall(r'(?<!\d)-?\d+(?!\d)', prompt)[:6]]
        if len(numbers) >= 3:
            return {
                'type': 'sequence',
                'hint_level': level,
                'values': numbers,
                'instruction': 'Look at the jump from one number to the next. Is the same change repeating?',
            }

    return None


@app.get('/api/questions/{qid}/hint-visual')
def hint_visual(qid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not worksheet or worksheet.student_id != user.id:
        raise HTTPException(403, 'Question does not belong to this student')
    return {
        'question_id': question.id,
        'hint_count': question.hint_count or 0,
        'visual': visual_hint_for(question),
    }


@app.get('/api/v0130/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.13.0',
        'visual_hints': True,
        'visual_hint_types': ['fraction_pies', 'fraction_pie', 'number_line', 'place_value', 'clock', 'angle', 'grid', 'rectangle', 'sequence'],
        'hint_answers_revealed': False,
        'inherits_v0120': True,
    }


# v0.12.1 deliberately keeps the SPA catch-all last. Registering new v0.13 GET
# endpoints happens after importing v0.12, so move the fallback to the end again.
v0120._move_spa_fallback_to_end()
