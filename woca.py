# German C1 TELC Flashcard App (v16 - Robust Click-to-Flip & Theme Filter)
# 독일어 C1 TELC 플래시카드 앱 (v16 - 안정적인 카드 클릭 전환 및 주제 필터 기능)

import streamlit as st
import pandas as pd
import random

# --- 1) 페이지 설정 & 기본 스타일 (CSS 일부 수정) ---
st.set_page_config(page_title="German Grammar Flashcard", page_icon="🇩🇪", layout="centered")

st.markdown("""
<style>
    /* 카드를 감싸는 컨테이너: 이 안에서 모든 위치 조정이 일어남 */
    .card-container {
        position: relative; /* 자식 요소(버튼)의 absolute 위치 기준점 */
        min-height: 290px;  /* 카드의 최소 높이와 일치시킴 */
    }

    /* 스트림릿 버튼을 투명 오버레이로 만드는 핵심 CSS */
    .card-container .stButton > button {
        position: absolute; /* 컨테이너를 기준으로 위치 고정 */
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: transparent;
        color: transparent;
        border: none;
        box-shadow: none;
        cursor: pointer;
        z-index: 10; /* 다른 요소들보다 위에 있도록 설정 */
    }

    .flashcard-front, .flashcard-back { 
        background: white; color: #333; border: 2px solid #007bff; border-radius: 15px; 
        padding: 30px 20px; margin-top: 15px; text-align: center; min-height: 250px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; 
    }
    .german-word { font-size: 2.8em; font-weight: bold; color: #2c3e50; }
    .korean-meaning { font-size: 2.2em; color: #e74c3c; margin: 20px 0; font-weight: bold; }
    .pos-badge { background: #007bff; color: white; padding: 8px 16px; border-radius: 20px; font-size: 1.1em; display: inline-block; margin-top: 15px; border: 1px solid #0056b3; }
    .example-box { background: #f8f9fa; border-left: 5px solid #007bff; border-radius: 8px; padding: 15px; margin: 20px 0; text-align: left; font-size: 1.1em; color: #333; }
    .front-example { font-size: 1.4em; color: #555; margin-top: 10px; font-style: italic; }
    .grammar-info { background: #e8f5e8; border: 1px solid #28a745; border-radius: 8px; padding: 15px; margin-top: 20px; text-align: left; color: #155724; }
    .grammar-title { font-weight: bold; color: #155724; margin-bottom: 10px; font-size: 1.2em; }
    .case-structure { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin: 10px 0; font-family: monospace; font-size: 1.1em; color: #856404; }
    .grammar-explanation { background: #e7f3ff; border-left: 4px solid #007bff; padding: 12px; margin: 10px 0; font-size: 1.0em; color: #004085; }
    .ko-example-translation { margin-top: 8px; color: #444; font-size: 1.05em; }
</style>
""", unsafe_allow_html=True)

# --- 2) 데이터 로딩 & 유틸 (기존과 동일) ---
@st.cache_data
def load_data(file_path_or_url):
    try:
        df = pd.read_csv(file_path_or_url, encoding='utf-8-sig', engine='python')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"데이터 파일을 불러오는 데 실패했습니다: {e}")
        st.info("GitHub에 올린 CSV 파일의 'Raw' 버튼을 누른 뒤, 그 주소를 복사해 코드에 붙여넣었는지 확인해주세요.")
        return None

def standardize_columns(df):
    cols_lower = [str(c).lower().strip() for c in df.columns]
    cand = {'german_word': ['german_word','german','word','item','deutsch','wort'],'korean_meaning': ['korean_meaning','korean','meaning','bedeutung','의미','뜻'],'german_example': ['german_example_de','german_example','example','beispiel','예문','예시'],'ko_example_translation': ['ko_example_translation','example_ko','예문_번역','예문해석','korean_example'],'pos': ['pos','part of speech','wortart','품사'],'verb_case': ['verb_case','kasus (verb)'],'verb_prep': ['verb_prep','präposition (verb)'],'reflexive': ['reflexive','reflexiv','재귀'],'complement_structure': ['complement_structure','struktur','문장 구조'],'theme': ['theme','type','category','thema','kategorie','테마','유형'],}
    mapping = {}
    for k, opts in cand.items():
        for o in opts:
            if o in cols_lower:
                mapping[k] = df.columns[cols_lower.index(o)]
                break
    for req in ['german_word','korean_meaning']:
        if req not in mapping:
            st.error(f"필수 컬럼이 없습니다: {req}"); return None, {}
    return df, mapping

def safe_get(row, key, mapping, default=""):
    if key in mapping and mapping[key] in row:
        v = row[mapping[key]]
        return str(v) if not pd.isna(v) and str(v).strip() != "" else default
    return default
# --- (문법 설명 함수들은 기존과 동일하여 생략) ---

# --- 3) 카드 UI 렌더 (st.markdown -> HTML 문자열 return으로 변경) ---
def display_question_card(row, mapping):
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    german_example = safe_get(row, 'german_example', mapping)
    # st.markdown 대신 HTML 문자열을 반환
    return f'<div class="flashcard-front"><div class="german-word">{german_word}</div><div class="front-example">{german_example}</div></div>'

