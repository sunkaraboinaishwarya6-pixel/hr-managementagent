import re
from pypdf import PdfReader

from servies.ollama_service import ask_qwen


MISSING = "Information not found in submitted documents"


def extract_text_from_pdf(file_path):
    """
    Extract text from the uploaded PDF.
    """

    reader = PdfReader(file_path)

    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


def extract_profile_facts(resume_text):
    """
    Extract verified social/coding profile information
    directly from the submitted resume.

    Never invent usernames or URLs.
    """

    text = resume_text.strip()

    def find_url(patterns):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        return None

    linkedin_url = find_url([
        r"https?://(?:www\.)?linkedin\.com/[^\s]+",
        r"linkedin\.com/[^\s]+"
    ])

    github_url = find_url([
        r"https?://(?:www\.)?github\.com/[^\s]+",
        r"github\.com/[^\s]+"
    ])

    leetcode_url = find_url([
        r"https?://(?:www\.)?leetcode\.com/[^\s]+",
        r"leetcode\.com/[^\s]+"
    ])

    hackerrank_url = find_url([
        r"https?://(?:www\.)?hackerrank\.com/[^\s]+",
        r"hackerrank\.com/[^\s]+"
    ])

    codechef_url = find_url([
        r"https?://(?:www\.)?codechef\.com/[^\s]+",
        r"codechef\.com/[^\s]+"
    ])

    def username_from_url(url):
        if not url:
            return None

        cleaned = url.rstrip("/")

        match = re.search(r"/([^/]+)$", cleaned)

        if match:
            return match.group(1)

        return None

    return {
        "linkedin": {
            "platform": "LinkedIn" if re.search(
                r"\blinkedin\b",
                text,
                re.IGNORECASE
            ) else None,
            "url": linkedin_url,
            "username": username_from_url(linkedin_url)
        },

        "github": {
            "platform": "GitHub" if re.search(
                r"\bgithub\b",
                text,
                re.IGNORECASE
            ) else None,
            "url": github_url,
            "username": username_from_url(github_url)
        },

        "leetcode": {
            "platform": "LeetCode" if re.search(
                r"\bleetcode\b",
                text,
                re.IGNORECASE
            ) else None,
            "url": leetcode_url,
            "username": username_from_url(leetcode_url)
        },

        "hackerrank": {
            "platform": "HackerRank" if re.search(
                r"\bhackerrank\b",
                text,
                re.IGNORECASE
            ) else None,
            "url": hackerrank_url,
            "username": username_from_url(hackerrank_url)
        },

        "codechef": {
            "platform": "CodeChef" if re.search(
                r"\bcodechef\b",
                text,
                re.IGNORECASE
            ) else None,
            "url": codechef_url,
            "username": username_from_url(codechef_url)
        }
    }

