import argparse
import json
import re
from pathlib import Path

import fitz


MAX_SECTION = 358


def clean(text):
    text = text.replace("\u00ad", "")
    text = text.replace("\r", "\n")

    # Fix common mojibake from PDF extraction
    replacements = {
        "â€”": "—",
        "â€“": "–",
        "â€˜": "‘",
        "â€™": "’",
        "â€œ": "“",
        "â€": "”",
        "â€¦": "…",
        "â€": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_pdf_pages(pdf_path):
    doc = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc):
        text = page.get_text("text")

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    doc.close()

    return pages


def find_act_start(pages):

    # We need the actual Act, not the table of contents.
    #
    # Search for the page containing:
    #
    # ACT NO. 45 OF 2023
    #
    # followed by:
    #
    # An Act to consolidate and amend...

    for i, page in enumerate(pages):

        text = page["text"]

        if (
            re.search(
                r"ACT\s+NO\.\s*45\s+OF\s+2023",
                text,
                re.IGNORECASE
            )
            and
            re.search(
                r"An\s+Act\s+to\s+consolidate\s+and\s+amend",
                text,
                re.IGNORECASE
            )
        ):

            return i

    raise RuntimeError(
        "Could not locate the beginning of the BNS Act."
    )


def is_section_start(line):

    # Match:
    #
    # 1. Short title...
    # 2. Definitions...
    #
    match = re.match(
        r"^\s*(\d{1,3})[.\u2013\u2014-]\s*(.+)$",
        line
    )

    if not match:
        return None

    number = int(match.group(1))

    if number < 1 or number > MAX_SECTION:
        return None

    return number, match.group(2).strip()


def build_sections(pages, start_page):

    sections = []

    current = None

    for page in pages[start_page:]:

        lines = page["text"].splitlines()

        for line in lines:

            result = is_section_start(line)

            if result is not None:

                number, heading = result

                # Ignore duplicate occurrences caused by headers,
                # contents, etc.
                if current is not None and number == current["number"]:
                    current["text_lines"].append(line)
                    continue

                # If the number goes backwards, it is probably
                # a page/header artifact.
                if current is not None and number < current["number"]:
                    current["text_lines"].append(line)
                    continue

                # Save previous section
                if current is not None:

                    sections.append({
                        "section": str(current["number"]),
                        "heading": current["heading"],
                        "text": clean(
                            "\n".join(
                                current["text_lines"]
                            )
                        )
                    })

                # Start new section
                current = {
                    "number": number,
                    "heading": heading,
                    "text_lines": [line]
                }

            else:

                if current is not None:
                    current["text_lines"].append(line)

    # Save final section
    if current is not None:

        sections.append({
            "section": str(current["number"]),
            "heading": current["heading"],
            "text": clean(
                "\n".join(
                    current["text_lines"]
                )
            )
        })

    # Keep only unique section numbers.
    # The first valid occurrence is retained.
    unique = {}

    for section in sections:

        number = int(section["section"])

        if number not in unique:
            unique[number] = section

    sections = [
        unique[number]
        for number in sorted(unique)
    ]

    return sections


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pdf",
        required=True
    )

    parser.add_argument(
        "--out",
        required=True
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    output_path = Path(args.out)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    print(f"Reading PDF: {pdf_path}")

    pages = extract_pdf_pages(pdf_path)

    print(
        f"Extracted {len(pages)} PDF pages"
    )

    start_page = find_act_start(pages)

    print(
        f"Actual Act starts around PDF page {start_page + 1}"
    )

    sections = build_sections(
        pages,
        start_page
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        for section in sections:

            f.write(
                json.dumps(
                    section,
                    ensure_ascii=False
                )
                + "\n"
            )

    print(
        f"Wrote {len(sections)} sections -> {output_path}"
    )

    if sections:

        print(
            f"First section: {sections[0]['section']}"
        )

        print(
            f"Last section: {sections[-1]['section']}"
        )

    section_numbers = {
        int(x["section"])
        for x in sections
    }

    missing = [
        i
        for i in range(1, MAX_SECTION + 1)
        if i not in section_numbers
    ]

    if not missing:

        print(
            "VALIDATION PASSED: Sections 1-358 found."
        )

    else:

        print(
            f"Missing {len(missing)} sections."
        )

        print(
            "Missing sections:",
            missing
        )


if __name__ == "__main__":
    main()