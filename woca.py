# German C1 TELC Flashcard App (v6 - UI Layout Update)
# 독일어 C1 TELC 준비용 플래시카드 앱 (v6 - UI 레이아웃 업데이트)

import streamlit as st
import pandas as pd
import random

# --- 1. 페이지 설정 및 스타일 ---
st.set_page_config(
    page_title="German Grammar Flashcard",
    page_icon="🇩🇪",
    layout="centered"
)

# CSS 스타일 (이전과 동일)
st.markdown("""
<style>
    /* ... 이전과 동일한 CSS 코드 ... */
    .flashcard-front, .flashcard-back { background: white; color: #333; border: 2px solid #007bff; border-radius: 15px; padding: 30px 20px; margin-top: 15px; text-align: center; min-height: 250px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; }
    .german-word { font-size: 2.8em; font-weight: bold; color: #2c3e50; }
    .korean-meaning { font-size: 2.2em; color: #e74c3c; margin: 20px 0; font-weight: bold; }
    .pos-badge { background: #007bff; color: white; padding: 8px 16px; border-radius: 20px; font-size: 1.1em; display: inline-block; margin-top: 15px; border: 1px solid #0056b3; }
    .example-box { background: #f8f9fa; border-left: 5px solid #007bff; border-radius: 8px; padding: 15px; margin: 20px 0; text-align: left; font-size: 1.1em; color: #333; }
    .front-example { font-size: 1.4em; color: #555; margin-top: 10px; font-style: italic; }
    .grammar-info { background: #e8f5e8; border: 1px solid #28a745; border-radius: 8px; padding: 15px; margin-top: 20px; text-align: left; color: #155724; }
    .grammar-title { font-weight: bold; color: #155724; margin-bottom: 10px; font-size: 1.2em; }
</style>
""", unsafe_allow_html=True)


# --- 2. 핵심 함수들 (수정 없음) ---

@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"데이터 파일({file_path})을 찾을 수 없습니다. GitHub 저장소에 파일이 올바르게 포함되었는지 확인하세요.")
        return None

def standardize_columns(df):
    columns_lower = [str(col).lower().strip() for col in df.columns]
    column_candidates = {
        'german_word': ['german_word', 'german', 'word', 'item', 'deutsch', 'wort'],
        'korean_meaning': ['korean_meaning', 'korean', 'meaning', 'bedeutung', '의미', '뜻'],
        'german_example': ['german_example_de', 'german_example', 'example', 'beispiel', '예문', '예시'],
        'ko_example_translation': ['ko_example_translation', 'korean_example', '예문 번역', '번역'],
        'pos': ['pos', 'part of speech', 'wortart', '품사'],
        'verb_case': ['verb_case', 'kasus (verb)'],
        'verb_prep': ['verb_prep', 'präposition (verb)'],
        'reflexive': ['reflexive', 'reflexiv', '재귀'],
        'adj_case': ['adj_case', 'kasus (adj)'],
        'adj_prep': ['adj_prep', 'präposition (adj)'],
        'theme': ['theme', 'type', 'category', 'thema', 'kategorie', '테마', '유형']
    }
    found_mapping = {}
    for standard_name, candidates in column_candidates.items():
        for candidate in candidates:
            if candidate in columns_lower:
                original_col_name = df.columns[columns_lower.index(candidate)]
                found_mapping[standard_name] = original_col_name
                break
    required = ['german_word', 'korean_meaning']
    missing = [col for col in required if col not in found_mapping]
    if missing:
        st.error(f"필수 컬럼을 찾을 수 없습니다: {', '.join(missing)}")
        return None, {}
    return df, found_mapping

def safe_get(row, key, mapping, default=""):
    if key in mapping and mapping[key] in row:
        value = row[mapping[key]]
        return str(value) if pd.notna(value) else default
    return default

def display_question_card(row, mapping):
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    german_example = safe_get(row, 'german_example', mapping)
    st.markdown(f"""
    <div class="flashcard-front">
        <div class="german-word">{german_word}</div>
        <div class="front-example">{german_example}</div>
    </div>
    """, unsafe_allow_html=True)

