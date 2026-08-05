#!/usr/bin/env python3
"""
Content for the Field Guide page.

This is the consolidation layer over the library: what the 292 posts actually
say once you collapse the repetition, plus the places they contradict each other.
Written by reading the corpus, not by reshuffling the topic tags.

Format: every claim carries the post numbers it came from, in [brackets]. The
build script turns those into clickable pointers that open the source post
inline, so nothing here has to be taken on trust.
"""

SECTIONS = [

# ---------------------------------------------------------------- job search
{
 "id": "job-search",
 "kicker": "Start here",
 "title": "The job search",
 "lede": "36 posts here come from people who hire AEs for a living. Read independently "
         "they look like 36 opinions. Read together they are one argument, made "
         "eight separate times.",
 "blocks": [

  {"type":"finding",
   "h":"The hiring process is a demo of the job, and they are grading it as one",
   "p":"This is the strongest consensus in the entire library. A recruiter puts it "
       "plainly: in the first interview you are building rapport, doing discovery, "
       "and persuading, then afterwards you are driving next steps and following up. "
       "You are running a deal, and founders read it exactly that way, right down to "
       "complaining that a candidate went 48 hours without contact. [39] A VP with 347 "
       "resumes for 3 roles listed what almost no one does: call or email the team, "
       "message on LinkedIn, ask any questions, follow up on the screen with specific "
       "takeaways. Three candidates out of 347 stood out. [156] The candidate who "
       "beat a saturated market built a shared deal room to track progress toward "
       "offer-signed and earned product certifications before the final round. [85, 152]",
   "cite":[39,156,85,152]},

  {"type":"h","h":"Before you apply"},
  {"type":"bullets","items":[
    ("Applying is the weakest available move. Of 160 applicants to one AE role, only "
     "about 40% also messaged the hiring manager directly. That alone was the first "
     "thing that made someone stand out.", [20]),
    ("Do not put the burden on the manager. The standard note (\"wanted to get your "
     "insight on the role before applying\") reads as \"teach me about your company so "
     "I can decide.\" Invert it: what you have learned about the company, what you have "
     "learned about the role, why you fit, low-effort ask.", [149]),
    ("Bring proof, not adjectives. The standout candidate attached screenshots of prior "
     "performance to the first message.", [85, 152]),
    ("The laid-off playbook, in order: find companies still hiring, sequence the hiring "
     "manager and the VP, send them a list of 5 accounts with 2 prospects each as an "
     "unsolicited value-add, then email the CEO.", [246]),
    ("Persistence is not rudeness. One candidate followed up four times, sent a "
     "personalised video, and researched where the company's President's Club was held. "
     "He advanced.", [60]),
    ("Unlisted roles never reach the job boards. Google the ATS domains directly: "
     "site:greenhouse.io | site:lever.co \"account executive\" AND \"remote\", "
     "then filter to the past week.", [108]),
   ]},

  {"type":"h","h":"The resume"},
  {"type":"bullets","items":[
    ("Your top 4-5 bullets should answer six questions: are you a high performer, how "
     "did you perform over time, what did you sell, who did you sell to, hunter or "
     "farmer, and what deal sizes. Results over responsibilities. Drop the objective "
     "section in favour of Sales Career Highlights.", [144]),
    ("What a hiring manager is actually scanning for is progression, and it shows up "
     "three ways: promotions, increasing technical complexity of what you sell, and "
     "increasing deal size. The middle one is a strong signal for infra and dev-tools "
     "roles specifically.", [19]),
    ("The resume only buys the screening call. Everything that moves you toward an "
     "offer happens after it.", [1]),
   ]},

  {"type":"h","h":"In the room"},
  {"type":"bullets","items":[
    ("Be concise and attach a number to every answer. \"#2 out of 30. 127% in FY24. "
     "$1.68M ARR closed\" beats \"I did really well.\" Specificity signals you are the "
     "kind of rep who tracks performance. Candidates who talk in circles lose the room.", [1, 51]),
    ("\"Tell me about yourself\" is the question candidates fumble most and the one you "
     "should most obviously have ready. It is a narrative, not a chronological walk "
     "through the resume, and it is where an unconventional background becomes an asset "
     "rather than a gap.", [22]),
    ("Take proactive control by offering to walk through your background, then tell "
     "stories rather than bullets: grit, curiosity, a specific win you are proud of. "
     "Hardly any candidate takes control, and interviewers are watching for it.", [248]),
    ("Use material from outside work. Taught yourself something hard, competitive at an "
     "elite level as an adult, obsessed with a subject, leader of your friend group. "
     "It reads as smart, disciplined and development-minded.", [38]),
    ("If you missed quota, take ownership before you explain. Blaming territory, product "
     "and manager loses even when it is true. Own the call you got wrong, then give the "
     "wins and the lessons.", [31]),
    ("Ask about the business, not the day-to-day and PTO. Product-market fit, "
     "trajectory, what is working.", [1]),
    ("Acknowledge your gap before they find it. Every strong candidate has one; the ones "
     "who advance are the ones who name it cleanly and without defensiveness.", [1]),
   ]},

  {"type":"h","h":"After every conversation"},
  {"type":"bullets","items":[
    ("Send a note referencing two specific things they said. One candidate did this "
     "after a 15-minute screen and it was remembered.", [156]),
    ("Recommend the next step yourself rather than waiting to be scheduled.", [85, 152]),
    ("Answer fast. Responsiveness is named as a dealbreaker by multiple hiring managers, "
     "and slow replies are read as a preview of how you will handle their customers.", [1, 39]),
   ]},

  {"type":"h","h":"Artifacts worth building once"},
  {"type":"bullets","items":[
    ("A one-page cheat sheet per interview: company background (pitch, mission, clients, "
     "competitors, recent funding), interviewer background (roles, past companies, a "
     "quote from something they posted), and questions written for that specific person.", [238]),
    ("A day-zero-to-120 plan, an example prospecting message for their buyer, and a "
     "written case for why this is not just another application.", [280]),
    ("Questions that grade the manager rather than the company: how do you identify skill "
     "gaps and coach them, how many reps left your team in the last 12 months and why, "
     "who earns the next promotion and what do they have to do first. Three good answers "
     "means take the job.", [145]),
   ]},

  {"type":"h","h":"Choosing between offers"},
  {"type":"bullets","items":[
    ("Learn four equity terms before you negotiate: double trigger, and what happens to "
     "unvested options on acquisition and termination.", [266]),
    ("A worked comparison of three VP offers at $500k, $400k and $300k OTE, differing on "
     "funding, remote policy and go-to-market motion. Useful as a checklist of what "
     "actually differs between offers.", [146]),
    ("Founding AE at an early-stage startup is a different job with different risks.", [165]),
   ]},
 ]},

# ------------------------------------------------------------------ conflicts
{
 "id":"contested",
 "kicker":"Read before you copy anything",
 "title":"Where the corpus contradicts itself",
 "lede":"Six places where credible practitioners in this library flatly disagree. An "
        "index hides these because it files both sides under the same topic. None of "
        "them is resolved below, on purpose: they are judgement calls, and knowing "
        "a call is contested is more useful than being handed the wrong side of it.",
 "blocks":[
  {"type":"conflict",
   "h":"AI-written personalisation",
   "a":("Against", "Personalisation that can be scaled is not personalisation. One post "
        "compares it to Milli Vanilli lip-syncing: if every message is generated from "
        "public information, it is not personal, and AI makes this worse rather than "
        "better.", [177, 2]),
   "b":("For", "\"It doesn't have to be personal and hand-written. But it sure does have "
        "to appear that way.\" And a first-hand account of a prospect who asked outright "
        "whether a message was AI, was told yes, said \"okay\" and carried on.", [102, 17])},

  {"type":"conflict",
   "h":"Permission-based openers",
   "a":("Against", "\"Did I catch you at a bad time\" is named the single worst opener "
        "in the library. Asking permission hands the buyer a job and applies decision "
        "pressure; another author calls the whole PBO approach a status-lowering fallacy.",
        [207, 18, 269]),
   "b":("For", "A 34-item list of softening language patterns built on exactly this "
        "instinct: \"would you be against\", \"I'm a little embarrassed to ask\", \"if "
        "you feel comfortable sharing\". Same mechanism, deployed deliberately to lower "
        "resistance.", [229])},

  {"type":"conflict",
   "h":"How much the rep should talk",
   "a":("Talk less", "The received wisdom throughout: get the prospect talking, listen "
        "first, one method claims 80% prospect talk time against 20% rep.", [252, 257]),
   "b":("Talk more", "Data from The Jolt Effect shows reps interrupt and talk over "
        "prospects more in wins than in losses, with 58% rep talk time in wins against "
        "52% in losses.", [215])},

  {"type":"conflict",
   "h":"The breakup email",
   "a":("Dead", "\"Have you given up solving for X\" is counterproductive: it implies "
        "there was no real problem, and de-prioritising is an executive skill, not "
        "surrender. A second author simply calls the pushy breakup email dead.", [50, 155]),
   "b":("Works", "A three-option template (no-go / not now / I didn't respond) is "
        "reported as un-ghosting three opportunities from three emails.", [67, 140])},

  {"type":"conflict",
   "h":"When a deal goes quiet, push or withdraw",
   "a":("Push", "Send an unprompted calendar invite with a written reason attached; if "
        "they cancel without proposing a time, move the invite yourself rather than "
        "starting an email thread.", [9, 194, 23]),
   "b":("Withdraw", "They are not ghosting you, they are in meetings and fires. You are "
        "not their priority, their job is. Do not add to the noise. A second author "
        "recommends actively pulling away and making it easy to opt out.", [94, 196])},

  {"type":"conflict",
   "h":"Short emails or long ones",
   "a":("Short", "Measured across roughly 200m emails: cutting 125 words to 25-75 lifted "
        "replies 64%, and dropping to a 5th-grade reading level lifted them 67.5%.", [182]),
   "b":("Long, sometimes", "Executives do not reply to \"short and sweet\", they reply "
        "to evidence you did the work. And a recruiter's favourite inbound candidate "
        "email is explicitly long: \"at some point we got too obsessed with brevity.\"",
        [4, 24])},
 ]},

# ---------------------------------------------------------------------- plays
{
 "id":"reply",
 "kicker":"Play",
 "title":"Getting a reply",
 "lede":"The single most crowded topic in the library, and the one where independent "
        "authors converge hardest. Six moves, in order. Almost every worked example "
        "here is the same six moves with different words.",
 "blocks":[
  {"type":"numbered","items":[
    ("An observation that answers \"why me and not someone else\"",
     "Specific enough to be unfaked. A trigger, a signal, a named person, something "
     "they said on a podcast. Never an opener the reader already knows about "
     "themselves.", [82, 99, 220, 131]),
    ("A problem, hypothesised rather than asserted",
     "\"Poke the bear.\" Phrase it as a question they cannot answer with certainty, "
     "which makes them think rather than defend. Normalise it so it does not read as "
     "blaming their team.", [71, 82, 92]),
    ("Third-party proof carrying a number",
     "A named comparable and what changed. \"Netflix cut 600 apps to 400.\" \"12-15 "
     "conversations every 45 minutes.\"", [71, 99, 131]),
    ("A line on how it actually works",
     "Buyers are silently asking this. One sentence, and pre-empt the objection while "
     "you are there: no new tech, no long-term contract.", [71, 131]),
    ("A low-friction binary ask",
     "\"Open to learning more?\" or \"Worth a chat?\" You are gauging interest, not "
     "asking for 30 minutes on a calendar.", [71, 99, 131]),
    ("A detach that gives them an easy out",
     "\"If now's not the time, happy to check back in Q3.\" Removes pressure, which is "
     "the thing that makes the reply cheap to send.", [71, 131, 196]),
   ]},
  {"type":"h","h":"The measured version"},
  {"type":"p","p":"One dataset in the library, drawn from 30k inboxes and around 200m "
        "emails, puts numbers on the same advice. Treat these as direction, not law: "
        "the author says as much."},
  {"type":"data","rows":[
    ("125 words cut to 25-75", "+64%"),
    ("10th grade reading level cut to 5th", "+67.5%"),
    ("Subject line of 5 words cut to 2", "+65%"),
    ("Mobile optimised", "+81%"),
    ("Adding a P.S. to a personalised email", "+35.7%"),
    ("Asking more than one question", "-26%"),
    ("Adding percentages or multipliers", "-44%"),
    ("Any informative tone", "-26%"),
   ], "cite":[182]},
  {"type":"h","h":"Details worth stealing"},
  {"type":"bullets","items":[
    ("Preview text is the first 8 words, it shows on mobile, and almost nobody writes "
     "it deliberately. Put the exec's name, product or initiative there.", [76]),
    ("Write the first email so it creates a reason for the second: \"forgot to mention "
     "this yesterday\" followed by the video or research you deliberately held back.", [95]),
    ("Subject lines: one word beats everything, four is the ceiling. A long list of real "
     "bad ones is worth reading once as a list of what not to do.", [176]),
    ("Put the personalised line after the signature rather than in the opener, so the "
     "email does not read as a template with a variable at the top.", [190]),
    ("A list of openers to never use, and the ones to replace them with.", [102, 220]),
    ("Signals beat tiers. A Tier 1 account showing intent is a different play from a "
     "cold Tier 1: less research, act faster.", [96]),
   ]},
 ]},

{
 "id":"phone",
 "kicker":"Play",
 "title":"Getting on the phone",
 "lede":"The opener is contested (see above). Everything around the opener is not.",
 "blocks":[
  {"type":"bullets","items":[
    ("Tone first. The customer-service voice repels: nobody woke up hoping for a "
     "surprise conversation, so unbridled enthusiasm at 9:03am does not match the "
     "moment. Calm beats cheerful, grounded beats bubbly.", [16]),
    ("Give context before you give a pitch. \"Don't say 'is this Chris' if you don't "
     "know who you're calling. Give more about you in your intro. Don't pitch straight "
     "up.\"", [135]),
    ("Educating outperforms selling: \"a lot of people don't know what our tech does, "
     "are you familiar with it?\" then \"do you mind if I quickly explain, it might be "
     "pertinent?\"", [118]),
    ("Humour and pattern interrupt work on the right buyer. A worked transcript of a "
     "cold call that landed in 17 words plus a laugh.", [91]),
    ("One line that works on calls and in deals: \"What would make this a YES?\" "
     "Deployed against \"send me an email\" it becomes \"what would that email have to "
     "include for you to say yes?\"", [66, 8]),
    ("A manager's diagnostic for your own recordings: opener, conversation starter, "
     "objection handling, each with specific pass/fail questions.", [87]),
   ]},
  {"type":"h","h":"Real numbers, for calibration"},
  {"type":"bullets","items":[
    ("239 dials produced 81 connects and 11 meetings over 2.5 days, one rep, with a "
     "curated list rather than more volume.", [70]),
    ("251 dials produced 5 conversations and 1 meeting, posted by a rep as a normal day.", [58]),
    ("4.8% of cold calls converting to meetings became 6.9% after changing the opener, "
     "opening statement and pitch structure. A 44% improvement.", [11]),
   ]},
 ]},

{
 "id":"power",
 "kicker":"Play",
 "title":"Getting to power",
 "lede":"The largest cluster in the deal shelf. Two opposing routes, both credible, "
        "then a set of mechanics that apply either way.",
 "blocks":[
  {"type":"bullets","items":[
    ("Top-down: start at the top, yo-yo down to the middle, then come back up. Deals "
     "move faster when power is involved from the start.", [130]),
    ("Bottom-up: start with VPs and directors to learn what is actually happening, build "
     "a point of view that teaches the exec something about their own business, then "
     "ask. One AE ran full discovery with an entry-level contact who was obviously the "
     "wrong buyer, learned a C-level goal, and built the business case from it.", [7, 40]),
    ("Ask for the exec as part of discovery rather than as a later escalation, and frame "
     "it as normal: \"typically an initiative like this is driven by someone at exec "
     "level, is there one on your side?\"", [130, 209]),
    ("Use your own executives. Execs take meetings with execs. Ghostwriting a message "
     "that sounds like your exec, aimed at their exec, is a named skill for moving "
     "upmarket.", [47, 175]),
    ("The Executive Power Hour: eight reps plus the CRO and one senior leader, one hour, "
     "everyone with LinkedIn open, mapping warm paths into named accounts. Reported as "
     "14 meetings, 9 opportunities and 4 closed-won inside 60 days.", [97]),
    ("A minute-by-minute structure for the exec meeting itself, opening with a "
     "non-obvious insight in the first five minutes.", [35]),
    ("Ask executives fewer questions, not more. Gong's \"discovery fatigue\": 10-14 "
     "questions is normal, 4-8 is right for execs.", [202]),
    ("Four one-liners for Fortune 50 executives, including scale-of-1-to-10 questions "
     "to force a decision in the moment.", [128]),
    ("Multi-threading has a shape: at least 1 champion, 3 coaches, 5 contacts. If your "
     "main contact goes quiet you continue the conversation with the others.", [251]),
   ]},
 ]},

{
 "id":"first-call",
 "kicker":"Play",
 "title":"Running the first call",
 "lede":"The counterintuitive finding here is the most quotable thing in the library, "
        "and it is the opposite of what most reps are coached to do.",
 "blocks":[
  {"type":"finding",
   "h":"The reps converting 70% of first calls discuss fewer problems, not more",
   "p":"Across hundreds of reviewed discovery calls, the difference between AEs "
       "converting 40% and 70%+ is the number of problems discussed, and the top reps "
       "discuss fewer. Going wide to find anything you can attach the product to feels "
       "like thoroughness. It reads as an interrogation, and no company has capacity to "
       "act on many priorities at once.",
   "cite":[54, 78]},
  {"type":"bullets","items":[
    ("Go deeper instead: four levels of impact, where 90% of reps stop at company-level "
     "cost or revenue and never reach the individual stake. Know what the deal does for "
     "your champion personally, up to and including their promotion.", [63, 83]),
    ("Do not ask about budget early. One seller with 18 years of experience never closed "
     "a large deal where budget was approved at the start; asking stops you before you "
     "have qualified anything.", [187, 154]),
    ("The three worst questions: anything you could have looked up, \"how does this "
     "impact you personally\", and \"what keeps you up at night\".", [116]),
    ("Better phrasings for the same intent: \"how is that showing up in the business?\" "
     "instead of \"what's the impact?\", and the magic-moment question, \"what was the "
     "moment you realised this was a problem worth solving?\", asked only after they "
     "have said they want to change.", [222, 12]),
    ("Never ask who the decision maker is. Ask who would feel left out if this moved "
     "forward without them, who can stop it, and walk me through how you bought "
     "something similar before.", [174]),
    ("For inbound, do not assume a demo request means a buyer. \"Of all the vendors, why "
     "are you considering us?\" sorts motivated buyers from browsers fast.", [226, 288]),
    ("Sell your discovery process rather than the product: when a prospect agrees to show "
     "you how they work today, they expect you to come back with a better way.", [183]),
    ("Set the agenda out loud, and offer to go first if you were the one who reached out. "
     "A worked transcript turns a cold, arms-folded VP into the author's best call.", [123]),
   ]},
 ]},

{
 "id":"alive",
 "kicker":"Play",
 "title":"Keeping the deal alive",
 "lede":"The library is unusually rich here, probably because it is where deals are "
        "most often lost quietly.",
 "blocks":[
  {"type":"bullets","items":[
    ("Stop sending recap emails. Flooding the buyer with everything you heard feels "
     "consultative and kills momentum; only one thing matters between first meeting and "
     "proposal, and the email should carry that.", [27, 33]),
    ("Never hand the buyer a task. \"Can we get Bob on the next call?\" is not a next "
     "step, it is work assigned to the person least incentivised to do it. \"How does "
     "Tuesday sound?\" is.", [18]),
    ("Replace the meeting-confirmation email, which is an easy out, with an agenda email "
     "the day before that asks for their input.", [106]),
    ("Bad news arriving by email gets answered by phone, never by email. If they will not "
     "take the call at all, there was no deal.", [6]),
    ("\"We'll get back to you after our internal discussions\" is a turning point, and "
     "there are worked bad, better and good responses to it.", [68, 86, 89]),
    ("The three-option un-ghosting template (no-go / not now / I didn't respond) and the "
     "46-word ghosting email are the two most-cited assets here.", [67, 140, 127]),
    ("Closed-lost is not closed. One rep re-opened a deal marked dead in February off a "
     "single alert that the account was back on the website.", [55]),
    ("A post-no-show move: do not delete the invite, move it two days out with a note.", [23, 194]),
   ]},
 ]},

{
 "id":"landing",
 "kicker":"Play",
 "title":"Landing it",
 "lede":"Thinner than the rest, but the negotiation material is specific and hard-won.",
 "blocks":[
  {"type":"bullets","items":[
    ("Never negotiate before you are vendor of choice. If they will not confirm it, the "
     "conversation is a price comparison, not a negotiation.", [44, 90]),
    ("29 negotiation habits from reps earning $350k+, of which the load-bearing ones are: "
     "get a get for every give, never discount unasked, uncover all asks before agreeing "
     "to any, and know your walk-away up front.", [113]),
    ("A word-for-word response to \"give me your drop dead final price\", built on "
     "refusing the race to the bottom.", [129]),
    ("Arm your champion with the questions their CFO will ask them, rather than just "
     "sending pricing when they ask for it.", [52]),
    ("Set the signature expectation before you send the contract: \"if we haven't heard "
     "from you by the weekend, would you be against me reaching out?\"", [236]),
    ("Get on texting terms with your champion. Every sizeable deal one author closed had "
     "this in common.", [201]),
    ("Accusation audit: voice their objection before they can. \"I'm assuming you already "
     "have a provider in place, but...\"", [74]),
   ]},
 ]},

# --------------------------------------------------------------------- assets
{
 "id":"assets",
 "kicker":"Index",
 "title":"Where the copy-paste assets are",
 "lede":"Templates, scripts and frameworks that exist verbatim in the library, rather "
        "than being described. This is the list to raid when you need something today.",
 "blocks":[
  {"type":"assets","rows":[
    ("22 prospecting plays ranked closest to furthest from revenue", "7-page document, transcribed in full", [199]),
    ("Six-sentence cold email framework, with a worked example", "", [71]),
    ("Colour-coded cold email teardown, line by line", "transcribed from the image", [131, 82]),
    ("Enterprise cold email that does not pitch a solution", "", [92]),
    ("Four-line email framework used to source 100s of meetings", "", [99]),
    ("13-step cold email checklist", "", [227]),
    ("Post-discovery follow-up email template", "", [221]),
    ("Three-option un-ghosting template", "", [67, 140]),
    ("46-word ghosting email", "", [127]),
    ("Post-no-show calendar note", "", [23]),
    ("Response to \"we'll get back to you internally\"", "", [68]),
    ("Response to \"just send me pricing for the CFO\"", "", [52]),
    ("Response to \"give me your drop dead final price\"", "", [129]),
    ("34 language patterns that lower resistance", "", [229]),
    ("29 negotiation habits", "", [113]),
    ("Champion / coach / contact multi-threading counts", "", [251]),
    ("Minute-by-minute exec meeting outline", "", [35]),
    ("Interview cheat sheet, three sections", "", [238]),
    ("Questions to grade a prospective manager", "", [145]),
    ("Rewritten job-seeking outreach to a hiring manager", "", [149]),
    ("Resume structure for AEs, six questions", "", [144]),
    ("10 LinkedIn and Sales Navigator features", "13-page document, transcribed in full", [235]),
    ("7 ChatGPT resume tips including the bullet formula", "9-page document, transcribed in full", [210]),
    ("ATS Google search syntax for unlisted jobs", "", [108]),
   ]},
 ]},

# --------------------------------------------------------------------- people
{
 "id":"voices",
 "kicker":"Orientation",
 "title":"Who to trust on what",
 "lede":"140 authors, but the library is dominated by a handful, and they specialise. "
        "If you are going one level deeper on a subject, this is whose back catalogue "
        "to read.",
 "blocks":[
  {"type":"voices","rows":[
    ("Kyle Asay", 26, "Hiring and interviewing from the manager's side, discovery conversion, pipeline generation plans, territory. The most useful single author here for your current project."),
    ("Josh Braun", 20, "Cold email psychology, resistance-lowering language, the anti-pitch stance. Most of the verbatim email teardowns are his."),
    ("Ian Koniak", 14, "Enterprise, executive access, levels of impact, and the argument against recap emails."),
    ("Chris Orlob", 11, "Discovery questions, negotiation habits, and what separates high earners."),
    ("Justin Michael", 11, "Cold calling theory, deliberately contrarian, the source of the anti-PBO position."),
    ("Brian LaManna", 9, "Working AE tactics: un-ghosting templates, preview text, closed-lost re-entry."),
    ("Isaiah Crossman", 8, "Recruiter. Interview positioning, plus deal-rescue moves like the calendar dart."),
    ("Kyle Coleman", 8, "Follow-up discipline, outbound testing, and the contrarian talk-time data."),
    ("Nate Nasralla", 5, "Selling to and through executives, ghostwriting for your own execs."),
    ("Florin Tatulea", 7, "SDR mechanics and the most concrete laid-off job-hunt plan in the library."),
   ]},
 ]},

# ---------------------------------------------------------------------- gaps
{
 "id":"gaps",
 "kicker":"Honest caveats",
 "title":"What this library is thin on",
 "lede":"Worth knowing before you treat it as complete. These are gaps in what you "
        "saved, not in the sorting.",
 "blocks":[
  {"type":"bullets","items":[
    ("Email deliverability: 2 posts. If a domain gets burned or open rates collapse, "
     "there is almost nothing here.", []),
    ("Outreach to hiring managers specifically: 2 posts as a primary subject, which is "
     "thin for what you are doing right now. The workaround is that cold email craft "
     "transfers directly, and the job-search section above pulls the relevant parts "
     "forward.", []),
    ("Territory and account planning: 15 posts across three topics, mostly frameworks to "
     "download rather than worked examples.", []),
    ("Objection handling: 5 posts as primary subject, which is surprisingly light given "
     "how much cold calling material there is.", []),
    ("Roughly 16 saves are not about sales at all, and are quarantined under Not Sales in "
     "the library rather than being silently mixed in.", []),
    ("Dating: anything older than a week is approximate, derived from LinkedIn's relative "
     "timestamps. A meaningful share of this library is 3 to 5 years old, which matters "
     "most for the AI and tooling material, where several posts are already obsolete.", []),
   ]},
 ]},
]
