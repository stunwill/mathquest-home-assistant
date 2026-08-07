from __future__ import annotations

from collections import defaultdict
from contextvars import ContextVar
from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy

app = legacy.app
app.version = "0.6.0"

_original_make_question = legacy.make_question
_original_dashboard = legacy.dashboard
_adaptive_targets: ContextVar[dict[str, str]] = ContextVar("adaptive_targets", default={})

MASTERY_WEIGHTS = {0: 1.0, 1: 0.7, 2: 0.4}
REVIEW_INTERVALS = (1, 3, 7, 14)


def _question_mastery(question: legacy.Question) -> float:
    if not question.attempts:
        return 0.0
    if not any(attempt.correct for attempt in question.attempts):
        return 0.0
    return MASTERY_WEIGHTS.get(min(question.hint_count or 0, 2), 0.4)


def _topic_questions(session: Session, student_id: int, topic: str, limit: int = 40) -> list[legacy.Question]:
    return list(
        session.scalars(
            select(legacy.Question)
            .join(legacy.Worksheet)
            .where(
                legacy.Worksheet.student_id == student_id,
                legacy.Question.topic == topic,
                legacy.Question.answered_at.is_not(None),
            )
            .order_by(legacy.Question.answered_at.desc())
            .limit(limit)
        ).all()
    )


def _skill_review_state(questions: list[legacy.Question]) -> dict[str, Any]:
    grouped: dict[str, list[legacy.Question]] = defaultdict(list)
    for question in questions:
        grouped[question.skill.split(":", 1)[0]].append(question)

    best_code = None
    best_score = -1.0
    due_codes: list[str] = []
    now = datetime.utcnow()

    for code, rows in grouped.items():
        rows = sorted(rows, key=lambda q: q.answered_at or datetime.min, reverse=True)
        mastery = sum(_question_mastery(q) for q in rows[:8]) / max(1, len(rows[:8]))
        independent_streak = 0
        for q in rows:
            if _question_mastery(q) == 1.0:
                independent_streak += 1
            else:
                break
        interval = REVIEW_INTERVALS[min(independent_streak, len(REVIEW_INTERVALS) - 1)]
        last_seen = rows[0].answered_at or now
        days_since = max(0, (now - last_seen).days)
        due = days_since >= interval and mastery < 0.95
        if due:
            due_codes.append(code)
        score = (1.0 - mastery) * 2.2 + (1.2 if due else 0.0)
        if score > best_score:
            best_score = score
            best_code = code

    return {"target_code": best_code, "due_codes": due_codes}


def _topic_metrics(session: Session, student_id: int, topic: str) -> dict[str, Any]:
    rows = _topic_questions(session, student_id, topic)
    if not rows:
        return {
            "topic": topic,
            "questions": 0,
            "mastery": 0,
            "independent_accuracy": 0,
            "hint_rate": 0,
            "review_due": False,
            "target_code": None,
        }

    correct = [q for q in rows if any(a.correct for a in q.attempts)]
    independent = [q for q in correct if (q.hint_count or 0) == 0]
    hinted = [q for q in rows if (q.hint_count or 0) > 0]
    mastery = sum(_question_mastery(q) for q in rows) / len(rows)
    review = _skill_review_state(rows)
    return {
        "topic": topic,
        "questions": len(rows),
        "mastery": round(mastery * 100),
        "independent_accuracy": round(len(independent) / len(rows) * 100),
        "hint_rate": round(len(hinted) / len(rows) * 100),
        "review_due": bool(review["due_codes"]),
        "target_code": review["target_code"],
    }


def adaptive_weights(session: Session, student_id: int, topics: list[str]) -> list[float]:
    targets: dict[str, str] = {}
    result: list[float] = []
    for topic in topics:
        metrics = _topic_metrics(session, student_id, topic)
        if metrics["target_code"]:
            targets[topic] = metrics["target_code"]
        if not metrics["questions"]:
            result.append(1.0)
            continue
        mastery_gap = 1.0 - metrics["mastery"] / 100
        hint_pressure = metrics["hint_rate"] / 100
        due_boost = 0.8 if metrics["review_due"] else 0.0
        result.append(max(0.35, 0.7 + mastery_gap * 2.0 + hint_pressure * 1.2 + due_boost))
    _adaptive_targets.set(targets)
    return result


def targeted_make_question(topic: str, level: int, rng: Any):
    target = _adaptive_targets.get().get(topic)
    if target and rng.random() < 0.45:
        for _ in range(30):
            generated = _original_make_question(topic, level, rng)
            if generated[0].startswith(f"{target}:"):
                return generated
    return _original_make_question(topic, level, rng)


