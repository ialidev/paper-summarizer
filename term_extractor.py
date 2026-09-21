"""
term_extractor.py
اكتشاف المصطلحات التقنية الصعبة داخل نص الورقة البحثية،
بالاعتماد على spaCy + مقارنة تكرار الكلمات بلغة عامة.

المنطق:
1. نستخرج noun phrases (عبارات اسمية) عن طريق spaCy، لأن المصطلحات
   التقنية غالبًا تكون عبارات اسمية مركبة (multi-word terms)
   مثل "gradient descent" أو "attention mechanism".
2. أي عبارة نادرة الاستخدام باللغة العامة، لكنها تتكرر داخل الورقة
   نفسها أكثر من مرة، تعتبر مصطلح تقني مرشّح.
"""

from collections import Counter
import spacy

# قائمة كلمات شائعة جدًا نتجاهلها حتى لو تكررت (stopwords موسّعة)
COMMON_ACADEMIC_WORDS = {
    "we", "this", "paper", "study", "result", "results", "section",
    "figure", "table", "approach", "work", "method", "data", "model",
    "example", "case", "et al", "et al.",
}


def load_model():
    """يحمّل نموذج spaCy الإنجليزي الخفيف."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        raise RuntimeError(
            "نموذج spaCy غير مثبت. شغّل:\n"
            "python -m spacy download en_core_web_sm"
        )


def extract_candidate_terms(text: str, nlp, min_occurrences: int = 2) -> list[str]:
    """
    يرجع قائمة مرتبة بالمصطلحات المرشحة، الأكثر تكرارًا أولًا.
    """
    doc = nlp(text)

    phrase_counter = Counter()

    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()

        # نتجاهل العبارات القصيرة جدًا أو الطويلة جدًا
        word_count = len(phrase.split())
        if word_count < 2 or word_count > 4:
            continue

        # نتجاهل لو العبارة تحتوي كلمة أكاديمية شائعة فقط
        if phrase in COMMON_ACADEMIC_WORDS:
            continue

        # نتجاهل العبارات اللي كل كلماتها stopwords
        if all(token.is_stop for token in chunk):
            continue

        phrase_counter[phrase] += 1

    # نرشّح بس اللي تكررت min_occurrences مرة أو أكثر
    candidates = [
        phrase for phrase, count in phrase_counter.most_common()
        if count >= min_occurrences
    ]

    return candidates


def extract_terms_with_context(text: str, nlp, top_n: int = 15) -> list[dict]:
    """
    يرجع قائمة مصطلحات مع أول جملة ظهر فيها المصطلح (كسياق يساعد الشرح لاحقًا).
    """
    candidates = extract_candidate_terms(text, nlp)[:top_n]
    doc = nlp(text)
    sentences = list(doc.sents)

    results = []
    for term in candidates:
        context_sentence = ""
        for sent in sentences:
            if term in sent.text.lower():
                context_sentence = sent.text.strip()
                break
        results.append({"term": term, "context": context_sentence})

    return results


if __name__ == "__main__":
    import sys
    from pdf_extractor import extract_paper

    if len(sys.argv) < 2:
        print("الاستخدام: python term_extractor.py path/to/paper.pdf")
        sys.exit(1)

    nlp = load_model()
    paper = extract_paper(sys.argv[1])
    terms = extract_terms_with_context(paper["raw_text"], nlp)

    print(f"لقينا {len(terms)} مصطلح مرشّح:\n")
    for item in terms:
        print(f"• {item['term']}")
        if item["context"]:
            print(f"   السياق: {item['context'][:120]}...")
