# German C1 TELC Flashcard App (v14.2 - Keep UI, Flip only on white area)
# 기존 UI 유지 + ko_example_translation 표시 + 흰색 카드 영역 클릭 시에만 뒤집기

import streamlit as st
import pandas as pd
import random

# --- 1) 페이지 설정 & 기본 스타일(원본 유지, 번역 라인 추가) ---
st.set_page_config(page_title="German Grammar Flashcard", page_icon="🇩🇪", layout="centered")

st.markdown("""
<style>
    .flashcard-front, .flashcard-back { 
        background: white; 
        color: #333; 
        border: 2px solid #007bff; 
        border-radius: 15px; 
        padding: 30px 20px; 
        margin-top: 15px; 
        text-align: center; 
        min-height: 250px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        position: relative; /* 오버레이 정렬 기준 */
    }
    .german-word { font-size: 2.8em; font-weight: bold; color: #2c3e50; }
    .korean-meaning { font-size: 2.2em; color: #e74c3c; margin: 20px 0; font-weight: bold; }
    .pos-badge { 
        background: #007bff; color: white; padding: 8px 16px; border-radius: 20px; 
        font-size: 1.1em; display: inline-block; margin-top: 15px; border: 1px solid #0056b3; 
    }
    .example-box { 
        background: #f8f9fa; border-left: 5px solid #007bff; border-radius: 8px; 
        padding: 15px; margin: 20px 0; text-align: left; font-size: 1.1em; color: #333; 
    }
    .front-example { font-size: 1.4em; color: #555; margin-top: 10px; font-style: italic; }
    .grammar-info { background: #e8f5e8; border: 1px solid #28a745; border-radius: 8px; padding: 15px; margin-top: 20px; text-align: left; color: #155724; }
    .grammar-title { font-weight: bold; color: #155724; margin-bottom: 10px; font-size: 1.2em; }
    .case-structure { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin: 10px 0; font-family: monospace; font-size: 1.1em; color: #856404; }
    .grammar-explanation { background: #e7f3ff; border-left: 4px solid #007bff; padding: 12px; margin: 10px 0; font-size: 1.0em; color: #004085; }
    .ko-example-translation { margin-top: 6px; color: #444; }

    /* ===== 오버레이 버튼: 카드 흰색 영역과 정확히 겹치기 ===== */
    .flip-overlay {
        position: absolute; 
        inset: 0;               /* 상하좌우 0 → 부모(.flashcard-*) 흰 영역과 동일 */
        z-index: 5;
        border-radius: 15px;    /* 카드와 동일한 라운드 */
        /* 버튼과 비슷한 포커스 테두리 제거 */
        outline: none;
    }
    .flip-overlay > button {
        width: 100%; height: 100%;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: transparent !important;       /* 텍스트 안 보이게 */
        cursor: pointer;
        padding: 0 !important; margin: 0 !important;
    }
    .flip-overlay > button:focus { outline: none !important; }
</style>
""", unsafe_allow_html=True)


# --- 2) 유틸 함수들 ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', engine='python')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"데이터 파일 '{file_path}'을(를) 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def standardize_columns(df):
    cols_lower = [str(c).lower().strip() for c in df.columns]
    cand = {
        'german_word': ['german_word','german','word','item','deutsch','wort'],
        'korean_meaning': ['korean_meaning','korean','meaning','bedeutung','의미','뜻'],
        'german_example': ['german_example_de','german_example','example','beispiel','예문','예시'],
        'ko_example_translation': ['ko_example_translation','example_ko','예문_번역','예문해석','korean_example'],
        'pos': ['pos','part of speech','wortart','품사'],
        'verb_case': ['verb_case','kasus (verb)'],
        'verb_prep': ['verb_prep','präposition (verb)'],
        'reflexive': ['reflexive','reflexiv','재귀'],
        'complement_structure': ['complement_structure','struktur','문장 구조'],
        'theme': ['theme','type','category','thema','kategorie','테마','유형'],
    }
    mapping = {}
    for k, opts in cand.items():
        for o in opts:
            if o in cols_lower:
                mapping[k] = df.columns[cols_lower.index(o)]
                break
    for req in ['german_word','korean_meaning']:
        if req not in mapping:
            st.error(f"필수 컬럼이 없습니다: {req}")
            return None, {}
    return df, mapping

def safe_get(row, key, mapping, default=""):
    if key in mapping and mapping[key] in row:
        v = row[mapping[key]]
        return str(v) if not pd.isna(v) and str(v).strip() != "" else default
    return default