def adaptive_update_skill(session: Session, student_id: int, topic: str) -> None:
    skill = session.scalar(
        select(legacy.Skill).where(legacy.Skill.student_id == student_id, legacy.Skill.topic == topic)
    )
    if not skill:
        skill = legacy.Skill(student_id=student_id, topic=topic)
        session.add(skill)
        session.flush()

    rows = _topic_questions(session, student_id, topic, 20)
    if not rows:
        return

    mastery = sum(_question_mastery(q) for q in rows) / len(rows)
    conventional_accuracy = sum(1 for q in rows if any(a.correct for a in q.attempts)) / len(rows)
    attempt_seconds = [a.seconds for q in rows for a in q.attempts]
    skill.attempts = len(rows)
    skill.rolling_accuracy = conventional_accuracy
    skill.avg_seconds = sum(attempt_seconds) / max(1, len(attempt_seconds))

    if len(rows) >= 12 and mastery >= 0.85:
        skill.level = min(8, skill.level + 1)
    elif len(rows) >= 8 and mastery < 0.65:
        skill.level = max(1, skill.level - 1)
    skill.highest_level = max(skill.highest_level, skill.level)


HINT_STRATEGIES = {
    "decimal_place_value": (
        "Start immediately to the right of the decimal point. The first digit is tenths and the second is hundredths.",
        "Point to the second digit after the decimal point. That is the place the question is asking about.",
    ),
    "number_sequences": (
        "Compare neighbouring numbers to find how much the sequence changes each time.",
        "Find the difference between the first two numbers, then apply that same change to the last number shown.",
    ),
    "equivalent_fractions": (
        "Equivalent fractions change the numerator and denominator by the same multiplication factor.",
        "Work out what the original denominator was multiplied by, then multiply the numerator by that same number.",
    ),
    "fraction_number_line": (
        "Convert each whole into a fraction using the denominator already shown.",
        "Multiply the whole number by the denominator first, then add the existing numerator.",
    ),
    "powers_of_ten": (
        "Think about how place value changes when multiplying or dividing by 10, 100 or 1000.",
        "Count the zeros in the power of ten. That tells you how many place-value positions the digits move.",
    ),
    "efficient_add_subtract": (
        "Split the numbers into hundreds, tens and ones so the calculation is easier to manage.",
        "Start with the largest place values, then combine the smaller parts.",
    ),
    "efficient_multiply_divide": (
        "Partition the larger number into tens and ones before multiplying.",
        "Multiply each part separately, then combine those partial results.",
    ),
    "estimation_reasonableness": (
        "Round each number before calculating. The question tells you which place value to round to.",
        "Look at the digit immediately to the right of the rounding place. Five or more rounds up.",
    ),
    "money_change": (
        "Change is the amount paid minus the price.",
        "Line up dollars and cents, then subtract the item cost from the amount paid.",
    ),
    "mathematical_modelling": (
        "Turn the story into operations. First find the total inside the equal groups.",
        "Multiply the number of groups by the amount in each group before adding anything extra.",
    ),
    "unknown_add_subtract": (
        "Use the inverse operation to undo what happened to the unknown number.",
        "If a number was added to the box, subtract that number from the total.",
    ),
    "fact_families": (
        "Multiplication and division are inverse operations and belong to the same fact family.",
        "Use the multiplication fact in the question to identify the missing factor in the division.",
    ),
    "perimeter": (
        "Perimeter is the distance all the way around the outside of a shape.",
        "For a rectangle, add the length and width, then double that amount.",
    ),
    "area": (
        "Area measures the space inside the rectangle.",
        "Multiply the rectangle's length by its width.",
    ),
    "duration_conversion": (
        "Convert everything to the same unit before combining the times.",
        "Each hour contains 60 minutes. Convert the hours first, then add the extra minutes.",
    ),
    "angle_names": (
        "Compare the angle with a right angle, a straight angle and a full turn.",
        "A right angle is 90° and a straight angle is 180°. Use those landmarks to classify it.",
    ),
    "grid_references": (
        "Grid references are read in a consistent order: column first, then row.",
        "Write the letter for the column first, followed by the row number.",
    ),
    "data_frequency": (
        "Frequency means how often a value appears.",
        "Count how many times each value occurs and choose the one with the largest count.",
    ),
    "likelihood": (
        "Compare how many outcomes favour each choice.",
        "The colour with more counters has the greater chance of being selected.",
    ),
}


def contextual_hint_text(question: legacy.Question, hint_number: int) -> str:
    key = question.skill.split(":", 1)[-1]
    strategy = HINT_STRATEGIES.get(key)
    if strategy:
        return strategy[min(max(hint_number, 1), 2) - 1]
    if hint_number == 1:
        return "Identify what the question is asking you to find, then choose the operation or comparison that matches it."
    return "Break the problem into smaller steps. Complete only the first step, check it, then continue."


