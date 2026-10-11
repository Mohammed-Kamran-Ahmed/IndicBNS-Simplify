import argparse
import json
from pathlib import Path


# Controlled multilingual retrieval terms.
# These are retrieval hints only.
# official_text remains unchanged.
ALIASES = {
    "303": {
        "hi": "चोरी चुराना चोरी करना चोरी करने पर सजा",
        "te": "దొంగతనం దొంగతనం చేయడం దొంగతనం చేస్తే శిక్ష",
        "en": "theft stealing stolen property punishment for theft"
    },
    "304": {
        "hi": "झपटमारी छीनना झपटकर चोरी",
        "te": "స్నాచింగ్ దోచుకోవడం లాక్కోవడం",
        "en": "snatching stealing by snatching"
    },
    "80": {
        "hi": "दहेज हत्या दहेज के लिए महिला की हत्या",
        "te": "కట్నం కోసం మహిళను చంపడం కట్నం మరణం",
        "en": "dowry death death of woman for dowry"
    },
    "351": {
        "hi": "आपराधिक धमकी धमकी डराना",
        "te": "క్రిమినల్ బెదిరింపు బెదిరించడం భయపెట్టడం",
        "en": "criminal intimidation threat threatening"
    },
    "356": {
        "hi": "मानहानि बदनामी प्रतिष्ठा को नुकसान",
        "te": "పరువు నష్టం అపకీర్తి ప్రతిష్టకు నష్టం",
        "en": "defamation damaging reputation"
    },
    "318": {
        "hi": "धोखाधड़ी धोखा छल करना",
        "te": "మోసం మోసం చేయడం మోసపూరిత చర్య",
        "en": "cheating fraud deception"
    },
    "319": {
        "hi": "प्रतिरूपण दूसरे व्यक्ति का रूप धारण करके धोखाधड़ी",
        "te": "మరొక వ్యక్తిగా నటించి మోసం చేయడం",
        "en": "cheating by personation impersonating another person"
    },
    "103": {
        "hi": "हत्या हत्या की सजा",
        "te": "హత్య హత్యకు శిక్ష",
        "en": "murder punishment for murder"
    },
    "109": {
        "hi": "हत्या का प्रयास हत्या करने का प्रयास",
        "te": "హత్యకు ప్రయత్నం హత్య చేయడానికి ప్రయత్నించడం",
        "en": "attempt to murder attempted murder"
    },
    "64": {
        "hi": "बलात्कार बलात्कार की सजा",
        "te": "బలాత్కారం అత్యాచారం బలాత్కారానికి శిక్ష",
        "en": "rape punishment for rape"
    }
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    rows = load(args.input)

    output = []

    for row in rows:
        section = str(row["section"])

        official_text = row["text"]

        aliases = ALIASES.get(
            section,
            {
                "en": row.get("heading", ""),
                "hi": "",
                "te": ""
            }
        )

        retrieval_text = " ".join(
            [
                f"section {section}",
                row.get("heading", ""),
                official_text,
                aliases.get("en", ""),
                aliases.get("hi", ""),
                aliases.get("te", "")
            ]
        )

        new_row = dict(row)

        new_row["official_text"] = official_text
        new_row["retrieval_text"] = retrieval_text

        output.append(new_row)

    output_path = Path(args.output)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        for row in output:
            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False
                ) + "\n"
            )

    print(
        f"Created multilingual retrieval corpus: "
        f"{len(output)} sections"
    )


if __name__ == "__main__":
    main()