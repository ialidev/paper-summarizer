"""
summarizer.py
تلخيص كل قسم من الورقة البحثية لحاله باستخدام خوارزمية TextRank
(استخراجية - Extractive)، بدل الاعتماد الكامل على LLM API جاهزة.

TextRank ببساطة: يبني رسم بياني (graph) من الجمل، ويحسب مدى تشابه
كل جملة بالباقي، ثم يختار الجمل "المركزية" الأكثر تمثيلاً للنص —
نفس فكرة PageRank بس على مستوى الجمل بدل صفحات الويب.
"""

import textstat
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer


def summarize_section(text: str, sentence_count: int = 3) -> str:
    """يلخّص قسم واحد إلى عدد محدد من الجمل الأهم."""
    if not text or len(text.split()) < 30:
        # نص قصير جدًا، ما يحتاج تلخيص
        return text

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)

    return " ".join(str(sentence) for sentence in summary_sentences)


def summarize_sections(sections: dict, sentence_count: int = 3) -> dict:
    """يلخّص كل الأقسام المستخرجة من الورقة، قسم بقسم."""
    summaries = {}
    for name, text in sections.items():
        summaries[name] = summarize_section(text, sentence_count)
    return summaries


def readability_report(original_text: str, simplified_text: str) -> dict:
    """
    يقارن سهولة القراءة قبل وبعد التبسيط باستخدام Flesch Reading Ease.
    كل ما زاد الرقم، كل ما كان النص أسهل للقراءة (0-100).
    """
    return {
        "before": round(textstat.flesch_reading_ease(original_text), 1),
        "after": round(textstat.flesch_reading_ease(simplified_text), 1),
        "before_grade": textstat.text_standard(original_text, float_output=False),
        "after_grade": textstat.text_standard(simplified_text, float_output=False),
    }


if __name__ == "__main__":
    import sys
    from pdf_extractor import extract_paper

    if len(sys.argv) < 2:
        print("الاستخدام: python summarizer.py path/to/paper.pdf")
        sys.exit(1)

    paper = extract_paper(sys.argv[1])
    summaries = summarize_sections(paper["sections"])

    for name, summary in summaries.items():
        print(f"\n=== {name.upper()} ===")
        print(summary)

    full_summary = " ".join(summaries.values())
    report = readability_report(paper["raw_text"], full_summary)
    print("\n--- تقرير سهولة القراءة ---")
    print(f"قبل التبسيط : {report['before']} ({report['before_grade']})")
    print(f"بعد التبسيط : {report['after']} ({report['after_grade']})")
