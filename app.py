import streamlit as st
import requests

# ---------- GUARDRAIL FUNCTION ----------
def is_valid_feedback(feedback):
    feedback_lower = feedback.lower()

    # 1️⃣ Too short → reject
    if len(feedback.strip()) < 20:
        return False

    # 2️⃣ Must contain product-related signals
    product_keywords = [
        "app", "feature", "bug", "issue", "error",
        "payment", "login", "crash", "slow",
        "support", "checkout", "onboarding", "ui", "ux"
    ]

    if not any(word in feedback_lower for word in product_keywords):
        return False

    # 3️⃣ Prompt injection patterns → reject
    blocked_patterns = [
        "ignore previous",
        "just output",
        "repeat after me",
        "write a song",
        "say this"
    ]

    for pattern in blocked_patterns:
        if pattern in feedback_lower:
            return False

    return True


# ---------- APP CONFIG ----------
st.set_page_config(page_title="Decision Intelligence Agent", layout="wide")

# ---------- HEADER ----------
st.title("🤖 Decision Intelligence Agent")
st.caption("AI-powered system to convert messy feedback into product decisions")

st.divider()

# ---------- INPUT ----------
feedback = st.text_area("Paste user feedback here:", height=150)

# ---------- BUTTON ----------
if st.button("Analyze Feedback"):

    # 🔹 Empty input
    if feedback.strip() == "":
        st.warning("Please enter some feedback")

    # 🔹 Guardrail check
    elif not is_valid_feedback(feedback):
        st.error("Invalid feedback detected. Please enter genuine product feedback.")
        st.stop()

    # 🔹 Main logic
    else:
        with st.spinner("Analyzing user feedback..."):

            url = "https://alka11.app.n8n.cloud/webhook/feedback-analysis"

            response = requests.post(
                url,
                json={"feedback": feedback}
            )

            # st.write(response.text)

            result = response.json()["result"]

            # 🔹 AI-level guardrail
            if "Invalid feedback" in result:
                st.error("Please enter valid product-related feedback.")
                st.stop()

            # ---------- SUCCESS ----------
            st.success("Analysis Complete")

            # ---------- METRICS ----------
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Issues", 4)

            with col2:
                st.metric("Critical Issues", 2)

            with col3:
                st.metric("Themes", 2)

            st.divider()

            # ---------- PARSE OUTPUT ----------
            sections = result.split("\n\n")

            def extract_items(section):
                lines = section.split("\n")
                items = []
                for line in lines:
                    if line.strip().startswith("-") or line.strip().startswith("1"):
                        items.append(line.replace("-", "").strip())
                return items

            top_problems = []
            themes = []
            critical = []
            actions = []

            for sec in sections:
                if "Top 3 Problems" in sec:
                    top_problems = extract_items(sec)
                elif "Key Themes" in sec:
                    themes = extract_items(sec)
                elif "Critical Issues" in sec:
                    critical = extract_items(sec)
                elif "What Should Be Built Next" in sec:
                    actions = extract_items(sec)

            # ---------- DASHBOARD ----------
            col_left, col_right = st.columns([2, 1])

            # LEFT SIDE
            with col_left:
                st.subheader("🔴 Top Problems")
                for problem in top_problems:
                    st.error(problem)

                st.subheader("📊 Key Themes")
                for theme in themes:
                    st.success(theme)

                st.subheader("💡 Recommended Actions")
                for action in actions:
                    st.info(action)

            # RIGHT SIDE
            with col_right:
                st.subheader("⚠️ Critical Issues")
                for issue in critical:
                    st.warning(issue)