def get_case_explanation(case_info):
    if not case_info: return ""
    cl = case_info.lower()
    s = []
    if 'nom' in cl: s.append("**1격 (Nominativ)**: 주어 역할")
    if 'akk' in cl: s.append("**4격 (Akkusativ)**: 직접목적어 (무엇을/누구를)")
    if 'dat' in cl: s.append("**3격 (Dativ)**: 간접목적어 (누구에게/무엇에게)")
    if 'gen' in cl: s.append("**2격 (Genitiv)**: 소유격 (~의)")
    return " | ".join(s)

def get_prep_explanation(prep_info):
    if not prep_info: return ""
    m = {
        'an': "접촉/위치 (3격: ~에서/~에게, 4격: ~로/~를 향해)",
        'auf': "표면 위 (3격: ~위에서, 4격: ~위로)",
        'bei': "근처/옆 (3격만: ~근처에서/~와 함께)",
        'für': "위해/~동안 (4격만: ~을/를 위해)",
        'gegen': "반대/~쪽으로 (4격만: ~에 반대하여/~쪽으로)",
        'in': "안/속 (3격: ~안에서, 4격: ~안으로)",
        'mit': "함께/수단 (3격만: ~와 함께/~로써)",
        'nach': "방향/시간 후 (3격만: ~후에/~로)",
        'über': "위/관하여 (3격: ~위에서, 4격: ~위로/~에 관하여)",
        'um': "주위/시간 (4격만: ~주위에/~시에)",
        'unter': "아래/사이 (3격: ~아래에서, 4격: ~아래로)",
        'von': "~로부터/~에 의해 (3격만: ~로부터/~의)",
        'vor': "앞/시간 전 (3격: ~앞에서/~전에, 4격: ~앞으로)",
        'zu': "~에게/~로 (3격만: ~에게/~로)"
    }
    return m.get(prep_info.lower().strip(), f"전치사: {prep_info}")


# --- 3) 카드 그리기 (UI 그대로) + 오버레이 영역 클릭 토글 ---
def draw_question_card(row, mapping):
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    german_example = safe_get(row, 'german_example', mapping)
    st.markdown(f"""
    <div class="flashcard-front">
        <div class="german-word">{german_word}</div>
        <div class="front-example">{german_example}</div>
        <div class="flip-overlay" id="front-overlay"></div>
    </div>
    """, unsafe_allow_html=True)
    # 오버레이 버튼(흰색 영역과 정확히 동일)
    return st.button(" ", key="flip_front", help="카드를 클릭해서 정답 보기", args=None)

