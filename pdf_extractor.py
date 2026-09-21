"""
pdf_extractor.py
استخراج النص من ورقة بحثية PDF وتقسيمه إلى أقسام منطقية
(Introduction, Methods, Results, Conclusion...)
"""

import re
import fitz  # PyMuPDF


# العناوين الشائعة بالأوراق البحثية (case-insensitive)
SECTION_HEADERS = [
    "abstract",
    "introduction",
    "related work",
    "background",
    "methodology",
    "methods",
    "approach",
    "experiments",
    "results",
    "discussion",
    "conclusion",
    "references",
]


def extract_raw_text(pdf_path: str) -> str:
    """يفتح ملف PDF ويسحب كل النص الخام منه صفحة بصفحة."""
    doc = fitz.open(pdf_path)
    full_text = []
    for page in doc:
        # "text" mode يتعامل بشكل أفضل مع الأعمدة المزدوجة
        # مقارنة بالاستخراج الافتراضي البسيط
        full_text.append(page.get_text("text"))
    doc.close()
    return "\n".join(full_text)


def clean_text(text: str) -> str:
    """تنظيف النص من الفواصل غير المفيدة (hyphenation, أرقام صفحات متكررة...)."""
    # دمج الكلمات المقسومة بنهاية السطر: "opti-\nmization" -> "optimization"
    text = re.sub(r"-\n(\w)", r"\1", text)
    # استبدال أسطر فارغة متعددة بسطر واحد
    text = re.sub(r"\n{3,}", "\n\n", text)
    # إزالة أرقام الصفحات المنفردة بسطر لحالها
    text = re.sub(r"\n\d+\n", "\n", text)
    return text.strip()


def split_into_sections(text: str) -> dict:
    """
    يقسم النص الكامل إلى أقسام بناءً على العناوين المعروفة.
    يرجع dict: {اسم_القسم: نص_القسم}
    """
    # نبني نمط regex يبحث عن أي عنوان من القائمة في بداية سطر
    pattern = re.compile(
        r"^\s*(" + "|".join(SECTION_HEADERS) + r")\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    matches = list(pattern.finditer(text))
    sections = {}

    if not matches:
        # لو ما لقينا عناوين واضحة، نرجع النص كامل تحت "full_text"
        sections["full_text"] = text
        return sections

    for i, match in enumerate(matches):
        section_name = match.group(1).strip().lower()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        if section_text:
            sections[section_name] = section_text

    return sections


def extract_paper(pdf_path: str) -> dict:
    """الدالة الرئيسية: تاخذ مسار PDF وترجع نص خام + أقسام مقسّمة."""
    raw = extract_raw_text(pdf_path)
    cleaned = clean_text(raw)
    sections = split_into_sections(cleaned)
    return {
        "raw_text": cleaned,
        "sections": sections,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("الاستخدام: python pdf_extractor.py path/to/paper.pdf")
        sys.exit(1)

    result = extract_paper(sys.argv[1])
    print(f"تم استخراج {len(result['sections'])} قسم:")
    for name in result["sections"]:
        print(f"  - {name}")
