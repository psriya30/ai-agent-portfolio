import re
from dataclasses import dataclass
from typing import Optional, List, Tuple

from smolagents.models import LiteLLMModel


# -------------------------
# Helpers (shared)
# -------------------------

def clean_value(s: str) -> str:
    return s.strip().strip("-").strip(":").strip()


def first_match(pattern: str, text: str) -> Optional[str]:
    m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return clean_value(m.group(1)) if m else None


def all_matches(pattern: str, text: str) -> List[str]:
    return [clean_value(x) for x in re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)]


def format_output(
    name: str,
    contact: str,
    location: str,
    exp: str,
    skills: str,
    degree: str,
    passout: str,
    college: str,
) -> str:
    return (
        f"Name: {name}\n"
        f"Contact: {contact}\n"
        f"Current location: {location}\n"
        f"Years of Experience: {exp}\n"
        f"Skills: {skills}\n"
        f"Degree: {degree}\n"
        f"Passout year: {passout}\n"
        f"College name: {college}\n"
    )


def not_mentioned(x: Optional[str]) -> str:
    return x if x and x.strip() else "Not mentioned"


# -------------------------
# MODE 1: Structured extraction (rule-based)
# -------------------------

def extract_field(text: str, keys: List[str]) -> Optional[str]:
    for k in keys:
        # matches: "Name - Ram", "Name: Ram", "Name-राम" etc.
        pattern = rf"^{re.escape(k)}\s*[-:]\s*(.+)$"
        val = first_match(pattern, text)
        if val:
            return val
    return None


def extract_contact_strict(text: str) -> Optional[str]:
    # Prefer mobile: +91 optional, then 10 digits
    # Valid India mobile: 10 digits starting 6-9
    m = re.search(r"(?:\+91[\s-]*)?([6-9]\d{9})\b", text)
    if m:
        return m.group(1)

    # If there is a phone-like field but invalid (e.g., 9 digits), treat as not mentioned (your rule)
    if re.search(r"(phone|mobile|contact)\s*[-:]", text, flags=re.IGNORECASE):
        return None

    return None


def extract_skills_merge(text: str) -> Optional[str]:
    lines = all_matches(r"^Skills?\s*[-:]\s*(.+)$", text)
    if not lines:
        return None

    seen = set()
    merged = []
    for line in lines:
        parts = [p.strip() for p in line.split(",") if p.strip()]
        for p in parts:
            key = p.lower()
            if key not in seen:
                seen.add(key)
                merged.append(p)
    return ", ".join(merged) if merged else None


def extract_experience_structured(text: str) -> Optional[str]:
    # expects: "10 years 3 months"
    m = re.search(r"(\d+)\s*years?\s*(\d+)\s*months?", text, flags=re.IGNORECASE)
    if not m:
        return None
    years = int(m.group(1))
    months = int(m.group(2))
    return f"{years} years {months} months (rounded down: {years} years)"


def analyze_mode_1_structured(text: str) -> str:
    name = extract_field(text, ["Name"])
    contact = extract_contact_strict(text)
    location = extract_field(text, ["Current location", "Location"])
    exp = extract_experience_structured(text)

    skills = extract_skills_merge(text)
    degree = extract_field(text, ["Degree"])
    passout = extract_field(text, ["Passout year", "Passout"])
    college = extract_field(text, ["College name", "Colege name", "College"])

    return format_output(
        name=not_mentioned(name),
        contact=not_mentioned(contact),
        location=not_mentioned(location),
        exp=not_mentioned(exp),
        skills=not_mentioned(skills),
        degree=not_mentioned(degree),
        passout=not_mentioned(passout),
        college=not_mentioned(college),
    )


# -------------------------
# MODE 2: Messy extraction (Regex + LLM Hybrid)
# -------------------------

def regex_email(text: str) -> Optional[str]:
    m = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, flags=re.IGNORECASE)
    return m.group(0) if m else None


def regex_mobile_india(text: str) -> Optional[str]:
    m = re.search(r"(?:\+91[\s-]*)?([6-9]\d{9})\b", text)
    return m.group(1) if m else None


def extract_year_ranges(text: str) -> List[Tuple[int, int]]:
    # Very simple: 2018-2021 or 2018–2021
    pairs = re.findall(r"\b(19\d{2}|20\d{2})\s*[–\-]\s*(19\d{2}|20\d{2})\b", text)
    out = []
    for a, b in pairs:
        out.append((int(a), int(b)))
    return out