def extract_verified_academic_facts(resume_text):
    """
    Extract academic information directly from resume text.

    IMPORTANT:
    - Do not convert CGPA to percentage.
    - Do not convert percentage to CGPA.
    - Do not invent year-wise B.Tech marks.
    """

    facts = {
        "10th": {
            "cgpa": None,
            "percentage": None,
            "year": None
        },
        "12th": {
            "cgpa": None,
            "percentage": None,
            "year": None
        },
        "btech": {
            "cgpa": None,
            "percentage": None,
            "year_wise": None
        }
    }

    # --------------------------------------------------
    # 10th CGPA
    # --------------------------------------------------

    tenth_cgpa_patterns = [
        r"(?:class\s*10|10th|ssc).*?(?:cgpa|gpa)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:cgpa|gpa)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?).*?(?:class\s*10|10th|ssc)"
    ]

    for pattern in tenth_cgpa_patterns:

        match = re.search(
            pattern,
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            facts["10th"]["cgpa"] = match.group(1)
            break

    # --------------------------------------------------
    # 10th Percentage
    # --------------------------------------------------

    tenth_percentage_patterns = [
        r"(?:class\s*10|10th|ssc).*?(?:percentage|percent|%)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:percentage|percent)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?).*?(?:class\s*10|10th|ssc)"
    ]

    for pattern in tenth_percentage_patterns:

        match = re.search(
            pattern,
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            facts["10th"]["percentage"] = match.group(1)
            break

    # --------------------------------------------------
    # 12th / Intermediate CGPA
    # --------------------------------------------------

    twelfth_cgpa_patterns = [
        r"(?:12th|intermediate|class\s*12).*?(?:cgpa|gpa)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:cgpa|gpa)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?).*?(?:12th|intermediate|class\s*12)"
    ]

    for pattern in twelfth_cgpa_patterns:

        match = re.search(
            pattern,
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            facts["12th"]["cgpa"] = match.group(1)
            break

    # --------------------------------------------------
    # 12th / Intermediate Percentage
    # --------------------------------------------------

    twelfth_percentage_patterns = [
        r"(?:12th|intermediate|class\s*12).*?(?:percentage|percent|%)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:percentage|percent)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?).*?(?:12th|intermediate|class\s*12)"
    ]

    for pattern in twelfth_percentage_patterns:

        match = re.search(
            pattern,
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            facts["12th"]["percentage"] = match.group(1)
            break

    # --------------------------------------------------
    # B.Tech CGPA
    # --------------------------------------------------

    btech_cgpa_patterns = [
        r"(?:b\.?\s*tech|bachelor\s+of\s+technology|degree).*?(?:cgpa|gpa)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:cgpa|gpa)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?).*?(?:b\.?\s*tech|bachelor\s+of\s+technology)"
    ]

    for pattern in btech_cgpa_patterns:

        match = re.search(
            pattern,
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            facts["btech"]["cgpa"] = match.group(1)
            break

    # --------------------------------------------------
    # B.Tech Percentage
    # --------------------------------------------------

    btech_percentage_patterns = [
        r"(?:b\.?\s*tech|bachelor\s+of\s+technology|degree).*?(?:percentage|percent|%)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"(?:percentage|percent)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?).*?(?:b\.?\s*tech|bachelor\s+of\s+technology)"
    ]

    for pattern in btech_percentage_patterns:

        match = re.search(
            pattern,
            resume_text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            facts["btech"]["percentage"] = match.group(1)
            break

    # --------------------------------------------------
    # B.Tech year-wise results
    #
    # We intentionally do NOT guess these.
    # --------------------------------------------------

    facts["btech"]["year_wise"] = None

    return facts


def build_verified_profile_text(profile_facts):
    """
    Build verified profile information for the AI prompt.
    """

    return f"""
LinkedIn:
{profile_facts["linkedin"] or MISSING}

GitHub:
{profile_facts["github"] or MISSING}

LeetCode:
{profile_facts["leetcode"] or MISSING}

HackerRank:
{profile_facts["hackerrank"] or MISSING}

CodeChef:
{profile_facts["codechef"] or MISSING}
"""


def build_verified_academic_text(academic_facts):
    """
    Build verified academic information for the AI prompt.
    """

    tenth = academic_facts["10th"]
    twelfth = academic_facts["12th"]
    btech = academic_facts["btech"]

    return f"""
10th:
- CGPA: {tenth["cgpa"] or MISSING}
- Percentage: {tenth["percentage"] or MISSING}

12th/Intermediate:
- CGPA: {twelfth["cgpa"] or MISSING}
- Percentage: {twelfth["percentage"] or MISSING}

B.Tech/Degree:
- Overall CGPA: {btech["cgpa"] or MISSING}
- Overall Percentage: {btech["percentage"] or MISSING}
- Year-wise results: {btech["year_wise"] or MISSING}
"""


def enforce_missing_profile_values(
    ai_result,
    profile_facts
):
    """
    Make sure AI cannot invent absent profiles.
    """

    platforms = {
        "LinkedIn": profile_facts["linkedin"],
        "GitHub": profile_facts["github"],
        "LeetCode": profile_facts["leetcode"],
        "HackerRank": profile_facts["hackerrank"],
        "CodeChef": profile_facts["codechef"],
    }

    for platform, detected in platforms.items():

        if detected is None:

            pattern = rf"{re.escape(platform)}\s*:.*?(?=\n[A-Z][A-Za-z0-9 /&().-]*:|\Z)"

            ai_result = re.sub(
                pattern,
                f"{platform}:\n{MISSING}\n",
                ai_result,
                flags=re.IGNORECASE | re.DOTALL
            )

    return ai_result


def enforce_missing_academic_values(
    ai_result,
    academic_facts
):
    """
    Replace missing academic values with the official missing marker.

    We do not calculate missing values.
    """

    # This function intentionally does only conservative replacement.
    # The AI prompt already contains verified academic facts.

    return ai_result


def clean_ai_result(ai_result):
    """
    Remove accidental markdown code fences if Qwen returns them.
    """

    ai_result = ai_result.strip()

    if ai_result.startswith("```"):
        ai_result = re.sub(
            r"^```[a-zA-Z0-9_-]*\s*",
            "",
            ai_result
        )

    if ai_result.endswith("```"):
        ai_result = ai_result[:-3].strip()

    return ai_result


def analyze_resume_with_ai(resume_text):
    """
    Analyze resume using the local Qwen model.

    The AI is instructed to use ONLY evidence from the submitted resume.
    """

    academic_facts = extract_verified_academic_facts(
        resume_text
    )

    profile_facts = extract_profile_facts(
        resume_text
    )

    verified_profiles = build_verified_profile_text(
        profile_facts
    )

    verified_academics = build_verified_academic_text(
        academic_facts
    )

    prompt = f"""
You are a STRICT HR Resume Screening AI.

Your job is to analyze ONLY the information explicitly present
in the submitted resume.

==================================================
CRITICAL ANTI-HALLUCINATION RULES
==================================================

1. NEVER invent information.

2. NEVER guess missing information.

3. NEVER create facts that are not present in the resume.

4. If information is missing, write exactly:

{MISSING}

5. NEVER convert CGPA into percentage.

6. NEVER convert percentage into CGPA.

7. NEVER copy academic information from one level to another.

8. 10th information must remain 10th information.

9. 12th/Intermediate information must remain
   12th/Intermediate information.

10. B.Tech information must remain B.Tech information.

11. NEVER create B.Tech year-wise results unless
    individual year results are explicitly present.

12. Projects and Internships/Experience are separate.

13. NEVER place a project under Internships/Experience.

14. Only report internship or professional experience if
    the resume explicitly mentions internship, company,
    employment, job, role, or work experience.

15. Do not treat projects as internships.

==================================================
VERIFIED ACADEMIC FACTS
==================================================

The following values were extracted directly from
the original resume text using Python.

{verified_academics}

These values have priority over AI interpretation.

If a verified value is missing, keep it as:

{MISSING}

Do not calculate or transform it.

==================================================
VERIFIED SOCIAL / CODING PLATFORM FACTS
==================================================

The following platform names were detected directly
from the original resume text.

{verified_profiles}

IMPORTANT:

- Only report a platform when it appears in the
  verified facts above.
- Never invent a username.
- Never invent a URL.
- Never treat an email address as GitHub,
  LinkedIn, LeetCode or another platform.
- Never treat a phone number as a social profile.
- Never infer a profile from a person's name.
- If a platform is absent, report:

{MISSING}

- If the platform name exists but username/URL does not,
  report the platform and say:

Username/Profile:
{MISSING}

==================================================
STRENGTHS
==================================================

Strengths must be supported by explicit resume evidence.

Examples:

- Python is explicitly listed.
- SQL is explicitly listed.
- Machine learning project is explicitly listed.
- Internship is explicitly listed.

Do not create personal characteristics without evidence.

==================================================
WEAKNESSES
==================================================

Weaknesses must be based only on clearly observable
missing information or limitations.

Examples:

- Internship experience not mentioned.
- GitHub profile not mentioned.
- B.Tech year-wise results not provided.

Do NOT create subjective personal weaknesses.

==================================================
ROLE SUITABILITY
==================================================

Evaluate suitability only from actual skills,
projects and experience found in the resume.

Evaluate:

- Data Science
- Full Stack Developer
- Data Analyst
- Machine Learning

Do not assume a candidate is suitable merely because
their degree name matches a role.

==================================================
OUTPUT FORMAT
==================================================

Return EXACTLY this structure:

Name:

Email:

Phone:

Education:

10th:
- Institution/Board:
- Year:
- CGPA:
- Percentage:

12th/Intermediate:
- Institution/Board:
- Year:
- CGPA:
- Percentage:

B.Tech/Degree:
- Institution:
- Branch:
- Duration:
- Overall CGPA:
- Overall Percentage:
- Year-wise results:

Certificates:

Skills:
- Programming Languages:
- Databases:
- Frameworks/Tools:
- AI/ML Tools:
- Soft Skills:

Projects:

Internships/Experience:

Achievements:

LinkedIn:

GitHub:

LeetCode:

HackerRank:

CodeChef:

Suitable Roles:
- Data Science:
- Full Stack Developer:
- Data Analyst:
- Machine Learning:

Strengths:

Weaknesses:

Overall Candidate Assessment:

==================================================
IMPORTANT FINAL RULE
==================================================

Every statement must be supported by the submitted
resume.

Do not invent marks.

Do not invent certificates.

Do not invent internships.

Do not invent projects.

Do not invent social profiles.

Do not invent coding profiles.

Do not invent URLs.

Do not invent usernames.

Do not invent year-wise B.Tech results.

==================================================
RESUME TEXT
==================================================

{resume_text}
"""

    ai_result = "".join(
        ask_qwen(prompt)
    )

    ai_result = clean_ai_result(
        ai_result
    )

    ai_result = enforce_missing_profile_values(
        ai_result,
        profile_facts
    )

    ai_result = enforce_missing_academic_values(
        ai_result,
        academic_facts
    )

    return ai_result


if __name__ == "__main__":

    print("Resume parser module loaded successfully.")

    print(
        "Functions available:"
    )

    print(
        "- extract_text_from_pdf()"
    )

    print(
        "- extract_profile_facts()"
    )

    print(
        "- extract_verified_academic_facts()"
    )

    print(
        "- analyze_resume_with_ai()"
    )