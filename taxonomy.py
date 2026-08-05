#!/usr/bin/env python3
"""
Two-level taxonomy for the sales tips library.

Built by reading all 292 opening lines, not from a generic sales-theory outline,
so the topics match what is actually in this corpus. Notable consequences:
  - "cold email" is split into craft vs deliverability, because there are enough
    of both to matter
  - "ghosting & re-engagement" is its own topic, not a footnote under objections
  - "not sales" exists, because ~20 saves are off-topic (Stable Diffusion, Borges,
    Selenium, buying a business) and they pollute every other shelf

Each post gets ONE primary topic (so navigation is clean and every post appears
once) plus any secondary topics that scored above threshold (so search finds it).

Scoring: `strong` patterns are worth 3, `weak` 1. Matches in the opening line
count double, since that line is almost always the post's thesis.
"""

import re

# shelf -> [(topic key, label, strong patterns, weak patterns)]
TAXONOMY = [
    ("prospecting", "Prospecting & Outbound", [
        ("cold-email-craft", "Cold email: writing the thing",
         [r"cold email", r"cold e-mail", r"opening line", r"first sentence",
          r"subject line", r"email template", r"copywriting", r"email framework",
          r"\bp\.?s\.?\b.{0,20}email", r"email checklist", r"personaliz"],
         [r"\bemail\b", r"reply rate", r"\bcopy\b", r"messaging"]),

        ("cold-email-delivery", "Cold email: deliverability & testing",
         [r"spam filter", r"warm.?up", r"deliverab", r"open rate", r"email tracking",
          r"tracking tool", r"inbox placement", r"domain"],
         [r"\btest\b", r"\bdata\b", r"reply rate"]),

        ("cold-calling", "Cold calling",
         [r"cold call", r"cold-call", r"\bdials?\b", r"call opener", r"opening line.{0,20}call",
          r"connect rate", r"pattern interrupt", r"permission.based opener",
          r"\bpbo\b", r"gatekeeper", r"cold calling"],
         [r"\bcall\b", r"pick up", r"live conversation", r"\bphone\b"]),

        ("linkedin-social", "LinkedIn & social selling",
         [r"linkedin (feature|playbook|post|dm)", r"\binmail", r"social selling",
          r"expand the sandbox", r"linkedin profile", r"content strategy",
          r"posting on linkedin"],
         [r"linkedin", r"\bdm\b", r"comment"]),

        ("voicemail-video", "Voicemail, video & voice notes",
         [r"voicemail", r"voice memo", r"voice note", r"video message", r"video prospecting",
          r"\bloom\b", r"send.{0,10}video"],
         [r"\bvideo\b", r"\bvoice\b"]),

        ("sequences", "Sequences & cadence",
         [r"sequence", r"cadence", r"multi.?channel", r"touch.?points?", r"follow.?up strategy",
          r"\d+ ?(step|touch) ", r"outbound motion"],
         [r"outbound", r"\bsteps?\b"]),

        ("targeting-triggers", "Targeting & trigger events",
         [r"trigger event", r"job change", r"funding (event|round)", r"intent data",
          r"ideal customer profile", r"\bicp\b", r"account list", r"tech stack.{0,20}prospect",
          r"break into", r"target account"],
         [r"\bresearch\b", r"\bsignals?\b", r"\bfit\b"]),

        ("referrals-warm", "Referrals & warm paths",
         [r"referral", r"\bintro(duction)?s? (to|from)", r"ask for an intro",
          r"warm (intro|path|lead)", r"champion.{0,15}intro", r"22 plays"],
         [r"\bnetwork\b", r"\bconnect(ion)?s\b"]),
    ]),

    ("deal", "Running the Deal", [
        ("discovery", "Discovery & qualification",
         [r"discovery call", r"\bdiscovery\b", r"disco call", r"qualif", r"\bmeddic",
          r"\bbant\b", r"\bspin\b", r"first call", r"\bpain\b", r"root cause",
          r"questions? (to|you) ask", r"\bimpact\b.{0,20}discovery"],
         [r"\bquestions?\b", r"\bproblem\b", r"\bwhy\b"]),

        ("demos", "Demos & presenting",
         [r"\bdemos?\b", r"demoing", r"product demo", r"powerpoint", r"\bslides?\b",
          r"\bdeck\b", r"presentation", r"\bpoc\b", r"proof of concept", r"paid trial"],
         [r"\bpresent", r"\bshow\b"]),

        ("followup-recap", "Follow-up & recap emails",
         [r"recap email", r"follow.?up email", r"after (the |a )?(discovery|demo|call)",
          r"between calls", r"keeping you in the loop", r"confirming your meeting",
          r"add value between"],
         [r"follow.?up", r"\brecap\b"]),

        ("exec-access", "Multithreading & executive access",
         [r"\bcfos?\b", r"\bceos?\b", r"\bcios?\b", r"\bcoo\b", r"\bciso\b", r"\bcro\b",
          r"c.suite", r"c.level", r"executive", r"economic buyer", r"getting to power",
          r"multi.?thread", r"above the line", r"fortune \d+", r"senior level"],
         # "vp of" is weak on purpose: as a strong title match it stole posts about
         # VPs who are hiring, which belong on the career shelf.
         [r"\bexec\b", r"\bpower\b", r"decision maker", r"\bvp of\b"]),

        ("objections", "Objections & brush-offs",
         [r"objection", r"send me (an |the )?email", r"not interested", r"we need to think",
          r"no budget", r"do you have budget", r"brush.?off", r"push.?back", r"\bstall",
          r"too expensive", r"happy with (our|their)", r"we're all set", r"zone of resistance"],
         [r"\bno\b.{0,10}thanks", r"\bresistance\b"]),

        ("ghosting", "Ghosting & re-engagement",
         [r"ghost", r"went dark", r"go dark", r"breakup email", r"break.?up email",
          r"un.?ghost", r"stopped hearing", r"closed lost", r"revive", r"re.?engage",
          r"chase", r"pulling away"],
         [r"\bsilence\b", r"\bignored\b"]),

        ("negotiation-pricing", "Negotiation & pricing",
         [r"negotiat", r"\bpricing\b", r"\bdiscount", r"final price", r"procurement",
          r"\bcontract\b", r"legal review", r"\bterms\b", r"give me your.{0,20}price"],
         [r"\bprice\b", r"\bbudget\b", r"\bcost\b"]),

        ("closing", "Closing & late stage",
         [r"close (the |bigger |more )?deals?", r"close rate", r"closing", r"mutual action plan",
          r"close plan", r"\bforecast", r"end of (quarter|year|fiscal)", r"late stage",
          r"internal discussions", r"get.{0,15}deals? closed", r"bad news",
          r"deal (review|rescue)", r"save the deal"],
         [r"\bclosed?\b", r"\bwon\b", r"\bsigned\b"]),
    ]),

    ("pipeline", "Territory & Pipeline", [
        ("pipeline-gen", "Pipeline generation systems",
         [r"pipeline generation", r"pipe ?gen", r"\bpg plan", r"generate (more )?pipeline",
          r"5x5", r"sourced \d+ meetings", r"booked \d+ meetings", r"net new meetings",
          r"weekly (plan|prep|goals)"],
         [r"\bpipeline\b", r"\bmeetings?\b"]),

        ("territory", "Territory & account planning",
         [r"territory", r"account plan", r"book of business", r"patch", r"account research",
          r"\d+ accounts", r"account mapping"],
         [r"\baccounts?\b", r"\bplanning\b"]),

        ("quota-metrics", "Quota, metrics & forecasting",
         [r"\bquota\b", r"\battainment\b", r"\bote\b", r"commission", r"comp plan",
          r"\bconversion rate", r"pipeline inflation", r"\bmetrics\b", r"\bpresident.s club"],
         [r"\bnumbers?\b", r"\bpercent", r"\b\d+%"]),
    ]),

    ("career", "Job Search & Career", [
        ("resumes", "Resumes & applications",
         [r"\bresume", r"\bcv\b", r"applicant tracking", r"\bats\b", r"job (board|posting|description)",
          r"applied", r"applications?", r"land(ing)? (a|your|my) (next )?(job|role|gig)",
          r"remote jobs?"],
         [r"\bapply\b", r"\bhiring\b"]),

        ("interviewing", "Interviewing",
         [r"interview", r"screening call", r"hiring manager", r"candidates?",
          r"final round", r"\bhired?\b", r"mock", r"interview question"],
         [r"\brecruiter", r"\bpanel\b"]),

        ("hm-outreach", "Outreach to hiring managers",
         [r"wanting a job at", r"reach(ing)? out to (the )?hiring", r"candidate email",
          r"inbound candidate", r"stood out.{0,25}(hiring|manager|role)",
          r"cold (email|outreach).{0,25}(job|role|hiring)", r"break through the noise.{0,20}job"],
         [r"stand out", r"\bnote\b"]),

        ("offers-comp", "Offers, comp & equity",
         [r"\bequity\b", r"stock option", r"\bvesting\b", r"job offers?", r"counter.?offer",
          r"negotiat\w* (your |the )?(salary|comp|offer)", r"compensation",
          r"questions i.d ask", r"evaluat\w* (a |the )?(company|role|opportunity)"],
         [r"\bsalary\b", r"\bcomp\b", r"\boffer\b"]),

        ("job-hunt-strategy", "Layoffs & job-hunt strategy",
         [r"laid off", r"layoff", r"job market", r"job search", r"job hunt",
          r"\bland(ing)? (my|your) next", r"got affected by", r"resources you can use to land",
          r"career (site|change|direction|pivot)"],
         [r"\bmarket\b", r"\bsearch\b"]),

        ("growth-mindset", "Career growth & mindset",
         [r"mindset", r"\bhabits?\b", r"burn.?out", r"\bpromotion\b", r"productivity",
          r"top 1%", r"earn(ing)? over \$?\d", r"\$\d+k?/?(year|yr)", r"best sellers do",
          r"discipline", r"personal brand", r"\bcoach(ing)? (dozens|sellers|reps)"],
         [r"\bcareer\b", r"\bgrow(th)?\b", r"\bsuccess\b"]),
    ]),

    ("tools", "Tools & AI", [
        ("ai-selling", "AI for selling",
         [r"chatgpt", r"gpt-?\d", r"\bclaude\b", r"\bllm", r"artificial intelligence",
          r"\bai\b.{0,20}(sales|seller|rep|prospect|outreach|email)", r"\bprompts?\b",
          r"ai tools?", r"ai.native"],
         [r"\bai\b", r"\bautomat"]),

        ("tech-stack", "Sales tech stack",
         [r"tech stack", r"tool stack", r"chrome extension", r"\bclay\b", r"\bgong\b",
          r"outreach\.io", r"\bapollo\b", r"salesloft", r"\bzoominfo", r"\bcrm\b",
          r"tools i can.t live without", r"\d+ tools"],
         [r"\btools?\b", r"\bsoftware\b", r"\bstack\b"]),
    ]),

    ("leadership", "Sales Leadership", [
        ("coaching-teams", "Coaching & managing reps",
         [r"my (team|org|reps)", r"sales manager", r"sales leader", r"coach(ing|ed) (a|my|the) (team|rep)",
          r"1:1", r"onboard", r"\bramp\b", r"reps hitting quota", r"i hired", r"managing the whole"],
         [r"\bmanager\b", r"\bleader", r"\bteam\b"]),

        ("gtm-strategy", "GTM strategy & org design",
         [r"go.?to.?market", r"\bgtm\b", r"sales process", r"full.?cycle ae", r"\bsdr\b.{0,25}strategy",
          r"bdr.{0,10}strategy", r"inbound.{0,15}outbound", r"sales methodolog",
          r"demand gen", r"\bmarketing team"],
         [r"\bstrategy\b", r"\bprocess\b", r"\bmodel\b"]),
    ]),

    ("other", "Not Sales", [
        # Deliberately narrow. These fire only against the title + opening of the
        # body (see classify), because a sales post that merely links a podcast or
        # mentions Nvidia is still a sales post. Trusting a body-wide match here
        # wrongly exiled a cold-call post and an SDR job-hunt resource list.
        ("not-sales", "Off-topic saves",
         [r"stable diffusion", r"dall-?e", r"\bselenium\b", r"\bkatalon\b", r"github repos",
          r"borges", r"magic johnson", r"\bnvidia\b", r"cyber monday", r"\bturo\b",
          r"buying a service business", r"startup launch plan", r"data science",
          r"machine learning", r"\bkaggle\b", r"\bsiri\b", r"ai tutor"],
         []),
    ]),
]

