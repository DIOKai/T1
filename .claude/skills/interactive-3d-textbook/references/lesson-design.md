# Lesson design: predict → test → prove

Read this before writing the lesson text, prediction options, flap, stamp, quiz or teacher notes. The "A lesson page is done when…" checklist near the end is the acceptance test.

Contents: 1 Predict–Observe–Explain · 2 PhET design principles · 3 Explorable explanations · 4 Feedback and the stamp · 5 Synchronised representations · 6 Energy misconceptions (distractors) · 7 Accessibility · 8 Teacher's guide · Done checklist · Sources

For subjects other than energy (seepage, circuits, cells…), §6 is only an example: find that subject's documented misconceptions (physics/engineering education research, the exam board's examiner reports, or the user's own teaching experience) and label which kind of source each distractor comes from.

Research date: 2026-10-28. Every claim has a source URL. **[2nd]** means it comes from a secondary summary (abstract page, blog, or citing paper) and I did not read the primary text. **UNVERIFIED** means I could not confirm it. **[heuristic]** marks design rules I derived myself; they are not research findings.

Reference genre: *Every Joule* (Techartist). Its public landing page describes 10 GCSE/IGCSE energy lessons. Each diagram is a 3D pop-up, energy is shown as coloured flow between stores, and each idea follows **predict, test, prove**: the student lifts a flap to see the explanation and earns a stamp. The book includes teacher notes and source references. The landing page does not describe its sliders, readouts or quiz format. https://iamtechartist.com/every-joule/

---

## 1. Predict–Observe–Explain (POE)

**Origin.** White & Gunstone, *Probing Understanding* (Falmer Press, 1992; Routledge reissue 2014) set out POE as a way to draw out each student's prediction about a specific event and their reasons for it. Students predict, then observe and record what actually happens, then reconcile any conflict between the two. https://arbs.nzcer.org.nz/node/7187 · https://interactivetextbooks.tudelft.nl/showthephysics/Pedagogy/PoE.html. It descends from Champagne, Klopfer & Anderson's "Demonstrate-Observe-Explain" (1979) [2nd] https://www.researchsquare.com/article/rs-3401672/latest

**Evidence that predicting first helps**
- Crouch, Fagen, Callan & Mazur, "Classroom demonstrations: Learning tools or entertainment?", *Am. J. Phys.* 72(6), 835–838 (2004), doi:10.1119/1.1707018. Students who only watched a demo understood the concept no better than students who never saw it. Students who predicted the outcome first showed "significantly greater understanding". https://www.compadre.org/portal/items/detail.cfm?ID=2329
  - A blog reports gains of about 0.09 for observe-only, 0.36 for predict + observe, and 0.45 for predict + observe + discuss. **[2nd, figures UNVERIFIED against the paper]** https://mirjamglessmer.com/2014/06/01/how-to-make-demos-useful-in-teaching/
  - A replication with 116 astronomy undergraduates found weaker effects, so don't oversell it. [2nd, same search; see the Mazur page] https://mazur.harvard.edu/presentations/classroom-demonstrations-learning-tools-or-entertainment
- Brod (2021), "Generative learning: Which strategies for what age?", *Educ. Psychol. Rev.* 33(4), 1295–1318. This is a narrative review, not a meta-analysis. Predicting is one of six generative strategies, and all six are effective for university students. Evidence for younger students is **mixed**. https://www.pedocs.de/volltexte/2021/23704/pdf/EPR_2021_4_Brod_Generative_Learning_A.pdf
- Metcalfe (2017), "Learning from errors", *Annu. Rev. Psychol.* 68, 465–489. Errors followed by corrective feedback help learning, especially when the learner was confident in the wrong answer (the hypercorrection effect) [2nd, abstract]. https://annualreviews.org/doi/abs/10.1146/annurev-psych-010416-044022

