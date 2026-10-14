# MathQuest 0.50.0 installed-version acceptance

Status: Pending installed Home Assistant and physical-device validation.

## Dashboard rewards

- Back up `/data` before installing the reviewed release. Record Sienna's existing XP and highest earned level from the existing dashboard API before the update.
- Verify `/api/health` reports 0.50.0 and the dashboard displays that same persisted XP, current level, and progress towards the next level. The existing model remains 250 XP per reward level. Reward level is separate from curriculum placement.
- Reload several times, restart the add-on, and verify XP and historical rewards do not change. Complete one worksheet and verify the reward appears once after returning to the dashboard.
- Test another learner account, sign out, and sign back in. Verify rewards belong to the signed-in learner, with no stale learner display during loading.
- Check iPhone portrait, iPad landscape and desktop. Confirm the compact rewards strip does not crowd out the primary learning action and its progress bar has an accessible label/value.

## Worksheet final action

- For short, standard and longer worksheets, answer the second-last question. The feedback action must say Next question and advance to the actual final question.
- Answer the final question with all earlier work resolved. The feedback action must say Finish worksheet.
- Skip questions, answer out of sequence, use the question map, revisit earlier answers, exit and resume. The finish action must never appear on an earlier question simply because most questions are answered.
- When skipped work remains, retain the normal skipped review flow. The explicit finish-with-skipped action is available only on the actual final question under the existing completion rules. Unanswered work must still block completion.

## Mathematics and adaptive integrity

- Compare newly created Number & Algebra and recommended targeted worksheets for learners with repeated independent skill success versus learners who still use hints or Math Mentor.
- Ready learners should receive varied four-digit subtraction and regrouping across zero, larger products/quotients, inverse relationships, missing values, estimates and applied reasoning. Strong readiness permits a bounded challenge, rather than harder questions everywhere.
- Reteach, prerequisite, review, diagnostic and explicit smaller-step sessions must retain their appropriate content. One correct answer, XP level or general overall accuracy must not manufacture skill readiness.
- Check generated answers and support against the actual problem, including missing dividend/factor questions and explicit remainder contexts. Verify worked examples use different values and the appropriate mathematical structure.
- Finish a targeted follow-up and verify its support-aware outcome remains associated with the previous decision. Previewing the next step must not consume it.
- Open older completed worksheets and resume existing work. Question IDs, prompts, answers and history must remain unchanged.

## Curriculum and evidence compatibility

Existing learning-evidence keys remain stable. New question payloads include separate `curriculum_alignment` metadata: VC2M4N06/VC2M4A01 for prerequisite strategies and unknown additive values, VC2M5N06 for larger multiplication, VC2M5N07 for division/remainders, VC2M5N08 for reasonableness and VC2M5A02 for multiplicative inverse number sentences.

Official curriculum references checked for this release:

- https://victoriancurriculum.vcaa.vic.edu.au/Search?q=VC2M4N06
- https://victoriancurriculum.vcaa.vic.edu.au/Search?q=VC2M5N06
- https://victoriancurriculum.vcaa.vic.edu.au/Search?q=VC2M5N07
- https://victoriancurriculum.vcaa.vic.edu.au/Search?q=VC2M5N08
- https://victoriancurriculum.vcaa.vic.edu.au/Search?q=VC2M5A02

Automated test evidence accompanies the PR. This checklist does not claim access to Sienna's live database or physical-device/installed ingress acceptance.
