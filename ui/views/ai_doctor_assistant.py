"""
PulsePoint OS v6.0 — Interactive AI Health Doctor Chatbot (ChatGPT-Style Medical & Medicine Assistant)
Clean, zero-clutter conversational chatbot interface where users type their disease/symptoms
in Hindi, Hinglish, or English and receive instant Sahi Ilaz, Medicine tables, and Diet plans.
Per-user isolated chat history + Anti-XSS WAF protection.
"""

import re
import streamlit as st
import pandas as pd
from core.security import sanitize_user_input, check_rate_limit


MEDICAL_KNOWLEDGE = {
    "heart_bp": {
        "title": "❤️ High Blood Pressure (Hypertension) & Heart Care",
        "keywords": ["heart", "bp", "blood pressure", "chest", "seene", "dard", "angina", "palpitation", "dhakkan", "hypertension", "cardiac", "attack", "high bp"],
        "summary": (
            "Aapke lakshan **High Blood Pressure (Hypertension) ya Cardiac Stress** ki taraf ishara kar rahe hain. "
            "Jab BP 140/90 mmHg se upar rehta hai ya seene me bharipan hota hai, toh dil ki naso (coronary arteries) par dabav badhta hai."
        ),
        "medicines": [
            {"Medicine (Generic Salt)": "Telmisartan 40mg / Amlodipine 5mg", "Kaam (Purpose)": "BP ko 24 ghante control me rakhne ke liye", "Kab Lein (Timing)": "Subah nashta ke baad 1 goli", "Savdhani (Precaution)": "Bina doctor se puche achanak band na karein"},
            {"Medicine (Generic Salt)": "Atorvastatin 10mg / Rosuvastatin 10mg", "Kaam (Purpose)": "Naso me cholesterol/plaque jamne se rokne ke liye", "Kab Lein (Timing)": "Raat ko khane ke baad 1 goli", "Savdhani (Precaution)": "Liver test (LFT) 6 mahine me check karayein"},
            {"Medicine (Generic Salt)": "Low-Dose Aspirin (Ecosprin 75mg)", "Kaam (Purpose)": "Khoon ko patla rakhne ke liye (Sirf Doctor ki salah par)", "Kab Lein (Timing)": "Dopahar khane ke baad", "Savdhani (Precaution)": "Khali pet bilkul na lein (acidity ho sakti hai)"},
            {"Medicine (Generic Salt)": "Metoprolol Succinate 25mg", "Kaam (Purpose)": "Dil ki dhadkan aur BP shant rakhne ke liye", "Kab Lein (Timing)": "Subah 1 baar", "Savdhani (Precaution)": "Asthma wale mareez doctor se puch kar lein"}
        ],
        "sahi_ilaz": [
            "🥗 **DASH Diet Apnayein:** Namak (Salt) din bhar me 1 choti chammach (< 4g) se kam lein. Papad, achar, chips aur packaged food band karein.",
            "🚶 **Rozana 30 Min Walk:** Subah ya shaam normal speed me 30 minute paidal chalein.",
            "🧄 **Home Supportive Care:** Subah 1 kali lahsun (garlic), lauki ka soup, nariyal pani aur hari sabziyan lein.",
            "🚭 **Smoking & Alcohol Band:** Tobacco aur alcohol BP aur heart attack ka risk 2x badhate hain."
        ],
        "tests": "12-Lead ECG, 2D Echo, Lipid Profile (Cholesterol), Kidney Function Test (KFT)",
        "emergency": "🚨 Agar seene ke beech me bhari dard बाएं haath/jabde me jaye aur thanda paseena aaye, toh turant **Sorbitrate 5mg** zubaan ke neeche rakhein aur Hospital Emergency jayein!"
    },
    "diabetes_sugar": {
        "title": "🩸 Diabetes (Madhumeh / High Blood Sugar) Care",
        "keywords": ["sugar", "diabetes", "madhumeh", "glucose", "hba1c", "insulin", "pyaas", "peshab", "thakan", "meetha", "diabetic"],
        "summary": (
            "Aapki problem **Blood Sugar (Type-2 Diabetes / Pre-Diabetes)** se judi hai. "
            "Jab Fasting Sugar 126 mg/dL se upar ya HbA1c 6.5% se zyada hota hai, toh khoon me glucose badhne lagta hai."
        ),
        "medicines": [
            {"Medicine (Generic Salt)": "Metformin SR 500mg", "Kaam (Purpose)": "First-line सुरक्षित sugar control dawa (Insulin sensitivity badhati hai)", "Kab Lein (Timing)": "Subah-Shaam khane ke turant baad", "Savdhani (Precaution)": "Khali pet na lein"},
            {"Medicine (Generic Salt)": "Dapagliflozin 10mg / Empagliflozin 10mg", "Kaam (Purpose)": "Extra sugar ko urine ke raste bahar nikalti hai aur Heart/Kidney bachati hai", "Kab Lein (Timing)": "Subah nashta ke baad 1 goli", "Savdhani (Precaution)": "Din bhar me 8-10 glass pani zaroor piyein"},
            {"Medicine (Generic Salt)": "Glimepiride 1mg / Sitagliptin 50mg", "Kaam (Purpose)": "Khane ke baad badhne wali sugar (PP) ko rokne ke liye", "Kab Lein (Timing)": "Nashte se 15 min pehle (Doctor salah se)", "Savdhani (Precaution)": "Dawa lene ke baad khana skip na karein"},
            {"Medicine (Generic Salt)": "Methylcobalamin (Vitamin B12) 1500mcg", "Kaam (Purpose)": "Haath-pairo ki jhanjhanahat aur kamzori dur karne ke liye", "Kab Lein (Timing)": "Dopahar khane ke baad", "Savdhani (Precaution)": "Sugar ke mareezo ke liye safe nerve vitamin"}
        ],
        "sahi_ilaz": [
            "🍽️ **Plate Method Diet:** Aadhi plate hari sabzi/salad, 1/4 plate dal/paneer/protein, aur sirf 1/4 plate multigrain roti rakhein.",
            "🚫 **Kya Band Karein:** Cheeni, gud, colddrink, maida, safed chawal, aam, chikoo, aur aloo.",
            "🌿 **Desi Support:** Raat ko 1 chammach Methi dana (Fenugreek) bhigo kar subah uska pani piyein; Jamun aur Karela faydemand hai.",
            "🚶 **Khane ke baad 15 Min Walk:** Lunch aur Dinner ke baad 15 minute tehelne se PP sugar 30-40 points kam hoti hai."
        ],
        "tests": "HbA1c (3-month average sugar), Fasting & PP Blood Sugar, Urine Microalbumin, Vitamin B12",
        "emergency": "🚨 Agar achanak chakkar aaye, kapkapi ho, ya paseena aaye (Low Sugar < 70 mg/dL), toh turant 3 chammach Glucose ya cheeni pani piyein!"
    },
    "stroke_neuro": {
        "title": "🧠 Brain Stroke Risk, Vertigo (Chakkar) & Migraine Care",
        "keywords": ["stroke", "paralysis", "lakwa", "chakkar", "dizziness", "vertigo", "headache", "sar dard", "migraine", "numbness", "sunn", "brain"],
        "summary": (
            "Aapke lakshan **Chakkar (Vertigo), Migraine ya Brain Blood Flow (Neuro-Vascular)** se jude hain. "
            "Agar BP high rehta hai aur chakkar ya haath-pair sunn hote hain, toh iski turant jaanch zaroori hai."
        ),
        "medicines": [
            {"Medicine (Generic Salt)": "Betahistine 16mg (Vertin) / Cinnarizine 25mg", "Kaam (Purpose)": "Chakkar (Vertigo) aur sar ghumna rokne ke liye", "Kab Lein (Timing)": "Subah-Shaam khane ke baad", "Savdhani (Precaution)": "Halki neend aa sakti hai, driving na karein"},
            {"Medicine (Generic Salt)": "Naproxen 250mg / Paracetamol 650mg", "Kaam (Purpose)": "Tez sar dard ya Migraine ke liye", "Kab Lein (Timing)": "Khane ke baad jab dard ho", "Savdhani (Precaution)": "Khali pet painkiller na lein"},
            {"Medicine (Generic Salt)": "Clopidogrel 75mg + Atorvastatin 20mg", "Kaam (Purpose)": "Brain stroke / blood clot se bachav (Sirf Neurologist ki salah par)", "Kab Lein (Timing)": "Raat ko khane ke baad", "Savdhani (Precaution)": "BP hamesha < 130/80 mmHg rakhein"}
        ],
        "sahi_ilaz": [
            "💧 **Hydration & Salt Control:** Pani barabar piyein aur achanak bistar se jhatke se na uthein (pehle 30 second baithein).",
            "😴 **7-8 Ghante ki Neend:** Neend ki kami aur mobile screen zyada dekhne se vertigo aur migraine badhta hai.",
            "🩺 **BP aur Sugar Check:** Jab bhi chakkar aaye, sabse pehle BP aur Blood Sugar check karein."
        ],
        "tests": "BP Monitoring, Carotid Doppler Ultrasound, Brain MRI/CT (if numbness), Vitamin D & B12",
        "emergency": "🚨 **BE-FAST Rule:** Agar chehra tedha ho, ek haath uthne me kamzori ho, ya aawaz ladkhadaye — toh bina 1 minute gawaye CT Scan wale Hospital jayein!"
    },
    "cholesterol_lipid": {
        "title": "🧬 High Cholesterol, Triglycerides & Fatty Liver Care",
        "keywords": ["cholesterol", "lipid", "triglyceride", "ldl", "hdl", "fatty liver", "obesity", "motapa", "weight", "vajan"],
        "summary": (
            "Aapki problem **High Cholesterol (Dyslipidemia) / Fatty Liver / Weight Management** se judi hai. "
            "Bad Cholesterol (LDL > 130 mg/dL) ya Triglycerides (> 150 mg/dL) naso me rukaawat paida karte hain."
        ),
        "medicines": [
            {"Medicine (Generic Salt)": "Rosuvastatin 10mg / Atorvastatin 10mg", "Kaam (Purpose)": "LDL (Bad Cholesterol) ko 40% tak kam karne ke liye", "Kab Lein (Timing)": "Raat ko sote samay 1 goli", "Savdhani (Precaution)": "Doctor ki salah se shuru karein"},
            {"Medicine (Generic Salt)": "Omega-3 Fatty Acid (EPA + DHA) 1000mg", "Kaam (Purpose)": "Triglycerides kam karne aur Good Cholesterol (HDL) badhane ke liye", "Kab Lein (Timing)": "Dopahar khane ke baad", "Savdhani (Precaution)": "Safe nutritional supplement"},
            {"Medicine (Generic Salt)": "Saroglitazar 4mg / Ursodeoxycholic Acid 300mg", "Kaam (Purpose)": "Diabetic High Triglycerides aur Fatty Liver ke liye (Prescription only)", "Kab Lein (Timing)": "Doctor ke nirdesh anusar", "Savdhani (Precaution)": "Alcohol aur तला-भुना bilkul band karein"}
        ],
        "sahi_ilaz": [
            "🥣 **Oats, Walnuts & Flaxseeds:** Subah Oats ka daliya, 4 Akhrot (Walnuts) aur 1 chammach Alsi (Flaxseed) powder lein.",
            "🚫 **Zero Trans-Fat:** Samosa, kachori, Dalda, butter, malai aur fast food band karein.",
            "🏃 **Brisk Walk & Weight Loss:** 5% vajan kam karne se Fatty Liver aur Triglycerides 30% tak suhar jate hain."
        ],
        "tests": "Fasting Lipid Profile (Total, LDL, HDL, Triglycerides), Liver Function Test (LFT), Ultrasound Abdomen",
        "emergency": "🚨 Agar दाहिनी pasli ke neeche lagatar dard ho ya aankhon me peela-pan (Jaundice) dikhe, toh Doctor ko dikhayein."
    },
    "general_fever_stomach": {
        "title": "🤒 General Health: Fever (Bukhar), Cough, Acidity & Weakness Care",
        "keywords": ["fever", "bukhar", "cough", "khansi", "cold", "zukam", "acidity", "gas", "pet", "stomach", "thyroid", "weakness", "kamzori", "body pain", "dard"],
        "summary": (
            "Aapne **Bukhar, Khansi, Acidity ya Kamzori (General Primary Care)** ke lakshan bataye hain. "
            "Mausami infection, viral fever ya gastric problem me niche di gayi standard medicines aur parhez kaam aate hain."
        ),
        "medicines": [
            {"Medicine (Generic Salt)": "Paracetamol 650mg (Dolo 650 / Calpol)", "Kaam (Purpose)": "Bukhar (Fever) aur Badan Dard ke liye sabse safe dawa", "Kab Lein (Timing)": "Khane ke baad (6 ghante ke gap par zaroorat padne par)", "Savdhani (Precaution)": "24 ghante me 3-4 goli se zyada na lein"},
            {"Medicine (Generic Salt)": "Pantoprazole 40mg (Pan-40) / Antacid Gel", "Kaam (Purpose)": "Gas, Acidity aur seene ki jalan ke liye", "Kab Lein (Timing)": "Subah khali pet nashte se 30 min pehle", "Savdhani (Precaution)": "Teekha aur masala khana band karein"},
            {"Medicine (Generic Salt)": "Cetirizine 10mg / Steam Inhalation", "Kaam (Purpose)": "Sardi-Zukam, chheenk aur gale ki kharash ke liye", "Kab Lein (Timing)": "Raat ko sote samay 1 goli", "Savdhani (Precaution)": "Gungune pani me namak daal kar garare (gargle) karein"},
            {"Medicine (Generic Salt)": "ORS Solution + Multivitamin + Zinc (Zinconia)", "Kaam (Purpose)": "Kamzori, Dehydration aur Immunity ke liye", "Kab Lein (Timing)": "Din bhar ORS piyein, 1 Zinc goli dopahar me", "Savdhani (Precaution)": "Halka khana (Khichdi, Daliya, Soup) lein"}
        ],
        "sahi_ilaz": [
            "🥣 **Halka Khana:** Moong dal khichdi, daliya, nariyal pani, ORS aur gunguna pani piyein.",
            "🌡️ **Temperature Note Karein:** Har 6 ghante me thermometer se bukhar check karein.",
            "🛌 **Pura Aaram (Rest):** Kam se kam 7-8 ghante aaram karein aur thanda pani/colddrink bilkul na lein."
        ],
        "tests": "CBC (Complete Blood Count), Widal / Dengue NS1 (agar bukhar 3 din se zyada rahe), TSH (Thyroid ke liye)",
        "emergency": "🚨 Agar bukhar 102°F se upar rahe, 3 din me kam na ho, ya saans lene me takleef ho, toh turant Doctor ko dikhayein!"
    }
}