def display_answer_card(row, mapping):
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    korean_meaning = safe_get(row, 'korean_meaning', mapping, '의미 없음')
    pos = safe_get(row, 'pos', mapping, '품사 미상')
    
    # 여러 정보를 모아 최종 HTML을 구성
    card_html = f'<div class="flashcard-back"><div class="german-word">{german_word}</div><div class="korean-meaning">{korean_meaning}</div><div class="pos-badge">{pos}</div></div>'
    
    german_example = safe_get(row, 'german_example', mapping)
    ko_example = safe_get(row, 'ko_example_translation', mapping)
    if german_example:
        trans_html = f"<div class='ko-example-translation'>🔹 번역: {ko_example}</div>" if ko_example else ""
        card_html += f'<div class="example-box"><strong>🔸 예문:</strong> {german_example}{trans_html}</div>'
    
    # (문법 정보 등 추가 정보 HTML 구성 로직도 여기에 포함시킬 수 있음)
    # 지금은 편의상 카드 뒷면의 핵심 정보만 포함
    
    return card_html


# --- 4) 세션 상태 초기화 (기존과 동일) ---
def initialize_session_state(df, mapping, selected_themes):
    theme_col = mapping.get('theme')
    if selected_themes and "전체 보기" not in selected_themes and theme_col:
        filtered_df = df[df[theme_col].isin(selected_themes)].copy()
    else:
        filtered_df = df.copy()

    st.session_state.filtered_df = filtered_df
    st.session_state.indices = list(filtered_df.index)
    random.shuffle(st.session_state.indices)
    st.session_state.current_idx_pos = 0
    st.session_state.show_answer = False
    st.session_state.data_loaded = True

# --- 5) 메인 로직 (핵심 변경!) ---
def main():
    st.title("🇩🇪 German Grammar Flashcard")
    st.markdown("흰색 카드 영역을 클릭하면 **정답 ↔ 문제**가 전환됩니다.")
    
    # ❗️ 중요: 이 URL을 자신의 GitHub Raw CSV 파일 주소로 변경하세요!
    DATA_URL = "https://raw.githubusercontent.com/Deplim/german_voca/main/c1_telc_voca.csv" 
    
    if 'full_df' not in st.session_state:
        full_df = load_data(DATA_URL)
        if full_df is None: st.stop()
        st.session_state.full_df, st.session_state.mapping = standardize_columns(full_df)

    if st.session_state.full_df is None: st.stop()
    full_df = st.session_state.full_df
    mapping = st.session_state.mapping
    
    # --- 사이드바 (기존과 동일) ---
    with st.sidebar:
        st.header("⚙️ 학습 설정")
        theme_col = mapping.get('theme')
        all_themes = sorted(list(full_df[theme_col].dropna().unique())) if theme_col else []

        selected_themes = ["전체 보기"]
        if all_themes:
            selected_themes = st.multiselect("학습할 주제를 선택하세요:", options=["전체 보기"] + all_themes, default=["전체 보기"])
            if not selected_themes: selected_themes = ["전체 보기"]
            if len(selected_themes) > 1 and "전체 보기" in selected_themes: selected_themes.remove("전체 보기")
        
        if 'last_filter' not in st.session_state or st.session_state.last_filter != selected_themes:
            initialize_session_state(full_df, mapping, selected_themes)
            st.session_state.last_filter = selected_themes

    if not st.session_state.data_loaded or st.session_state.filtered_df.empty:
        st.warning("선택한 주제에 해당하는 단어가 없습니다."); st.stop()
        
    filtered_df = st.session_state.filtered_df
    indices = st.session_state.indices
    pos = st.session_state.current_idx_pos
    current_row = filtered_df.loc[indices[pos]]
    total_words = len(filtered_df)

    st.info(f"💡 현재 학습 중인 주제: **{', '.join(selected_themes)}**")
    st.progress((pos + 1) / total_words)
    st.write(f"**진행률:** {pos + 1}/{total_words}")
    st.markdown("---")

    # --- 네비게이션 버튼 (기존과 동일) ---
    c1, c2, c3 = st.columns([1, 1, 1])
    if c1.button("⬅️ 이전", use_container_width=True):
        if pos > 0:
            st.session_state.current_idx_pos -= 1; st.session_state.show_answer = False; st.rerun()
    if c2.button("➡️ 다음", use_container_width=True):
        if pos < total_words - 1:
            st.session_state.current_idx_pos += 1; st.session_state.show_answer = False; st.rerun()
    if c3.button("🔀 섞기", use_container_width=True):
        initialize_session_state(full_df, mapping, selected_themes); st.rerun()

    # --- ✨ 새롭고 안정적인 카드 표시 및 클릭 로직 ---
    card_html_content = ""
    if st.session_state.show_answer:
        # 뒷면 카드 HTML 가져오기
        card_html_content = display_answer_card(current_row, mapping)
    else:
        # 앞면 카드 HTML 가져오기
        card_html_content = display_question_card(current_row, mapping)

    # 컨테이너와 투명 버튼으로 클릭 기능 구현
    with st.container():
        # 카드 컨테이너 시작
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # 실제 카드 내용(HTML) 그리기
        st.markdown(card_html_content, unsafe_allow_html=True)
        
        # 전체를 덮는 투명 버튼 (CSS가 알아서 위치를 잡아줌)
        if st.button(" ", key="card_flip_button"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()
            
        # 카드 컨테이너 끝
        st.markdown('</div>', unsafe_allow_html=True)


    # --- 사이드바 학습 현황 (기존과 동일) ---
    with st.sidebar:
        st.header("📊 학습 현황")
        st.metric("총 단어 수 (선택됨)", total_words)
        st.metric("현재 위치", pos + 1)
        st.metric("남은 단어", total_words - pos - 1)
        if 'pos' in mapping:
            st.write("**품사별 분포 (선택됨):**")
            st.bar_chart(filtered_df[mapping['pos']].value_counts())

if __name__ == "__main__":
    main()
