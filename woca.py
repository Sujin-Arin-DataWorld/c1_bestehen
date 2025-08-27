# German C1 TELC Flashcard App (v16 - 렌더링 오류 수정 버전)
# 독일어 C1 TELC 준비용 플래시카드 앱 (v16 - Rendering Bug Fix)

import streamlit as st
import pandas as pd
import random

# --- 1. 페이지 설정 및 스타일 ---
st.set_page_config(
    page_title="German Grammar Flashcard",
    page_icon="🇩🇪",
    layout="centered"
)

# CSS 스타일 (변경 없음)
st.markdown("""
<style>
    /* 카드 기본 스타일 */
    .flashcard-container {
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
    }
    .german-word { font-size: 2.8em; font-weight: bold; color: #2c3e50; }
    .korean-meaning { font-size: 2.2em; color: #e74c3c; margin: 20px 0; font-weight: bold; }
    .pos-badge { background: #007bff; color: white; padding: 8px 16px; border-radius: 20px; font-size: 1.1em; display: inline-block; margin-top: 15px; border: 1px solid #0056b3; }
    .example-box { background: #f8f9fa; border-left: 5px solid #007bff; border-radius: 8px; padding: 15px; margin: 20px 0; text-align: left; font-size: 1.1em; color: #333; line-height: 1.6; }
    .front-example { font-size: 1.4em; color: #555; margin-top: 10px; font-style: italic; }
    .grammar-info { background: #e8f5e8; border: 1px solid #28a745; border-radius: 8px; padding: 15px; margin-top: 20px; text-align: left; color: #155724; }
    .grammar-title { font-weight: bold; color: #155724; margin-bottom: 10px; font-size: 1.2em; }
    .case-structure { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin: 10px 0; font-family: monospace; font-size: 1.1em; color: #856404; text-align: left; }
    .grammar-explanation { background: #e7f3ff; border-left: 4px solid #007bff; padding: 12px; margin: 10px 0; font-size: 1.0em; color: #004085; text-align: left; }
</style>
""", unsafe_allow_html=True)


