import streamlit as st
import pandas as pd
import random

# --- 1. 페이지 설정 및 스타일 ---
st.set_page_config(
    page_title="German Grammar Flashcard",
    page_icon="🇩🇪",
    layout="centered"
)

# CSS 스타일
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
    }
    .german-word { 
        font-size: 2.8em; 
        font-weight: bold; 
        color: #2c3e50; 
    }
    .korean-meaning { 
        font-size: 2.2em; 
        color: #e74c3c; 
        margin: 20px 0; 
        font-weight: bold; 
    }
    .pos-badge { 
        background: #007bff; 
        color: white; 
        padding: 8px 16px; 
        border-radius: 20px; 
        font-size: 1.1em; 
        display: inline-block; 
        margin-top: 15px; 
        border: 1px solid #0056b3; 
    }
    .example-box { 
        background: #f8f9fa; 
        border-left: 5px solid #007bff; 
        border-radius: 8px; 
        padding: 15px; 
        margin: 20px 0; 
        text-align: left; 
        font-size: 1.1em; 
        color: #333; 
    }
    .front-example { 
        font-size: 1.4em; 
        color: #555; 
        margin-top: 10px; 
        font-style: italic; 
    }
    .grammar-info { 
        background: #e8f5e8; 
        border: 1px solid #28a745; 
        border-radius: 8px; 
        padding: 15px; 
        margin-top: 20px; 
        text-align: left; 
        color: #155724; 
    }
    .grammar-title { 
        font-weight: bold; 
        color: #155724; 
        margin-bottom: 10px; 
        font-size: 1.2em; 
    }
    .case-structure { 
        background: #fff3cd; 
        border: 1px solid #ffeaa7; 
        border-radius: 8px; 
        padding: 12px; 
        margin: 10px 0; 
        font-family: monospace; 
        font-size: 1.1em; 
        color: #856404; 
    }
    .grammar-explanation { 
        background: #e7f3ff; 
        border-left: 4px solid #007bff; 
        padding: 12px; 
        margin: 10px 0; 
        font-size: 1.0em; 
        color: #004085; 
    }