TOPIC_META = {}
for shelf_key, shelf_label, topics in TAXONOMY:
    for key, label, strong, weak in topics:
        TOPIC_META[key] = {
            "label": label,
            "shelf": shelf_key,
            "shelf_label": shelf_label,
            "strong": [re.compile(p, re.I) for p in strong],
            "weak": [re.compile(p, re.I) for p in weak],
        }

SHELVES = [(k, l, [t[0] for t in ts]) for k, l, ts in TAXONOMY]


def score_post(title, body, extra=""):
    """Return {topic: score}. Opening line counts double."""
    scores = {}
    for key, meta in TOPIC_META.items():
        s = 0
        for rx in meta["strong"]:
            if rx.search(title):
                s += 6
            if rx.search(body) or (extra and rx.search(extra)):
                s += 3
        for rx in meta["weak"]:
            if rx.search(title):
                s += 2
            if rx.search(body):
                s += 1
        if s:
            scores[key] = s
    return scores


# Off-topic posts whose title gives nothing to match on. Checked by hand:
#   49  ChatGPT used to dispute a car insurance claim
#   206 a ChatGPT "AI tutor" prompt showcase, nothing to do with selling
#   264 podcast on acquiring and flipping SaaS startups, not an AE topic
OFF_TOPIC_IDS = {49, 206, 264}


def classify(title, body, extra="", post_id=None):
    """-> (primary_topic, [secondary_topics])"""
    if post_id in OFF_TOPIC_IDS:
        return "not-sales", []

    scores = score_post(title, body, extra)
    if not scores:
        return "not-sales", []

    # An off-topic post should not win on a stray match buried in the body. Judge
    # the title only: a sales post that happens to list "machine learning" among
    # in-demand skills is still a sales post.
    if "not-sales" in scores:
        if any(rx.search(title) for rx in TOPIC_META["not-sales"]["strong"]):
            return "not-sales", []
        del scores["not-sales"]
    if not scores:
        return "not-sales", []

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    primary = ranked[0][0]
    top = ranked[0][1]
    # Secondaries feed search and "related" links, so be generous: a topic needs
    # a real signal of its own and to be within reach of the winner, not to tie it.
    secondary = [k for k, v in ranked[1:] if v >= 6 and v >= top * 0.30][:4]
    return primary, secondary
