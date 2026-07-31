#!/usr/bin/env python3
"""All README copy in one place, so the wording is edited here and nowhere else.

Every claim below is traceable to something checkable: the repositories, the
company site, or the CV. Deliberately excluded: security implementation detail
from the private SkillsBIT repos, and raw commit counts (223 of 314 carry an AI
co-author trailer, so volume is the weakest available proof).
"""

# "exact"   -> 1,939 CONTRIBUTIONS SINCE JUL 2022
# "rounded" -> 1,900+ CONTRIBUTIONS SINCE JUL 2022  (rounds down, never overstates)
COUNT_STYLE = "exact"

HERO_NAME = "AMANI M AL-ZOUBI"
HERO_ROLE = "FULL-STACK DEVELOPER"
HERO_ORG = "// SKILLSBIT"

TAGLINES = [
    "Full-stack developer, front end and API",
    "Both ends of the same system",
    "Django  ·  DRF  ·  Next.js  ·  TypeScript  ·  PostgreSQL",
    "Amman, Jordan  ·  open to remote",
]

# label, value. "|" wraps a punctuation glyph that gets the muted colour,
# "|>|" becomes a green arrow.
CALIBRATION = [
    ("ROLE", "Full-stack developer, front end and API"),
    ("COMPANY", "SkillsBIT |·| enterprise IT, engineered to scale"),
    ("BASED", "Amman, Jordan |·| open to remote"),
    ("FRONT END", "Next.js |·| React |·| TypeScript |·| Tailwind |·| Three.js"),
    ("BACK END", "Django |·| DRF |·| PostgreSQL |·| ASP.NET Core"),
    ("ORIGIN", "BSc Electrical Engineering |>| RF systems |>| software"),
]

ABOUT = [
    "I build both ends of the same system. The SkillsBIT site runs on a Next.js front end "
    "and a Django REST API that I wrote and maintain. The dental platform is the same story: "
    "a React and TypeScript front end carrying an interactive 3D tooth model, sitting on a "
    "Django backend for booking, records and clinic administration. Working across the whole "
    "stack is the point, not a compromise.",

    "**[SkillsBIT](https://www.skilsbit.com/)** builds, secures and scales the systems modern "
    "companies run on, then trains their people to own them. Founded in 2022 and based in "
    "Amman, the company works across infrastructure and cloud, software development, "
    "cybersecurity, data and AI, consulting and emerging technology, with an academy alongside "
    "it. My work sits on the software side: I design the data models, write the APIs and build "
    "the interfaces that go on top of them.",

    "I came to software from **electrical engineering**. A BSc at the University of Jordan, then "
    "a year on radio frequency systems at the SESAME synchrotron, writing MATLAB and Python to "
    "simulate and tune RF performance. That work fixed one habit permanently: a system either "
    "behaves within tolerance or it does not, and no opinion changes the reading.",

    "The route since has been deliberate rather than accidental. A 900-hour ASAC and Code Fellows "
    "programme in 2022, a year teaching it back as a teaching assistant, prompt design and "
    "evaluation at MENADEVS through 2024, then production Django and TypeScript from 2025. "
    "Each stack came from needing it, and the previous one never went to waste.",

    "Concretely, that looks like multi-tenant data models scoped per company, append-only audit "
    "logging, several hundred automated tests running against PostgreSQL in CI, and deployments "
    "on Render, Vercel and Neon. I care about REST APIs that are dull to consume and data models "
    "that survive the second feature request.",
]

SKILLSBIT_INTRO = (
    "SkillsBIT delivers enterprise IT across six practice areas and runs a bilingual academy "
    "alongside it. On the build side, systems are designed to be deployed per client, each with "
    "its own database and environment, so onboarding the next customer is configuration rather "
    "than a rewrite. A selection of what I have worked on:"
)