**Rules for writing prediction options**
1. **Build the distractors from documented misconceptions.** Sadler (1998, *JRST* 35, 265–296) argues for "distractor-driven" items whose wrong answers are the most common student ideas, so that every wrong choice tells you something [2nd]. https://users.nber.org/~sewp/events/2004.05.28/Sadler_PsychometricModels.pdf · https://www.gse.harvard.edu/ideas/news/99/04/research-finds-revolutionary-discoveries-cognitive-sciences-are-not-reflected-high
2. **Use 3 options by default, never more than 4.** Rodriguez (2005, *EM:IP* 24(2), 3–13), a meta-analysis of 80 years of research, found three options optimal "in most settings" [2nd]. https://tipsforteachers.substack.com/p/research-bite-20-three-options-are. Example pattern: "goes higher / same height / lower".
3. **Commit before the reveal.** Lock the choice before the experiment runs. Predicting only helps if the student commits before seeing the result (Crouch et al. 2004, above).
4. **Ask for a confidence rating (optional).** A one-tap "sure / not sure" makes it possible to address high-confidence errors explicitly (Metcalfe 2017, above). [heuristic]
5. **No trick answers.** Each option must be a position a real student would hold, and the experiment must settle the question cleanly. Turn off friction when the point is mass independence, and add friction in a later step. [heuristic; mirrors PhET's tab-by-tab "fading", §2]
6. **Ask a "why" after the prediction.** Mazur's discussion condition gave the largest gain [2nd], and the E in POE is the student's explanation (White & Gunstone).

---

## 2. PhET Interactive Simulations design principles

**PhET's stated principles** (official About page): encourage scientific inquiry; provide interactivity; **make the invisible visible**; show visual mental models; **include multiple representations** (object motion, graphs, numbers); use real-world connections; give users **implicit guidance (e.g., by limiting controls)** in productive exploration; make sims flexible for many classroom uses. The page also says users get **immediate feedback** about the effect of their changes. https://phet.colorado.edu/en/about

**Implicit scaffolding.** Podolefsky, Moore & Perkins, arXiv:1306.6544 (2013, rev. 2014), read from the full text and worked through *Energy Skate Park: Basics*. https://arxiv.org/abs/1306.6544
- Definition: guidance built from affordances, constraints, cueing and feedback, with no explicit instructions. Their phrase is that it "guides without students feeling guided."
- **Productive constraints.** These make the wrong action impossible, as with a push-only door. Slider ranges and other boundary conditions are "both a productive constraint and a significant affordance". Students explore the extremes, so choose ranges whose endpoints show something useful.
- **Fade the scaffolding across screens.** The Intro tab fixes friction at zero and keeps the skater stuck to the track. Later tabs relax this (Stick to Track can be turned off, friction can be increased).
- **Representations start closed.** The bar graph, pie chart and speedometer start closed so learners are not overwhelmed, and so that each one draws attention when it is opened. They are toggled with checkboxes. The bar graph checkbox sits at the top of the toolbox, which cues students to use it first.
- **Real-time, coordinated representations.** Moving the mass slider changes the bars and the pie immediately. Two energy views let a student use the familiar one to make sense of the other.
- **Nothing buried in menus.** Every control is visible and gives immediate feedback.
- **Minimal text.** "The text on the graph is minimal, promoting sense" making. PhET's older Look-and-Feel guide recommends 1–3-word text strings and calls text a distraction in the play area [2nd]. https://PHet.colorado.edu/publications/PhET%20Look%20and%20Feel.pdf
- **Feedback.** Changes in motion, colour, size and readout values give immediate feedback "cueing the student to try that action again".

**Engaged exploration.** Podolefsky, Perkins & Adams, *Phys. Rev. ST PER* 6, 020117 (2010), open access, define engaged exploration as students interacting, making sense, and exploring mainly through their own questions. https://link.aps.org/doi/10.1103/PhysRevSTPER.6.020117. Adams et al. (2008, *J. Interactive Learning Research* 19) ran more than 275 interviews. They found sims teach best when the student's own questions drive the interaction, and that an unintuitive interface pulls attention onto operating the sim instead of the physics [2nd]. https://ej.issuelab.org/resource/a-study-of-educational-simulations-part-ii-interface-design

**Rules for this textbook**
- In the first step of each lesson, show one experiment with at most 2–3 controls. Unlock more controls on later steps (fading).
- Start the energy bars, pie and readouts closed or minimal, and let the student open them.
- Set slider ranges so that both ends are informative (for example, a friction slider whose top end visibly stops the object).
- Keep labels to 1–3 words in the 3D scene and put any longer explanation behind the flap.

---

## 3. Explorable explanations

**Bret Victor, "Explorable Explanations" (10 Mar 2011)** https://worrydream.com/ExplorableExplanations/
- *Reactive documents*: the author's model is live in the text. Readers change the assumptions and watch the conclusions update, which forces the author to show their work.
- *Explorable examples*: adjustable examples replace static figures. Victor says this "makes the abstract concrete". The author still guides the reader, and the interaction supports the argument instead of replacing it.
- *Contextual information*: terms and related material can be looked up in place, so readers can "learn related material just-in-time".

**Bret Victor, "Kill Math" (Apr 2011).** His umbrella project for solving problems of quantity with concrete representations and intuition-guided exploration, including a "scrubbing calculator" where you drag numbers to adjust them. https://worrydream.com/KillMath (summary: https://futureofcoding.org/notes/bret-victor/kill-math)

**Nicky Case**
- "How to Explain Things Real Good" (18-minute talk, June 2022). Its tips: show what made you care; show, then tell; connect with "therefore / but", not "and then"; write a draft, then cut 10%; do real tests early and often [2nd: list summary]. https://href.leiden.digital/entry/38 · https://ncase.me/archive
- "Explorable Explanations: The Plan" (22 Mar 2015) is mostly about building the community, but it warns against a hard definition of what counts as an explorable. https://blog.ncase.me/explorable-explanations-the-plan
- Case's definition of an explorable, as quoted on a course page: something that teaches, and is "more interactive than a boring ol' quiz with only one right answer" [2nd]. https://redblobgames.com/x/2306-educ432
- The Explorables Jam tip list includes Case's "make everything bouncy". https://explorabl.es/jam/
- A guide titled "How I Make Explorable Explanations" is listed in https://github.com/blob42/awesome-explorables, but **I could not retrieve its text (UNVERIFIED content).**

**Takeaways for the lesson page**
- **One idea per page or step.** "Show, then tell" fits predict → test → prove exactly: the experiment shows, the flap tells.
- **The reader controls the model.** Every number in the explanation that comes from the experiment should be live, recomputed from the student's own run (reactive document).
- **Show the invisible quantity.** Energy, stores and flows get a visual form (PhET's "make the invisible visible").
- Open each lesson with a hook ("what made you care"). Chain steps with "but…" and "therefore…".
- Put definitions in hover/tap pop-overs instead of linking to another page (contextual information).

---

## 4. Feedback and reward (the stamp)

- **Feedback should be about the task, not the student.** Hattie & Timperley (2007, *Rev. Educ. Res.* 77(1), 81–112) describe four levels: task, process, self-regulation, and self. Task, process and self-regulation feedback produce gains. Self-level praise ("clever!") generally does not, because it doesn't say what to do next [2nd]. https://www.bera.ac.uk/blog/how-to-optimise-the-use-of-hattie-and-timperleys-feedback-levels-for-student-learning
- **Wrong predictions are useful.** Errors followed by corrective feedback improve learning, and confident errors are the most correctable (Metcalfe 2017, above). The reveal for a wrong prediction should name the misconception behind the option the student picked, without judging them.
- **Be careful with extrinsic rewards.** Deci, Koestner & Ryan (1999, *Psych. Bull.* 125, 627–668), a meta-analysis of 128 experiments, found that tangible rewards undermine intrinsic motivation. The verbal-reward result is more nuanced, and the size of the effect is still debated. https://home.ubalt.edu/ntygmitc/642/Articles%20syllabus/Deci%20Koestner%20Ryan%20meta%20IM%20psy%20bull%2099.pdf · https://utupub.fi/handle/10024/173853
- **Badges and leaderboards can backfire.** Hanus & Fox (2015, *Computers & Education* 80, 152–161): over a 16-week course, the gamified class (badges and leaderboard) showed lower intrinsic motivation, satisfaction and final exam scores than the control class (n≈80, one study) [2nd]. https://www.smhp.psych.ucla.edu/pdfdocs/gamil.pdf
- **Avoid seductive details.** Interesting but irrelevant material reduces learning (Harp & Mayer 1998, *J. Educ. Psych.* 90, 414–434; Mayer's coherence principle) [2nd]. https://www.cambridge.org/core/books/abs/multimedia-learning/coherence-principle/4E80B70CB76E2166B76E5653EBDE7D3E

**Rules** [heuristic, derived from the sources above]
- Award the stamp for **completing the full loop** (predict + test + open the flap). An optional second mark can show a correct prediction. That way a wrong guess still finishes the page and there is no reason to skip predicting.
- Show **no points, streaks or leaderboards**, and never show a red ✗ for a prediction. Use neutral wording such as "Surprised? Here's why."
- Write the stamp text about the physics ("Mass cancels out"), not about the student ("Genius!").
- Keep the stamp animation short (under about 600 ms), turn it off under reduced motion (§7), and don't cover the experiment with it.

---

## 5. Multiple synchronised representations

- Ainsworth's DeFT framework (2006, *Learning and Instruction* 16(3), 183–198) names the design parameters for multiple representations: how many, how information is split between them, their types, their order, and how much help learners get translating between them. Their functions are to complement each other, to constrain interpretation, and to build deeper understanding [2nd: abstract and citing papers]. https://nottingham-repository.worktribe.com/output/23577631/deft-a-conceptual-framework-for-considering-learning-with-multiple-representations
- PhET: representations run "in real time and in coordination", and the familiar one supports the unfamiliar one (arXiv:1306.6544, above).

**Rules**
- One state object drives every view (3D glow/flow, energy bars, equation with substituted numbers, numeric readout). Update every view in the same animation frame, so no representation ever disagrees with another. [heuristic]
- **Translation help (DeFT):** highlight the matching bar segment, equation term and readout when the student hovers or focuses any one of them. Use the same colour per energy store in every view. [heuristic, based on DeFT's "support for translation"]
- **Order:** open the most concrete view first (motion and glow), then the bars, then the equation (PhET's closed-by-default, top-to-bottom cueing).
- **Units:** use SI symbols, with a space between the number and the unit (e.g., "4.9 J", "2.0 m/s"), per NIST SP 811 / the SI Brochure. https://www.nist.gov/pml/special-publication-811 [I did not re-check the section number]
- **Significant figures** [heuristic]: show 2–3 sig figs in live readouts, and never more than the input slider's precision supports. Use fixed decimals while a value is changing so the digits don't jump around. Round only for display and never round internally. Totals must still add up exactly (display "Total 10.0 J" computed from the unrounded sum, and add a footnote if the parts appear to add up to 9.9).
- Readouts on **sliders** must show value and unit (see §7, `aria-valuetext`).

---

## 6. Energy misconceptions to use as distractors

| Misconception (distractor) | Correct idea | Source |
|---|---|---|
| "There is less energy at the end than at the start / energy gets used up" | Energy only shifts between stores, and the total stays the same | IOP Spark "Energy can run out" (Wrong Track / Right Lines). https://spark.iop.org/energy-can-run-out |
| "Energy disappears because of friction" | Where energy seems lost, something has been warmed: it ends up in thermal stores (air, surfaces) | IOP Spark (pendulum/friction guidance), via https://spark.iop.org/collections/shifting-energy-between-stores-teaching-and-learning-issues [2nd]. Oak National notes pupils miss that surroundings heat up: https://thenational.academy/teachers/programmes/physics-secondary-ks4-foundation-edexcel/units/energy-of-moving-objects/lessons/efficiency-in-terms-of-useful-energy-transferred |
| "Energy is a fluid / substance that flows" | Energy is an accounting quantity tracked across stores | IOP Spark: https://spark.iop.org/many-students-see-energy-intangible-fluid-flows-one-place-or-object-another-during-process |
| "Energy belongs to living things / fuels / electricity" | Energy is a property of any system | IOP Spark: https://spark.iop.org/many-students-associate-energy-humans-and-other-living-things · https://spark.iop.org/many-students-also-associate-energy-fuels-and-electricity |
| "Biological processes use energy up" | Conserved in living systems too | https://spark.iop.org/many-students-do-not-think-energy-conserved-biological-processes-and-see-these-either-using-energy |
| "Heavier objects move faster" (heavier skater/ball is faster at the bottom) | On a frictionless track, mass cancels: v = √(2gh) | Observed in a PhET interview and attributed to a "well-documented student intuition that heavy objects move faster" (Hestenes, Wells & Swackhamer 1992, among others), arXiv:1306.6544 full text |
| "Heavier ball rises higher" on the far side | Same height without friction (mass cancels) | A plausible extension of the row above. **UNVERIFIED** as a separately documented misconception |
| Watts' seven alternative frameworks: human-centred, depository, ingredient, obvious activity, product, functional, flow-transfer | — | Watts (1983), *Phys. Educ.* 18, 213–217 [2nd]. https://arxiv.org/pdf/1407.5533 |

IOP's advice: have students look for **every** store that fills, including small ones, instead of just labelling energy as "dissipated" (energy-can-run-out page, above). In this textbook, show the thermal store glowing when friction is on.

## 6a. Finding misconceptions for other subjects (source ladder)

For topics without a ready table (soil mechanics, circuits, chemistry, biology), work down this list and stop at the first rung that gives you a usable wrong idea. Write the option in the student's own words, and put the source in the teacher notes.

1. **Education research**: search `"<topic>" misconceptions`, `"<topic>" alternative conceptions`, `"<topic>" concept inventory` (Google Scholar, ERIC, *Physical Review PER*, *Journal of Engineering Education*, *European Journal of Engineering Education*, ASEE conference papers). A concept inventory's wrong answers are ready-made distractors.
2. **Teaching collections that list student errors**: IOP Spark (physics), RSC Education (chemistry), PhET teacher-submitted activities and their research notes.
3. **Examiner and moderator reports**: exam boards publish the common wrong answers per question (e.g. Cambridge International, AQA, Edexcel examiner reports; for engineering, university or professional-exam reports where public).
4. **Textbook "common mistakes" or worked-example warnings** in a standard text for the topic (cite edition and section).
5. **None of the above**: write the wrong idea a reasonable student would hold, label it "teacher's judgement" in the teacher notes, and say in your report which searches came up empty. This is allowed, but it is the last rung, not the first.

What you may not do: invent a trick option that no student would actually hold, or cite a paper you have only seen in a search result as if you had read it — say "abstract only" when that is all you read.

---

## 7. Accessibility

| Need | Rule | Reference |
|---|---|---|
| Keyboard | All functions work from the keyboard, including the predict buttons, run/reset, flap and sliders (SC 2.1.1, Level A) | https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html |
| Sliders | Prefer native `<input type=range>`. A custom slider needs `role="slider"` plus `aria-valuenow`, `aria-valuemin`, `aria-valuemax` and a label. Use `aria-valuetext` such as "2.0 metres". Keys: arrows ±1 step, Home/End for min/max, PgUp/PgDn for a larger step | https://www.w3.org/WAI/ARIA/apg/patterns/slider/ |
| Drag alternatives | Anything done by dragging (moving the object, orbiting the camera, building a track) needs a single-pointer, non-drag alternative: click the track to set a value, ± buttons, a number field (SC 2.5.7, AA) | https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html |
| Motion | Respect `prefers-reduced-motion`: no camera fly-ins or stamp bounces, and show results as a step/snap or a slower run (SC 2.3.3, AAA, technique C39). Auto-playing motion over 5 s needs pause/stop (SC 2.2.2, A) | https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html · https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html |
| 3D diagrams | Each canvas gets a text alternative (SC 1.1.1, A), plus a live text description of the current state and result ("Ball released from 2.0 m; reached 2.0 m on the far side") | https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html |
| Readouts and results | Announce outcomes through a polite live region without moving focus (SC 4.1.3 Status Messages, AA). Throttle while a slider is being dragged [heuristic] | https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html |
| Colour | Energy stores must not rely on colour alone: add labels, patterns or icons on the bars and glow (SC 1.4.1, A). UI and graph parts need 3:1 contrast (SC 1.4.11, AA) | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html · https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html |
| Correct/incorrect | Never signal right and wrong with green/red alone: add text and an icon | SC 1.4.1 (above) |

**PhET precedent.** The Oct-2026 *Energy Skate Park: Basics* teacher guide lists "Inclusive Features" (alternative input, sonification with confirmatory sounds on button presses and checkboxes, interactive description of the core features), a keyboard shortcut that pauses the sim without moving focus, and URL parameters for configuring the sim. Read from the guide PDF: https://phet.colorado.edu/files/teachers-guide/energy-skate-park-basics-html-guide_en.pdf

---

## 8. Teacher's guide structure

**PhET's "Tips for Teachers"** (ESP: Basics, Oct 2026; sections read from the PDF above): an annotated screenshot of the controls → **Complex Controls** → **Model Simplifications** (e.g., on landing, the vertical KE component turns into thermal energy [2nd]) → **Insights into Student Use** → **Suggestions for Use** (sample challenge prompts, clicker questions, link to published activities) → **Simulation Details / Model Documentation** → **Inclusive Features** → **Customisation** (screens, initial screen, locale). Learning goals for the sim include explaining conservation of mechanical energy and predicting position or speed from the bar and pie charts [2nd]. https://www.compadre.org/portal/items/detail.cfm?ID=12838

**IOP Spark** writes misconceptions as **"Wrong Track / Right Lines"** pairs with teaching notes. https://spark.iop.org/energy-can-run-out

**Recommended per-lesson guide** [heuristic, combining the two models above]
1. Learning objectives (2–4, measurable: "explain…", "calculate…", "predict…").
2. Curriculum mapping: list the spec points (e.g., the GCSE/IGCSE codes). **Exact codes must come from the board's spec, not from guesswork.**
3. Timings. Suggested 30–40 min: hook 3, predict 3, test 8–10, prove/flap 5, discussion 8, quiz 5. **[heuristic, UNVERIFIED as research-backed]**
4. Misconceptions, written as Wrong Track / Right Lines and tied to which prediction option targets each one.
5. Model simplifications (what the simulation ignores: air resistance, rotation, and so on).
6. Discussion questions, including "Why did people pick option B?"
7. Answers to the quiz, with an explanation for each distractor.
8. Accessibility and setup notes (keyboard use, reduced motion, low-GPU fallback).
9. Sources.

---

## A lesson page is done when…

- [ ] It teaches **one idea**, opens with a hook, and steps are chained with "but / therefore".
- [ ] The prediction has **3 (max 4) options**, every distractor is a sourced misconception, there are no trick options, and the choice **locks before** the experiment runs.
- [ ] The experiment starts with **≤3 controls**, representations start closed or minimal, slider ranges have informative extremes, and confounds are off by default (friction off when testing mass).
- [ ] Every representation (3D flow, bars, equation, readout) updates **in the same frame** from one state, and each energy store has one colour **plus** a label or pattern.
- [ ] Readouts show **SI units with a space**, at 2–3 sig figs, and totals add up.
- [ ] The flap explanation **reuses the student's own numbers**, and a wrong prediction gets an explanation of *that* misconception without blame.
- [ ] The stamp rewards **completing the loop**. There are no points or leaderboards, no red-only ✗, and stamp text is about the physics.
- [ ] Scene text is 1–3-word labels, and longer text sits behind the flap or in pop-overs.
- [ ] Everything works from the **keyboard**, sliders follow the APG pattern with `aria-valuetext`, and every drag has a non-drag alternative.
- [ ] `prefers-reduced-motion` is honoured, any auto-motion can be paused, and each 3D canvas has a text alternative plus live status messages.
- [ ] The quiz has 3–5 items, uses misconception-based distractors, and gives explained feedback.
- [ ] The teacher's guide has objectives, spec mapping, timings, Wrong Track / Right Lines, model simplifications, discussion questions and sources.

---

## Sources

- White & Gunstone 1992 / POE: https://arbs.nzcer.org.nz/node/7187 · https://interactivetextbooks.tudelft.nl/showthephysics/Pedagogy/PoE.html · https://www.researchsquare.com/article/rs-3401672/latest
- Crouch et al. 2004: https://www.compadre.org/portal/items/detail.cfm?ID=2329 · https://mazur.harvard.edu/presentations/classroom-demonstrations-learning-tools-or-entertainment · https://mirjamglessmer.com/2014/06/01/how-to-make-demos-useful-in-teaching/
- Brod 2021: https://www.pedocs.de/volltexte/2021/23704/pdf/EPR_2021_4_Brod_Generative_Learning_A.pdf
- Metcalfe 2017: https://annualreviews.org/doi/abs/10.1146/annurev-psych-010416-044022
- Sadler 1998: https://users.nber.org/~sewp/events/2004.05.28/Sadler_PsychometricModels.pdf
- Rodriguez 2005: https://tipsforteachers.substack.com/p/research-bite-20-three-options-are
- PhET About: https://phet.colorado.edu/en/about
- Podolefsky, Moore & Perkins (implicit scaffolding): https://arxiv.org/abs/1306.6544
- Podolefsky, Perkins & Adams 2010: https://link.aps.org/doi/10.1103/PhysRevSTPER.6.020117
- Adams et al. 2008: https://ej.issuelab.org/resource/a-study-of-educational-simulations-part-ii-interface-design
- PhET Look and Feel: https://PHet.colorado.edu/publications/PhET%20Look%20and%20Feel.pdf
- PhET ESP: Basics teacher guide: https://phet.colorado.edu/files/teachers-guide/energy-skate-park-basics-html-guide_en.pdf · https://www.compadre.org/portal/items/detail.cfm?ID=12838
- Victor: https://worrydream.com/ExplorableExplanations/ · https://worrydream.com/KillMath
- Case: https://href.leiden.digital/entry/38 · https://ncase.me/archive · https://blog.ncase.me/explorable-explanations-the-plan · https://explorabl.es/jam/ · https://redblobgames.com/x/2306-educ432 · https://github.com/blob42/awesome-explorables
- Hattie & Timperley 2007: https://www.bera.ac.uk/blog/how-to-optimise-the-use-of-hattie-and-timperleys-feedback-levels-for-student-learning
- Deci, Koestner & Ryan 1999: https://home.ubalt.edu/ntygmitc/642/Articles%20syllabus/Deci%20Koestner%20Ryan%20meta%20IM%20psy%20bull%2099.pdf · https://utupub.fi/handle/10024/173853
- Hanus & Fox 2015: https://www.smhp.psych.ucla.edu/pdfdocs/gamil.pdf
- Harp & Mayer 1998 / coherence: https://www.cambridge.org/core/books/abs/multimedia-learning/coherence-principle/4E80B70CB76E2166B76E5653EBDE7D3E
- Ainsworth 2006: https://nottingham-repository.worktribe.com/output/23577631/deft-a-conceptual-framework-for-considering-learning-with-multiple-representations
- NIST SP 811: https://www.nist.gov/pml/special-publication-811
- IOP Spark: https://spark.iop.org/energy-can-run-out · https://spark.iop.org/collections/shifting-energy-between-stores-teaching-and-learning-issues · https://spark.iop.org/many-students-see-energy-intangible-fluid-flows-one-place-or-object-another-during-process · https://spark.iop.org/many-students-associate-energy-humans-and-other-living-things · https://spark.iop.org/many-students-also-associate-energy-fuels-and-electricity · https://spark.iop.org/many-students-do-not-think-energy-conserved-biological-processes-and-see-these-either-using-energy
- Watts 1983 (via resource letter): https://arxiv.org/pdf/1407.5533
- Oak National: https://thenational.academy/teachers/programmes/physics-secondary-ks4-foundation-edexcel/units/energy-of-moving-objects/lessons/efficiency-in-terms-of-useful-energy-transferred
- WCAG 2.2 Understanding: keyboard, dragging-movements, animation-from-interactions, pause-stop-hide, non-text-content, status-messages, use-of-color, non-text-contrast (URLs in §7); ARIA APG slider: https://www.w3.org/WAI/ARIA/apg/patterns/slider/
- Every Joule (pattern only): https://iamtechartist.com/every-joule/
