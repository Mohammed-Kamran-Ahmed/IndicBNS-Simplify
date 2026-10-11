import os
from openai import OpenAI

SYSTEM='''You simplify legal text using ONLY the retrieved official provision.
Do not invent section numbers, penalties, exceptions, procedures, or facts.
If the provision does not answer the query, say so. Clearly separate official
text from the simplified explanation. This is informational, not legal advice.'''

def explain(query,record,language="English"):
    client=OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt=f'''Query: {query}
Language: {language}
Section: {record.get("section")}
Heading: {record.get("heading")}
Official text:
{record.get("text")}
Detected entities: {record.get("entities",{})}

Return section, a short description, a simple explanation, important penalty/entity
information, and state that the answer is based on the retrieved provision.'''
    r=client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),temperature=0,
        messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}])
    return r.choices[0].message.content