def generate_ai_doctor_reply(user_message: str) -> dict:
    """
    Analyzes the user's natural language query (Hindi, Hinglish, or English)
    and returns a structured medical response with condition summary, medicine table, Sahi Ilaz, and tests.
    """
    q_lower = user_message.lower()

    # Check if user mentioned specific numbers (e.g. BP 160/100 or Sugar 240)
    bp_match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", q_lower)
    vital_note = ""
    if bp_match:
        sbp, dbp = int(bp_match.group(1)), int(bp_match.group(2))
        if sbp >= 140 or dbp >= 90:
            vital_note = f"⚠️ **Aapka BP ({sbp}/{dbp} mmHg) High hai** (Normal < 120/80 mmHg hota hai). "
        else:
            vital_note = f"✅ **Aapka BP ({sbp}/{dbp} mmHg) Normal range me hai.** "

    # Match categories based on keywords
    matched_keys = []
    for key, info in MEDICAL_KNOWLEDGE.items():
        if any(kw in q_lower for kw in info["keywords"]):
            matched_keys.append(key)

    if not matched_keys:
        # Default helpful matching if user wrote a general query
        if bp_match:
            matched_keys = ["heart_bp"]
        else:
            matched_keys = ["general_fever_stomach"]

    primary = MEDICAL_KNOWLEDGE[matched_keys[0]]

    # Combine medicines if user asked about multiple conditions (e.g., both BP and Sugar)
    combined_meds = list(primary["medicines"])
    combined_ilaz = list(primary["sahi_ilaz"])
    titles = [primary["title"]]

    for extra_key in matched_keys[1:2]:
        extra = MEDICAL_KNOWLEDGE[extra_key]
        titles.append(extra["title"])
        combined_meds.extend(extra["medicines"][:2])
        combined_ilaz.extend(extra["sahi_ilaz"][:2])

    return {
        "title": " + ".join(titles),
        "summary": vital_note + primary["summary"],
        "medicines": combined_meds,
        "sahi_ilaz": combined_ilaz,
        "tests": primary["tests"],
        "emergency": primary["emergency"]
    }


