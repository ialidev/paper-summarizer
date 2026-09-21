"""
main.py
نقطة الدخول الرئيسية للأداة.
يجمع: استخراج PDF -> تحديد المصطلحات الصعبة -> تلخيص كل قسم -> تقرير سهولة القراءة

الاستخدام:
    python main.py path/to/paper.pdf
"""

import sys
import json

from pdf_extractor import extract_paper
from term_extractor import load_model, extract_terms_with_context
from summarizer import summarize_sections, readability_report


def run(pdf_path: str) -> dict:
    print(f"[1/4] استخراج النص من {pdf_path} ...")
    paper = extract_paper(pdf_path)

    print(f"[2/4] تحميل نموذج spaCy واكتشاف المصطلحات الصعبة ...")
    nlp = load_model()
    terms = extract_terms_with_context(paper["raw_text"], nlp)

    print(f"[3/4] تلخيص {len(paper['sections'])} قسم ...")
    summaries = summarize_sections(paper["sections"])

    print(f"[4/4] حساب تقرير سهولة القراءة ...")
    full_summary_text = " ".join(summaries.values())
    report = readability_report(paper["raw_text"], full_summary_text)

    return {
        "sections_found": list(paper["sections"].keys()),
        "summaries": summaries,
        "difficult_terms": terms,
        "readability": report,
    }


def print_report(result: dict) -> None:
    print("\n" + "=" * 50)
    print("ملخص الورقة البحثية")
    print("=" * 50)

    for section, summary in result["summaries"].items():
        print(f"\n--- {section.upper()} ---")
        print(summary)

    print("\n" + "=" * 50)
    print(f"المصطلحات الصعبة ({len(result['difficult_terms'])})")
    print("=" * 50)
    for item in result["difficult_terms"]:
        print(f"• {item['term']}")

    r = result["readability"]
    print("\n" + "=" * 50)
    print("سهولة القراءة (Flesch Reading Ease, 0-100)")
    print("=" * 50)
    print(f"قبل: {r['before']}  |  بعد: {r['after']}")
    print(f"المستوى الدراسي المطلوب قبل: {r['before_grade']}")
    print(f"المستوى الدراسي المطلوب بعد: {r['after_grade']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("الاستخدام: python main.py path/to/paper.pdf")
        sys.exit(1)

    result = run(sys.argv[1])
    print_report(result)

    # حفظ النتيجة كـ JSON لاستخدامها لاحقًا (مثلاً بواجهة ويب)
    output_path = "summary_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✓ تم حفظ النتيجة الكاملة في {output_path}")