def display_answer_card(row, mapping):
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    korean_meaning = safe_get(row, 'korean_meaning', mapping, '의미 없음')
    pos = safe_get(row, 'pos', mapping, '품사 미상')
    st.markdown(f"""
    <div class="flashcard-back">
        <div class="german-word">{german_word}</div>
        <div class="korean-meaning">{korean_meaning}</div>
        <div class="pos-badge">{pos}</div>
    </div>
    """, unsafe_allow_html=True)
    
    german_example = safe_get(row, 'german_example', mapping)
    ko_example = safe_get(row, 'ko_example_translation', mapping)
    if german_example:
        st.markdown(f"""
        <div class="example-box">
            <strong>🔸 예문:</strong> {german_example}<br>
            <strong>🔸 번역:</strong> {ko_example if ko_example else '번역 없음'}
        </div>
        """, unsafe_allow_html=True)
    
    grammar_info = []
    if "Verb" in pos:
        reflexive = safe_get(row, 'reflexive', mapping)
        if reflexive.lower() in ['ja', 'yes', 'true']:
            grammar_info.append("🔄 **재귀 동사 (Reflexives Verb)**")
        
        prep = safe_get(row, 'verb_prep', mapping)
        case = safe_get(row, 'verb_case', mapping)
        
        structure_displayed = False
        
        if prep:
            structure_displayed = True
            if case and case.lower() in prep.lower():
                grammar_info.append(f"구조: `{prep}`")
            elif case:
                grammar_info.append(f"구조: `{prep}` + **{case}**")
            else:
                grammar_info.append(f"구조: `{prep}`")
        
        if not structure_displayed and case:
            case_lower = case.lower()
            if 'dat' in case_lower and 'akk' in case_lower:
                grammar_info.append("구조: **jmdm. (Dat) + etw. (Akk)**")
            elif 'gen' in case_lower:
                grammar_info.append("구조: **einer Sache (Gen)**")
            elif 'akk' in case_lower:
                grammar_info.append("구조: **jmdn./etw. (Akk)**")
            elif 'dat' in case_lower:
                grammar_info.append("구조: **jmdm./etw. (Dat)**")
            else:
                grammar_info.append(f"구조: **{case}-Ergänzung**")

    elif "Adjektiv" in pos:
        prep = safe_get(row, 'adj_prep', mapping)
        case = safe_get(row, 'adj_case', mapping)
        if prep:
            if case and case.lower() in prep.lower():
                grammar_info.append(f"구조: `{prep}`")
            elif case:
                grammar_info.append(f"구조: `{prep}` + **{case}**")
            else:
                grammar_info.append(f"구조: `{prep}`")
            
    theme = safe_get(row, 'theme', mapping)
    if theme:
        grammar_info.append(f"테마: {theme}")
        
    if grammar_info:
        info_html = "".join([f"<li>{info}</li>" for info in grammar_info])
        st.markdown(f"""
        <div class="grammar-info">
            <div class="grammar-title">📚 문법 및 추가 정보</div>
            <ul>{info_html}</ul>
        </div>
        """, unsafe_allow_html=True)

# --- 3. 메인 앱 실행 로직 ---
def main():
    st.title("🇩🇪 German Grammar Flashcard")
    st.markdown("단어와 예문을 보고, 문법 구조까지 한번에 학습하세요!")
    
    df = load_data('C1_telc_Vocab_Example_20_entries.csv')

    if df is None:
        st.stop()

    if 'data_loaded' not in st.session_state:
        st.session_state.df, st.session_state.mapping = standardize_columns(df)
        if st.session_state.df is not None:
            st.session_state.indices = list(range(len(st.session_state.df)))
            random.shuffle(st.session_state.indices)
            st.session_state.current_idx_pos = 0
            st.session_state.show_answer = False
            st.session_state.data_loaded = True
    
    if st.session_state.data_loaded:
        indices = st.session_state.indices
        current_idx_pos = st.session_state.current_idx_pos
        current_word_index = indices[current_idx_pos]
        current_row = st.session_state.df.iloc[current_word_index]

        st.progress((current_idx_pos + 1) / len(df))
        st.write(f"**진행률:** {current_idx_pos + 1}/{len(df)}")
        st.markdown("---")

        # ✨✨✨ 핵심 수정 부분 ✨✨✨
        # 버튼 생성 코드를 카드 표시 코드 위로 이동시켰습니다.
        
        # --- 4. 네비게이션 버튼 (위치 변경) ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⬅️ 이전"):
                if current_idx_pos > 0:
                    st.session_state.current_idx_pos -= 1
                    st.session_state.show_answer = False
                    st.rerun()
        
        with col2:
            button_text = "🔄 문제로" if st.session_state.show_answer else "💡 정답 보기"
            if st.button(button_text, use_container_width=True):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()

        with col3:
            if st.button("➡️ 다음"):
                if current_idx_pos < len(df) - 1:
                    st.session_state.current_idx_pos += 1
                    st.session_state.show_answer = False
                    st.rerun()
        
        with col4:
            if st.button("🔀 섞기"):
                random.shuffle(st.session_state.indices)
                st.session_state.current_idx_pos = 0
                st.session_state.show_answer = False
                st.rerun()

        # --- 5. 플래시카드 표시 ---
        if st.session_state.show_answer:
            display_answer_card(current_row, st.session_state.mapping)
        else:
            display_question_card(current_row, st.session_state.mapping)
        
        # 사이드바 (수정 없음)
        with st.sidebar:
            st.header("📊 학습 현황")
            st.metric("총 단어 수", len(df))
            st.metric("현재 위치", current_idx_pos + 1)
            st.metric("남은 단어", len(df) - current_idx_pos - 1)
            
            if 'pos' in st.session_state.mapping:
                pos_col = st.session_state.mapping['pos']
                st.write("**품사별 분포:**")
                st.bar_chart(df[pos_col].value_counts())

if __name__ == "__main__":
    main()