def render(df: pd.DataFrame = None):
    from core.rasp_shield import BackendIsolationGuard, AntiTamperRaspEngine, AntiLLMTrapEngine
    from core.audit import log_audit_event

    user = st.session_state.get("user", {})
    username = user.get("username", "guest")
    role = user.get("role", "Guest")
    tenant_ns = BackendIsolationGuard.isolate_tenant_namespace(username)
    chat_key = f"ai_chat_history_{tenant_ns}"

    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {
                "role": "assistant",
                "type": "welcome",
                "content": (
                    "🙏 **Namaste! Main PulsePoint AI Health Doctor hoon.**\n\n"
                    "Aap niche **Chat Box** me apni koi bhi **Bimari, Lakshan (Symptoms)** ya **BP/Sugar Report** "
                    "seedha Hindi, Hinglish ya English me type karein — main aapko turant **Sahi Ilaz, Medicines Table aur Diet Plan** bataunga!\n\n"
                    f"🛡️ *Protected by Zero-Trust Backend Isolation (`{tenant_ns}`), RASP Runtime Shield & Anti-LLM Canary Trap.*"
                )
            }
        ]

    # Clean, Minimal Header (No wall of theory!)
    col_title, col_clear = st.columns([8.5, 1.5])
    with col_title:
        st.markdown("### 🤖 AI Health Doctor Chatbot (Bimari, Sahi Ilaz & Medicine Guide)")
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear_ai_chat"):
            st.session_state[chat_key] = [st.session_state[chat_key][0]]
            st.rerun()

    # 4 Simple 1-Click Quick Question Buttons
    st.caption("👇 **Quick Example Questions (Click karein ya niche Chat Box me khud type karein):**")
    q1, q2, q3, q4 = st.columns(4)
    quick_prompt = None
    with q1:
        if st.button("❤️ High BP & Seene me Dard", use_container_width=True, key="qp_bp"):
            quick_prompt = "Mera BP 155/95 rehta hai aur kabhi-kabhi seene me bharipan lagta hai. Sahi medicine aur ilaz batayein."
    with q2:
        if st.button("🩸 High Sugar / Diabetes", use_container_width=True, key="qp_sugar"):
            quick_prompt = "Mera fasting blood sugar 185 hai aur thakan rehti hai. Diabetes ki sahi medicine aur diet plan kya hai?"
    with q3:
        if st.button("🧠 Chakkar / Migraine / Stroke", use_container_width=True, key="qp_stroke"):
            quick_prompt = "Mujhe subah uthte waqt chakkar (vertigo) aur tez sar dard hota hai. Konsi dawa aur savdhani zaroori hai?"
    with q4:
        if st.button("🤒 Bukhar, Khansi & Acidity", use_container_width=True, key="qp_fever"):
            quick_prompt = "Mujhe 2 din se bukhar, khansi aur pet me gas/acidity ho rahi hai. Sahi medicine aur parhez batayein."

    st.markdown("<hr style='border-color: rgba(0,242,254,0.18); margin: 8px 0 12px 0;'/>", unsafe_allow_html=True)

    # Render Chat Conversation History
    for msg in st.session_state[chat_key]:
        with st.chat_message(msg["role"], avatar="🩺" if msg["role"] == "assistant" else "🧑"):
            if msg.get("type") in ("welcome", "anti_llm_trap") or msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                res = msg["data"]
                st.markdown(f"#### {res['title']}")
                st.markdown(res["summary"])

                st.markdown("##### 💊 Standard Clinical Medicines & Dosage Guide")
                st.dataframe(pd.DataFrame(res["medicines"]), use_container_width=True, hide_index=True)

                st.markdown("##### 🥗 Sahi Ilaz, Diet & Daily Recovery Plan")
                for item in res["sahi_ilaz"]:
                    st.markdown(f"- {item}")

                st.markdown(f"🧪 **Recommended Lab Tests:** `{res['tests']}`")
                st.warning(res["emergency"])
                st.caption("⚕️ *Clinical Note: Koi bhi prescription medicine shuru karne se pehle apne Doctor se confirm zaroor karein.*")

    # Bottom Chatbot Input Box (Just like ChatGPT / WhatsApp!)
    typed_prompt = st.chat_input(
        "💬 Yahan apni bimari ya symptoms type karein (e.g., 'Mujhe high BP aur sugar hai konsi medicine lu?')..."
    )

    active_input = quick_prompt or typed_prompt
    if active_input:
        allowed, _ = check_rate_limit(f"ai_chat_{username}", max_requests=25, window_seconds=60)
        if not allowed:
            st.error("🛡️ Please wait a few seconds before sending more messages.")
            return

        # 1. Anti-LLM Prompt Injection & Jailbreak Honeypot Trap Check
        trap_result = AntiLLMTrapEngine.inspect_and_trap_llm_attack(active_input, username)
        if trap_result.get("trapped"):
            canary_token = trap_result["canary_honeytoken"]
            log_audit_event(
                username=username,
                role=role,
                event_type="ANTI_LLM_TRAP_TRIGGERED",
                resource="ai_doctor_chatbot",
                status="HONEYPOT_TRAPPED",
                details={"canary_honeytoken": canary_token, "attack_type": trap_result["attack_type"]}
            )
            st.session_state[chat_key].append({
                "role": "user",
                "type": "text",
                "content": "[BLOCKED PROMPT INJECTION ATTEMPT]"
            })
            st.session_state[chat_key].append({
                "role": "assistant",
                "type": "anti_llm_trap",
                "content": trap_result["decoy_message"]
            })
            st.rerun()

        # 2. RASP & WAF Sanitization Check
        clean_input, is_safe, threat_msg = sanitize_user_input(active_input)
        if not is_safe:
            log_audit_event(
                username=username,
                role=role,
                event_type="RASP_RUNTIME_BLOCK",
                resource="ai_doctor_chatbot",
                status="BLOCKED",
                details={"reason": threat_msg}
            )
            st.error(f"🛡️ RASP & WAF Security Firewall Blocked Input: {threat_msg}")
            return

        # Append user message
        st.session_state[chat_key].append({
            "role": "user",
            "type": "text",
            "content": clean_input
        })

        # Generate AI Doctor response
        reply_data = generate_ai_doctor_reply(clean_input)
        st.session_state[chat_key].append({
            "role": "assistant",
            "type": "structured_medical",
            "data": reply_data
        })

        # Cap chat history at 20 messages per user so memory never grows unbounded
        if len(st.session_state[chat_key]) > 21:
            st.session_state[chat_key] = [st.session_state[chat_key][0]] + st.session_state[chat_key][-20:]

        st.rerun()