# --- 2. 핵심 함수들 (generate_card_html 제외하고 변경 없음) ---

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', engine='python')
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"데이터 파일 '{file_path}'을(를) 찾을 수 없습니다. 파일 이름과 위치를 확인하세요.")
        return None
    except Exception as e:
        st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def standardize_columns(df):
    columns_lower = [str(col).lower().strip() for col in df.columns]
    column_candidates = {
        'german_word': ['german_word', 'german', 'word', 'item', 'deutsch', 'wort'],
        'korean_meaning': ['korean_meaning', 'korean', 'meaning', 'bedeutung', '의미', '뜻'],
        'german_example': ['german_example_de', 'german_example', 'example', 'beispiel', '예문', '예시'],
        'ko_example_translation': ['ko_example_translation', 'korean_example_translation', 'example_ko', '예문번역', '예문해석'],
        'pos': ['pos', 'part of speech', 'wortart', '품사'],
        'verb_case': ['verb_case', 'kasus (verb)'],
        'verb_prep': ['verb_prep', 'präposition (verb)'],
        'reflexive': ['reflexive', 'reflexiv', '재귀'],
        'complement_structure': ['complement_structure', 'struktur', '문장 구조'],
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
        return str(value) if not pd.isna(value) and str(value).strip() != '' else default
    return default

def get_case_explanation(case_info):
    if not case_info: return ""
    case_lower = case_info.lower()
    explanations = []
    if 'nom' in case_lower: explanations.append("**1격 (Nominativ)**: 주어 역할")
    if 'akk' in case_lower: explanations.append("**4격 (Akkusativ)**: 직접목적어 (무엇을/누구를)")
    if 'dat' in case_lower: explanations.append("**3격 (Dativ)**: 간접목적어 (누구에게/무엇에게)")
    if 'gen' in case_lower: explanations.append("**2격 (Genitiv)**: 소유격 (~의)")
    return " | ".join(explanations)

def get_prep_explanation(prep_info):
    if not prep_info: return ""
    prep_explanations = {
        'an': "접촉/위치 (3격: ~에서/~에게, 4격: ~로/~를 향해)", 'auf': "표면 위 (3격: ~위에서, 4격: ~위로)",
        'bei': "근처/옆 (3격만: ~근처에서/~와 함께)", 'für': "위해/~동안 (4격만: ~을/를 위해)",
        'gegen': "반대/~쪽으로 (4격만: ~에 반대하여/~쪽으로)", 'in': "안/속 (3격: ~안에서, 4격: ~안으로)",
        'mit': "함께/수단 (3격만: ~와 함께/~로써)", 'nach': "방향/시간 후 (3격만: ~후에/~로)",
        'über': "위/관하여 (3격: ~위에서, 4격: ~위로/~에 관하여)", 'um': "주위/시간 (4격만: ~주위에/~시에)",
        'unter': "아래/사이 (3격: ~아래에서, 4격: ~아래로)", 'von': "~로부터/~에 의해 (3격만: ~로부터/~의)",
        'vor': "앞/시간 전 (3격: ~앞에서/~전에, 4격: ~앞으로)", 'zu': "~에게/~로 (3격만: ~에게/~로)"
    }
    return prep_explanations.get(prep_info.lower().strip(), f"전치사: {prep_info}")

def generate_card_html(row, mapping, is_answer_side):
    # 이 함수는 이전 버전과 동일하게 유지됩니다.
    if not is_answer_side:
        german_word = safe_get(row, 'german_word', mapping, '단어 없음')
        german_example = safe_get(row, 'german_example', mapping)
        return f"""<div class="flashcard-container">
                       <div class="german-word">{german_word}</div>
                       <div class="front-example">{german_example}</div>
                   </div>"""
    else:
        inner_html_parts = []
        german_word = safe_get(row, 'german_word', mapping, '단어 없음')
        korean_meaning = safe_get(row, 'korean_meaning', mapping, '의미 없음')
        pos = safe_get(row, 'pos', mapping, '품사 미상')
        inner_html_parts.append(f"""<div class="german-word">{german_word}</div>
                                    <div class="korean-meaning">{korean_meaning}</div>
                                    <div class="pos-badge">{pos}</div>""")
        german_example = safe_get(row, 'german_example', mapping)
        ko_example_translation = safe_get(row, 'ko_example_translation', mapping)
        if german_example:
            translation_html = f"<br/><strong>➡️ 번역:</strong> {ko_example_translation}" if ko_example_translation else ""
            inner_html_parts.append(f"""<div class="example-box">
                                          <strong>🔸 예문:</strong> {german_example}
                                          {translation_html}
                                      </div>""")
        grammar_info_list = []
        if "verb" in pos.lower() or "Verb" in pos:
            if safe_get(row, 'reflexive', mapping).lower() in ['ja', 'yes', 'true']:
                grammar_info_list.append("🔄 **재귀동사 (Reflexives Verb)** - sich와 함께 사용")
            complement_structure = safe_get(row, 'complement_structure', mapping)
            prep = safe_get(row, 'verb_prep', mapping)
            case = safe_get(row, 'verb_case', mapping)
            if complement_structure:
                inner_html_parts.append(f'<div class="case-structure"><strong>📝 문장 구조:</strong> <code>{complement_structure}</code></div>')
                structure_lower = complement_structure.lower()
                explanations = []
                if 'dat' in structure_lower and 'akk' in structure_lower: explanations.append("**3격 + 4격 지배**: 누구에게(3격) 무엇을(4격) 주는 동사")
                elif 'dat' in structure_lower: explanations.append("**3격 지배**: 누구에게/무엇에게를 나타내는 간접목적어")
                elif 'akk' in structure_lower: explanations.append("**4격 지배**: 무엇을/누구를을 나타내는 직접목적어")
                elif 'gen' in structure_lower: explanations.append("**2격 지배**: 소유관계나 특별한 의미관계를 나타냄")
                if explanations: inner_html_parts.append(f'<div class="grammar-explanation">{"<br/>".join(explanations)}</div>')
            if prep:
                inner_html_parts.append(f'<div class="grammar-explanation"><strong>🔗 전치사:</strong> <code>{prep}</code><br/>{get_prep_explanation(prep)}</div>')
            elif case and not complement_structure and get_case_explanation(case):
                inner_html_parts.append(f'<div class="grammar-explanation"><strong>📋 격 지배:</strong> {case}<br/>{get_case_explanation(case)}</div>')
        elif "Nomen-Verb" in pos:
            complement_structure = safe_get(row, 'complement_structure', mapping)
            if complement_structure: inner_html_parts.append(f'<div class="case-structure"><strong>📝 명사-동사 구조:</strong> <code>{complement_structure}</code></div>')
        theme = safe_get(row, 'theme', mapping)
        if theme: grammar_info_list.append(f"🏷️ **테마**: {theme}")
        if grammar_info_list:
            info_html = "".join([f"<li>{info}</li>" for info in grammar_info_list])
            inner_html_parts.append(f'<div class="grammar-info"><div class="grammar-title">📚 추가 정보</div><ul>{info_html}</ul></div>')
        inner_content = "".join(inner_html_parts)
        return f'<div class="flashcard-container">{inner_content}</div>'

# --- 3. 메인 앱 실행 로직 (❗️핵심 수정 부분) ---
def main():
    st.title("🇩🇪 German Grammar Flashcard")
    st.markdown("단어와 예문을 보고, 문법 구조까지 한번에 학습하세요!")
    
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
    
    if st.session_state.get('data_loaded', False):
        indices = st.session_state.indices
        current_idx_pos = st.session_state.current_idx_pos
        current_row = st.session_state.df.iloc[indices[current_idx_pos]]

        st.progress((current_idx_pos + 1) / len(df))
        st.write(f"**진행률:** {current_idx_pos + 1}/{len(df)}")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ 이전", use_container_width=True):
                if current_idx_pos > 0:
                    st.session_state.current_idx_pos -= 1
                    st.session_state.show_answer = False # 답변 상태 초기화
                    st.rerun()
        with col2:
            if st.button("➡️ 다음", use_container_width=True):
                if current_idx_pos < len(df) - 1:
                    st.session_state.current_idx_pos += 1
                    st.session_state.show_answer = False # 답변 상태 초기화
                    st.rerun()
        with col3:
            if st.button("🔀 섞기", use_container_width=True):
                random.shuffle(st.session_state.indices)
                st.session_state.current_idx_pos = 0
                st.session_state.show_answer = False # 답변 상태 초기화
                st.rerun()

        # ❗️수정: st.markdown으로 카드 디자인을 올바르게 표시
        card_html = generate_card_html(current_row, st.session_state.mapping, st.session_state.show_answer)
        st.markdown(card_html, unsafe_allow_html=True)

        # ❗️수정: st.toggle을 사용하여 정답 보기/숨기기 기능 구현
        # st.toggle은 현재 상태(True/False)를 직접 반환합니다.
        st.session_state.show_answer = st.toggle(
            "💡 정답 보기", 
            value=st.session_state.show_answer, # 현재 상태를 토글에 반영
            key=f"flipper_{current_idx_pos}"
        )
        
        # 사이드바 (변경 없음)
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