</style>
""", unsafe_allow_html=True)


# --- 2. 핵심 함수들 ---

@st.cache_data
def load_data(file_path):
    """가장 안정적인 방법으로 CSV 파일을 로드합니다."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', engine='python')
        # CSV 로드 후 컬럼 이름의 앞뒤 공백을 모두 제거합니다.
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"데이터 파일 '{file_path}'을(를) 찾을 수 없습니다. GitHub 저장소에 파일이 올바르게 포함되었는지, 파일 이름이 정확한지 확인하세요.")
        return None
    except Exception as e:
        st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def standardize_columns(df):
    """다양한 CSV 열 이름을 표준화된 이름으로 매핑합니다."""
    columns_lower = [str(col).lower().strip() for col in df.columns]
    column_candidates = {
        'german_word': ['german_word', 'german', 'word', 'item', 'deutsch', 'wort'],
        'korean_meaning': ['korean_meaning', 'korean', 'meaning', 'bedeutung', '의미', '뜻'],
        'german_example': ['german_example_de', 'german_example', 'example', 'beispiel', '예문', '예시'],
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
    """Pandas의 isna를 사용하여 더 안정적으로 값을 가져옵니다."""
    if key in mapping and mapping[key] in row:
        value = row[mapping[key]]
        return str(value) if not pd.isna(value) and str(value).strip() != '' else default
    return default

def get_case_explanation(case_info):
    """격 정보에 따른 상세 설명을 반환합니다."""
    if not case_info:
        return ""
    
    case_lower = case_info.lower()
    explanations = []
    
    if 'nom' in case_lower:
        explanations.append("**1격 (Nominativ)**: 주어 역할")
    if 'akk' in case_lower:
        explanations.append("**4격 (Akkusativ)**: 직접목적어 (무엇을/누구를)")
    if 'dat' in case_lower:
        explanations.append("**3격 (Dativ)**: 간접목적어 (누구에게/무엇에게)")
    if 'gen' in case_lower:
        explanations.append("**2격 (Genitiv)**: 소유격 (~의)")
    
    return " | ".join(explanations)

def get_prep_explanation(prep_info):
    """전치사에 따른 상세 설명을 반환합니다."""
    if not prep_info:
        return ""
    
    prep_explanations = {
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
    
    prep_lower = prep_info.lower().strip()
    return prep_explanations.get(prep_lower, f"전치사: {prep_info}")

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
    """[뒷면] 정답 카드 표시 - 상세 문법 설명 포함"""
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
    
    # 예문 표시
    german_example = safe_get(row, 'german_example', mapping)
    if german_example:
        st.markdown(f"""
        <div class="example-box">
            <strong>🔸 예문:</strong> {german_example}
        </div>
        """, unsafe_allow_html=True)

    # 📚 상세 문법 정보 표시
    grammar_info = []
    
    # 동사인 경우의 상세 문법 분석
    if "verb" in pos.lower() or "Verb" in pos:
        # 재귀동사 확인
        reflexive = safe_get(row, 'reflexive', mapping)
        if reflexive.lower() in ['ja', 'yes', 'true']:
            grammar_info.append("🔄 **재귀동사 (Reflexives Verb)** - sich와 함께 사용")
        
        # complement_structure 우선 표시 (가장 중요!)
        complement_structure = safe_get(row, 'complement_structure', mapping)
        prep = safe_get(row, 'verb_prep', mapping)  
        case = safe_get(row, 'verb_case', mapping)
        
        if complement_structure:
            st.markdown(f"""
            <div class="case-structure">
                <strong>📝 문장 구조:</strong> <code>{complement_structure}</code>
            </div>
            """, unsafe_allow_html=True)
            
            # complement_structure에 대한 추가 설명
            structure_lower = complement_structure.lower()
            explanations = []
            if 'dat' in structure_lower and 'akk' in structure_lower:
                explanations.append("**3격 + 4격 지배**: 누구에게(3격) 무엇을(4격) 주는 동사")
            elif 'dat' in structure_lower:
                explanations.append("**3격 지배**: 누구에게/무엇에게를 나타내는 간접목적어")
            elif 'akk' in structure_lower:  
                explanations.append("**4격 지배**: 무엇을/누구를을 나타내는 직접목적어")
            elif 'gen' in structure_lower:
                explanations.append("**2격 지배**: 소유관계나 특별한 의미관계를 나타냄")
            
            if explanations:
                explanation_text = "<br/>".join(explanations)
                st.markdown(f"""
                <div class="grammar-explanation">
                    {explanation_text}
                </div>
                """, unsafe_allow_html=True)
        
        # 전치사 정보가 있는 경우
        if prep:
            prep_explanation = get_prep_explanation(prep)
            st.markdown(f"""
            <div class="grammar-explanation">
                <strong>🔗 전치사:</strong> <code>{prep}</code><br/>
                {prep_explanation}
            </div>
            """, unsafe_allow_html=True)
        
        # 격 정보만 있는 경우 (complement_structure가 없을 때)
        elif case and not complement_structure:
            case_explanation = get_case_explanation(case)
            if case_explanation:
                st.markdown(f"""
                <div class="grammar-explanation">
                    <strong>📋 격 지배:</strong> {case}<br/>
                    {case_explanation}
                </div>
                """, unsafe_allow_html=True)
    
    # 명사-동사 구조나 기타 품사의 경우
    elif "Nomen-Verb" in pos:
        complement_structure = safe_get(row, 'complement_structure', mapping)
        if complement_structure:
            st.markdown(f"""
            <div class="case-structure">
                <strong>📝 명사-동사 구조:</strong> <code>{complement_structure}</code>
            </div>
            """, unsafe_allow_html=True)
    
    # 테마 정보
    theme = safe_get(row, 'theme', mapping)
    if theme:
        grammar_info.append(f"🏷️ **테마**: {theme}")
        
    # 기타 문법 정보가 있는 경우 표시
    if grammar_info:
        info_html = "".join([f"<li>{info}</li>" for info in grammar_info])
        st.markdown(f"""
        <div class="grammar-info">
            <div class="grammar-title">📚 추가 정보</div>
            <ul>{info_html}</ul>
        </div>
        """, unsafe_allow_html=True)

# --- 3. 메인 앱 실행 로직 ---
def main():
    st.title("🇩🇪 German Grammar Flashcard")
    st.markdown("단어와 예문을 보고, 문법 구조까지 한번에 학습하세요!")
    
    # CSV 파일 로드
    df = load_data('c1_telc_voca.csv')

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
        
        # 버튼 컨트롤
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

        # 카드 표시
        if st.session_state.show_answer:
            display_answer_card(current_row, st.session_state.mapping)
        else:
            display_question_card(current_row, st.session_state.mapping)
        
        # 사이드바
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
