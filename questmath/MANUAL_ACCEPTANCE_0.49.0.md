# MathQuest 0.49.0 installed-version validation

Status: Pending installed Home Assistant and physical-device validation.

1. Back up `/data`, install the release after review/merge, and verify startup plus `/api/health` report 0.49.0. Existing learners, diagnostic evidence, worksheet history and settings must remain available.
2. Open MathQuest through Home Assistant ingress on iPhone portrait, iPad landscape with a physical keyboard and desktop. Verify login, Today's Focus, Best Next Step, answer interaction, support controls and worksheet resume.
3. Complete a targeted subtraction session with incorrect attempts. Preview the next step repeatedly, restart the add-on and confirm the same pending learning intent remains. Start the recommended session twice and confirm it resumes one follow-up worksheet.
4. Complete the follow-up independently. Confirm the completion message recognises independence, Parent Dashboard shows what was tried and what changed, and the next recommendation no longer repeats the consumed reteach decision.
5. Repeat with hints and Math Mentor. Supported success must not be presented as independent mastery. Skip target questions and confirm MathQuest requests more evidence.
6. For two linked subtraction sessions showing continued difficulty, confirm the next session checks subtraction without regrouping. Success on that smaller step must lead back to an independent check of the full skill, rather than mastery or automatic progression.
7. For a transfer follow-up, familiar question families alone must not confirm transfer. Check varied-family evidence where the existing generator supports it.
8. Open older completed targeted worksheets without lineage. Confirm they remain reviewable and the Parent Dashboard handles missing outcome data safely.

This checklist does not claim physical-device, ingress or installed-data acceptance has been performed. CI separately validates the ARM64 image build, add-on startup and health version.
