"""
app.py
واجهة ويب بسيطة للأداة باستخدام Streamlit.
يرفع المستخدم ملف PDF، والتطبيق يطلع الملخص والمصطلحات الصعبة
وتقرير سهولة القراءة مباشرة بالمتصفح.
"""

import tempfile
import os

import streamlit as st

from pdf_extractor import extract_paper
from term_extractor import load_model, extract_terms_with_context
from summarizer import summarize_sections, readability_report


st.set_page_config(
    page_title="مبسّط الأبحاث العلمية",
    page_icon="📄",
    layout="wide",
)


@st.cache_resource
def get_nlp_model():
    """نحمّل نموذج spaCy مرة وحدة بس ونخزنه بالكاش (يبطئ أول تحميل فقط)."""
    return load_model()


def main():
    st.title("📄 مبسّط الأبحاث العلمية")
    st.markdown(
        "ارفع ورقة بحثية بصيغة PDF، وراح نطلع لك ملخص مبسّط، "
        "المصطلحات الصعبة، وتقرير سهولة القراءة."
    )

    uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

    if uploaded_file is None:
        st.info("ارفع ملف PDF فوق عشان نبدأ التحليل.")
        return

    with st.spinner("جاري تحليل الورقة... قد ياخذ دقيقة لأول تشغيل"):
        # نحفظ الملف المرفوع مؤقتًا عشان PyMuPDF يقدر يفتحه من مسار
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            paper = extract_paper(tmp_path)
            nlp = get_nlp_model()
            terms = extract_terms_with_context(paper["raw_text"], nlp)
            summaries = summarize_sections(paper["sections"])
            full_summary_text = " ".join(summaries.values())
            report = readability_report(paper["raw_text"], full_summary_text)
        finally:
            os.unlink(tmp_path)

    # -------- عرض النتائج --------
    col1, col2 = st.columns(2)
    col1.metric("سهولة القراءة قبل", report["before"])
    col2.metric("سهولة القراءة بعد", report["after"])

    st.subheader("📝 الملخص حسب الأقسام")
    for section, summary in summaries.items():
        with st.expander(section.upper(), expanded=True):
            st.write(summary if summary else "_(قسم قصير جدًا، ما احتاج تلخيص)_")

    st.subheader(f"🔑 المصطلحات الصعبة ({len(terms)})")
    for item in terms:
        with st.expander(item["term"]):
            st.write(item["context"] or "_ما لقينا سياق واضح لهذا المصطلح_")


if __name__ == "__main__":
    main()