# tag, title, description lines, stack line, accent ("blue" or "green")
WORK = [
    ("WEB", "SkillsBIT platform",
     ["The live company site and the API behind it: service catalogue,",
      "enquiries, academy courses and enrolments, client project portal,",
      "support ticketing and role-based dashboards."],
     "Next.js  ·  Django 5.2  ·  DRF 3.17  ·  PostgreSQL", "blue"),

    ("DEN", "Dental clinic system",
     ["Front end and API. Public catalogue, online booking, patient portal",
      "and staff administration, with an interactive 3D tooth model mapped",
      "to FDI notation and a treatment cost calculator."],
     "Next.js 15  ·  React 19  ·  Three.js  ·  Django REST", "green"),

    ("ERP", "ERP and HR backend",
     ["Employee records, organisation structure and a ledger-backed leave",
      "engine on a multi-tenant data model scoped per company, with an",
      "append-only audit log."],
     "Django  ·  DRF  ·  PostgreSQL", "blue"),

    ("EV", "PlugSpot",
     ["Personal project. An EV charging reservation API with geolocated",
      "stations, per-port scheduling and phone-number authentication",
      "localised for Jordan."],
     "Django 5.2  ·  DRF", "green"),

    ("EDU", "ISOEnroll and ISOExam",
     ["Personal projects built alongside my assessment work: admissions",
      "tracking with student registration and events, plus a separate",
      "examination platform."],
     "Django 5.2  ·  DRF  ·  SimpleJWT", "blue"),

    ("+", "And more in build",
     ["Further systems are in progress across the SkillsBIT product line",
      "and in my own repositories. Most of the code is private, so I am",
      "glad to walk through architecture on a call."],
     "Django  ·  TypeScript  ·  PostgreSQL", "green"),
]

WORK_NOTE = (
    "Most of this code is private. I am glad to screen-share it and talk through the "
    "trade-offs on a call."
)

STACK_ROWS = [
    ("FRONT END", ["ts", "js", "react", "nextjs", "tailwind", "threejs", "html", "css"]),
    ("BACK END", ["py", "django", "cs", "dotnet", "nodejs", "express"]),
    ("DATA AND OPS", ["postgres", "mongodb", "docker", "git", "github", "githubactions",
                      "postman", "vercel"]),
]
STACK_ALSO = "DRF  ·  SimpleJWT  ·  Render  ·  Neon  ·  Cloudinary  ·  pytest  ·  ruff  ·  mypy"
STACK_PRACTICE = ("A regression test with every fix   ·   CI against PostgreSQL   ·   "
                  "Phased branches and pull requests   ·   Mentoring")

TRAJECTORY = [
    ("01", "RF Engineering Intern", "SESAME Synchrotron", "Jun 2021 |>| Jul 2022",
     ["Analysed RF cavities and wrote MATLAB and Python to simulate and tune system",
      "performance. Learned to trust the instrument over the intuition."]),
    ("02", "Teaching Assistant, Coding Program", "ASAC", "Mar 2023 |>| Mar 2024",
     ["Mentored bootcamp developers through their first production code, contributed to",
      "curriculum, and assessed progress through technical interviews."]),
    ("03", "AI Prompt Engineer", "MENADEVS", "Mar 2024 |>| Dec 2024",
     ["Designed and iterated prompts for generative models across several industries,",
      "running structured evaluation to make outputs reliable enough to ship."]),
    ("04", "BTEC IT Internal Verifier", "ISO Education Schools", "Jan 2025 |>| Present",
     ["Verify assessment against BTEC and Pearson standards and hold grading consistent.",
      "Held alongside the engineering work at SkillsBIT."]),
]

EDUCATION = [
    ("ASAC / Code Fellows", "Full Stack Web Development, 900-hour intensive", "2022 to 2023"),
    ("University of Jordan", "BSc Electrical Engineering", "2014 to 2019"),
]

CONTACT_INTRO = ("Open to full-time, remote and contract work. Email reaches me fastest "
                 "and I answer.")

STRAPS = {
    "stack": "FRONT END AND BACK END, IN PRODUCTION",
    "work": "SELECTED SYSTEMS, MOST OF THEM PRIVATE",
    "trajectory": "FOUR DISCIPLINES, ONE DIRECTION",
}

SIGN_OFF = "Measure, don't guess."