def adaptive_dashboard(session: Session, student_id: int) -> dict[str, Any]:
    data = _original_dashboard(session, student_id)
    metrics = [_topic_metrics(session, student_id, topic) for topic in legacy.LEVEL4_STRANDS]
    established = [m for m in metrics if m["questions"]]
    recommended = min(established, key=lambda m: (m["mastery"], -m["hint_rate"])) if established else None
    due = [m["topic"] for m in established if m["review_due"]]
    data["adaptive_learning"] = {
        "enabled": True,
        "mastery_weights": {"independent": 1.0, "hint_1": 0.7, "hint_2": 0.4, "incorrect": 0.0},
        "recommended_topic": recommended["topic"] if recommended else None,
        "review_due_topics": due,
        "topics": metrics,
    }
    return data


legacy.weights = adaptive_weights
legacy.make_question = targeted_make_question
legacy.update_skill = adaptive_update_skill
legacy.hint_text = contextual_hint_text
legacy.dashboard = adaptive_dashboard


def _printable_answer_area(pdf: canvas.Canvas, y: float, question: legacy.Question) -> float:
    payload = {}
    try:
        payload = legacy.json.loads(question.payload)
    except Exception:
        payload = {}
    if question.answer_type == "choice" and payload.get("choices"):
        for choice in payload["choices"]:
            pdf.drawString(72, y, f"○  {choice}")
            y -= 16
        return y - 4
    pdf.line(72, y - 8, 530, y - 8)
    return y - 28


def _worksheet_pdf(worksheet: legacy.Worksheet, student: legacy.User) -> bytes:
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4

    def header() -> float:
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(48, height - 50, "MathQuest Worksheet")
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width - 48, height - 50, "Status: In Progress")
        pdf.drawString(48, height - 72, f"Student: {student.display_name}")
        pdf.drawString(48, height - 88, f"Date: {worksheet.worksheet_date.strftime('%d %B %Y')}")
        topic = (worksheet.selected_topic or "mixed").replace("_", " ").title()
        pdf.drawString(48, height - 104, f"Quest: {topic}")
        pdf.line(48, height - 114, width - 48, height - 114)
        return height - 140

    y = header()
    for index, question in enumerate(sorted(worksheet.questions, key=lambda q: q.position), start=1):
        prompt = f"{index}. {question.prompt}"
        words = prompt.split()
        lines: list[str] = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if pdf.stringWidth(trial, "Helvetica", 11) > 480 and current:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
        required = 22 * len(lines) + 48
        if y - required < 55:
            pdf.showPage()
            y = header()
        pdf.setFont("Helvetica", 11)
        for line in lines:
            pdf.drawString(54, y, line)
            y -= 16
        y -= 4
        y = _printable_answer_area(pdf, y, question)

    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawCentredString(width / 2, 24, "MathQuest by Stu • Worksheet started and saved as In Progress")
    pdf.save()
    return output.getvalue()


@app.post("/api/worksheets/today/print")
def print_today_worksheet(
    selection: legacy.WorksheetCreateIn,
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    if user.role != "student":
        raise HTTPException(403, "Student access required")

    existing = session.scalar(
        select(legacy.Worksheet).where(
            legacy.Worksheet.student_id == user.id,
            legacy.Worksheet.worksheet_date == date.today(),
        )
    )
    if existing and existing.completed_at:
        raise HTTPException(400, "Today's worksheet is already completed")

    if not existing:
        legacy.today_ws(selection, user, session)
        existing = session.scalar(
            select(legacy.Worksheet).where(
                legacy.Worksheet.student_id == user.id,
                legacy.Worksheet.worksheet_date == date.today(),
            )
        )
    if not existing:
        raise HTTPException(500, "Unable to prepare worksheet")

    existing.status = "in_progress"
    existing.last_active_at = datetime.utcnow()
    if existing.started_at is None:
        existing.started_at = datetime.utcnow()
    first = sorted(existing.questions, key=lambda q: q.position)[0] if existing.questions else None
    if first and existing.current_question_id is None:
        existing.current_question_id = first.id
        first.state = "active"
        if first.first_viewed_at is None:
            first.first_viewed_at = datetime.utcnow()
    session.commit()

    content = _worksheet_pdf(existing, user)
    filename = f"mathquest-{existing.worksheet_date.isoformat()}-{existing.selected_topic or 'mixed'}.pdf"
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-MathQuest-Worksheet-Status": "in_progress",
        },
    )
