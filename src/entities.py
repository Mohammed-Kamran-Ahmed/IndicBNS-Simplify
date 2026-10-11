import re

PATTERNS=[
 re.compile(r"\\b(?:section|sec\\.?)\\s*(\\d+[A-Za-z]?)\\b",re.I),
 re.compile(r"\\bधारा\\s*(\\d+[A-Za-z]?)\\b"),
 re.compile(r"\\bసెక్షన్\\s*(\\d+[A-Za-z]?)\\b")
]
PENALTY_TERMS=["imprisonment","fine","punishment","life imprisonment","कारावास","जुर्माना","सजा","జైలు","జరిమానా","శిక్ష"]

def extract_entities(query,record):
    text=f"{query}\\n{record.get('heading','')}\\n{record.get('text','')}"
    sections=[]
    for p in PATTERNS: sections += [m.group(1) for m in p.finditer(text)]
    low=text.lower()
    return {"section_numbers":sorted(set(sections)),
            "penalty_terms":sorted({x for x in PENALTY_TERMS if x.lower() in low})}