def merge_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not ranges:
        return []
    ranges = sorted(ranges)
    merged = [ranges[0]]
    for s, e in ranges[1:]:
        ps, pe = merged[-1]
        if s <= pe:  # overlap
            merged[-1] = (ps, max(pe, e))
        else:
            merged.append((s, e))
    return merged


def calc_experience_years_months_from_ranges(ranges: List[Tuple[int, int]]) -> Optional[str]:
    if not ranges:
        return None
    merged = merge_ranges(ranges)

    # Approx: treat year->year as whole years (simple beginner-safe)
    total_years = sum(max(0, e - s) for s, e in merged)
    # months unknown in this simple parser
    years = total_years
    months = 0
    return f"{years} years {months} months (rounded down: {years} years)"


@dataclass
class LLMExtractResult:
    name: str
    location: str
    skills: str
    degree: str
    passout: str
    college: str


def llm_extract_fields(text: str, model: LiteLLMModel) -> LLMExtractResult:
    prompt = f"""
You extract resume fields from messy text.

STRICT RULES:
- Do NOT invent phone numbers, emails, dates, years, or numbers.
- Copy any names/skills/degree/college words exactly if present.
- If a field is missing, output: Not mentioned
- Output must be EXACTLY 6 lines, in this exact format:
Name: ...
Current location: ...
Skills: ...
Degree: ...
Passout year: ...
College name: ...

TEXT:
{text}
""".strip()

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    resp = model(messages).content.strip()

    def pick(line_key: str) -> str:
        m = re.search(rf"^{re.escape(line_key)}\s*(.+)$", resp, flags=re.IGNORECASE | re.MULTILINE)
        return clean_value(m.group(1)) if m else "Not mentioned"

    return LLMExtractResult(
        name=pick("Name:"),
        location=pick("Current location:"),
        skills=pick("Skills:"),
        degree=pick("Degree:"),
        passout=pick("Passout year:"),
        college=pick("College name:"),
    )


def analyze_mode_2_messy(text: str) -> str:
    model = LiteLLMModel(model_id="ollama/phi3")

    # 1) Regex first (high precision)
    contact_mobile = regex_mobile_india(text)  # your rule: only valid mobile accepted
    # (You can also extract email if you want later — currently output format has only Contact)
    # email = regex_email(text)

    # 2) Experience from ranges (beginner version)
    ranges = extract_year_ranges(text)
    exp = calc_experience_years_months_from_ranges(ranges)

    # 3) LLM for semantic fields (only where needed)
    llm = llm_extract_fields(text, model)

    # 4) Skills merge/dedupe (even in messy mode)
    if llm.skills != "Not mentioned":
        parts = [p.strip() for p in llm.skills.split(",") if p.strip()]
        seen = set()
        merged = []
        for p in parts:
            key = p.lower()
            if key not in seen:
                seen.add(key)
                merged.append(p)
        skills = ", ".join(merged) if merged else "Not mentioned"
    else:
        skills = "Not mentioned"

    return format_output(
        name=not_mentioned(llm.name),
        contact=not_mentioned(contact_mobile),  # strict: invalid => Not mentioned
        location=not_mentioned(llm.location),
        exp=not_mentioned(exp),
        skills=skills,
        degree=not_mentioned(llm.degree),
        passout=not_mentioned(llm.passout),
        college=not_mentioned(llm.college),
    )


# -------------------------
# Runner
# -------------------------

if __name__ == "__main__":
    structured_sample = """Name -Ram Kumar
Contact-9876543210,987654321
Current location-Bengaluru,Karnataka
year of experience: 10 years 3 months
skills:java,python,AI/ML
Skills: SQL
Degree:Btech
Passout:2015
Colege name:XYZ
"""

    messy_sample = """Ram Kumar is a passionate software engineer.
He has worked at multiple companies from 2018-2020 and 2019-2022.
Currently based in Bangalore.
Skills include backend systems, Python, Java.
Education: XYZ Institute of Technology, BTech, 2015.
Mobile: +91 9876543210
"""

    print("=== MODE 1 (Structured) ===")
    print(analyze_mode_1_structured(structured_sample))

    print("=== MODE 2 (Messy: Regex + LLM) ===")
    print(analyze_mode_2_messy(messy_sample))