def draw_answer_card(row, mapping):
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    korean_meaning = safe_get(row, 'korean_meaning', mapping, '의미 없음')
    pos = safe_get(row, 'pos', mapping, '품사 미상')

    st.markdown(f"""
    <div class="flashcard-back">
        <div class="german-word">{german_word}</div>
        <div class="korean-meaning">{korean_meaning}</div>
        <div class="pos-badge">{pos}</div>
        <div class="flip-overlay" id="back-overlay"></div>
    </div>
    """, unsafe_allow_html=True)

    german_example = safe_get(row, 'german_example', mapping)
    ko_example = safe_get(row, 'ko_example_translation', mapping)
    if german_example:
        trans_html = f"<div class='ko-example-translation'>🔹 번역: {ko_example}</div>" if ko_example else ""
        st.markdown(f"""
        <div class="example-box">
            <strong>🔸 예문:</strong> {german_example}
            {trans_html}
        </div>
        """, unsafe_allow_html=True)

    # 문법 정보(기존 유지)
    grammar_info = []
    if "verb" in pos.lower() or "Verb" in pos:
        reflexive = safe_get(row, 'reflexive', mapping)
        if reflexive.lower() in ['ja','yes','true']:
            grammar_info.append("🔄 **재귀동사 (Reflexives Verb)** - sich와 함께 사용")

        complement_structure = safe_get(row, 'complement_structure', mapping)
        prep = safe_get(row, 'verb_prep', mapping)
        case = safe_get(row, 'verb_case', mapping)

        if complement_structure:
            st.markdown(f"""
            <div class="case-structure"><strong>📝 문장 구조:</strong> <code>{complement_structure}</code></div>
            """, unsafe_allow_html=True)
            sl = complement_structure.lower()
            exps = []
            if 'dat' in sl and 'akk' in sl: exps.append("**3격 + 4격 지배**: 누구에게(3격) 무엇을(4격) 주는 동사")
            elif 'dat' in sl: exps.append("**3격 지배**: 누구에게/무엇에게(간접목적)")
            elif 'akk' in sl: exps.append("**4격 지배**: 무엇을/누구를(직접목적)")
            elif 'gen' in sl: exps.append("**2격 지배**: 소유/특별 의미관계")
            if exps:
                st.markdown(f"""<div class="grammar-explanation">{'<br/>'.join(exps)}</div>""", unsafe_allow_html=True)

        if prep:
            st.markdown(f"""
            <div class="grammar-explanation"><strong>🔗 전치사:</strong> <code>{prep}</code><br/>{get_prep_explanation(prep)}</div>
            """, unsafe_allow_html=True)
        elif case and not complement_structure:
            ce = get_case_explanation(case)
            if ce:
                st.markdown(f"""<div class="grammar-explanation"><strong>📋 격 지배:</strong> {case}<br/>{ce}</div>""", unsafe_allow_html=True)

    elif "Nomen-Verb" in pos:
        cs = safe_get(row, 'complement_structure', mapping)
        if cs:
            st.markdown(f"""<div class="case-structure"><strong>📝 명사-동사 구조:</strong> <code>{cs}</code></div>""", unsafe_allow_html=True)

    theme = safe_get(row, 'theme', mapping)
    if theme:
        grammar_info.append(f"🏷️ **테마**: {theme}")
    if grammar_info:
        st.markdown(f"""<div class="grammar-info"><div class="grammar-title">📚 추가 정보</div><ul>{"".join([f"<li>{i}</li>" for i in grammar_info])}</ul></div>""", unsafe_allow_html=True)

    # 오버레이 버튼(흰색 영역과 정확히 동일)
    return st.button(" ", key="flip_back", help="카드를 클릭해서 문제로", args=None)


# --- 4) 메인 ---
def main():
    st.title("🇩🇪 German Grammar Flashcard")
    st.markdown("흰색 카드 영역을 클릭하면 **정답 ↔ 문제**가 전환됩니다.")

    df = load_data('c1_telc_voca.csv')
    if df is None: st.stop()

    if 'data_loaded' not in st.session_state:
        st.session_state.df, st.session_state.mapping = standardize_columns(df)
        if st.session_state.df is not None:
            st.session_state.indices = list(range(len(st.session_state.df)))
            random.shuffle(st.session_state.indices)
            st.session_state.current_idx_pos = 0
            st.session_state.show_answer = False
            st.session_state.data_loaded = True

    if not st.session_state.data_loaded: st.stop()

    idxs = st.session_state.indices
    pos = st.session_state.current_idx_pos
    row = st.session_state.df.iloc[idxs[pos]]

    st.progress((pos + 1) / len(df))
    st.write(f"**진행률:** {pos + 1}/{len(df)}")
    st.markdown("---")

    # 네비게이션 (원래 UI 유지)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⬅️ 이전"):
            if pos > 0:
                st.session_state.current_idx_pos -= 1
                st.session_state.show_answer = False
                st.rerun()
    with c2:
        if st.button("🔄 문제/정답 전환", use_container_width=True):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()
    with c3:
        if st.button("➡️ 다음"):
            if pos < len(df) - 1:
                st.session_state.current_idx_pos += 1
                st.session_state.show_answer = False
                st.rerun()
    with c4:
        if st.button("🔀 섞기"):
            random.shuffle(st.session_state.indices)
            st.session_state.current_idx_pos = 0
            st.session_state.show_answer = False
            st.rerun()

    # 카드 + 오버레이(카드 내부에 겹침)
    if st.session_state.show_answer:
        if draw_answer_card(row, st.session_state.mapping):   # 오버레이 버튼
            st.session_state.show_answer = False
            st.rerun()
    else:
        if draw_question_card(row, st.session_state.mapping): # 오버레이 버튼
            st.session_state.show_answer = True
            st.rerun()

    # 사이드바
    with st.sidebar:
        st.header("📊 학습 현황")
        st.metric("총 단어 수", len(df))
        st.metric("현재 위치", pos + 1)
        st.metric("남은 단어", len(df) - pos - 1)
        if 'pos' in st.session_state.mapping:
            st.write("**품사별 분포:**")
            st.bar_chart(df[st.session_state.mapping['pos']].value_counts())

if __name__ == "__main__":
    main()
