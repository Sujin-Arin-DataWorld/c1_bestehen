# German C1 TELC Flashcard App (v15.0 - 개선된 버전)
# - 정확한 카드 크기 오버레이로 뒤집기 구현
# - 카테고리/테마별 학습 기능 추가
# - UI/UX 개선 및 성능 최적화

import streamlit as st
import pandas as pd
import random
from typing import Dict, List, Optional, Tuple

# --- 1) 페이지 설정 & 개선된 스타일 ---
st.set_page_config(
    page_title="German Grammar Flashcard", 
    page_icon="🇩🇪", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# 개선된 CSS 스타일
st.markdown("""
<style>
    /* 메인 컨테이너 스타일링 */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* 카드 컨테이너 - 정확한 크기 지정 */
    .card-container {
        position: relative;
        width: 100%;
        height: 350px;
        margin: 20px auto;
        perspective: 1000px;
    }
    
    /* 카드 기본 스타일 */
    .flashcard-front, .flashcard-back { 
        background: white; 
        color: #333; 
        border: 3px solid #007bff; 
        border-radius: 20px; 
        padding: 30px 25px; 
        text-align: center; 
        width: 100%;
        height: 350px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15); 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        position: absolute;
        top: 0;
        left: 0;
        transition: all 0.3s ease;
        cursor: pointer;
        box-sizing: border-box;
    }
    
    /* 카드 호버 효과 */
    .flashcard-front:hover, .flashcard-back:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.2);
        border-color: #0056b3;
    }
    
    /* 투명 오버레이 - 카드와 정확히 동일한 크기 */
    .click-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 350px;
        background: transparent;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        z-index: 10;
        opacity: 0;
    }
    
    .click-overlay:hover {
        background: rgba(0, 123, 255, 0.05);
        opacity: 1;
    }
    
    /* 텍스트 스타일링 */
    .german-word { 
        font-size: 3.2em; 
        font-weight: bold; 
        color: #2c3e50;
        margin-bottom: 15px;
        line-height: 1.2;
    }
    
    .korean-meaning { 
        font-size: 2.4em; 
        color: #e74c3c; 
        margin: 15px 0; 
        font-weight: bold;
        line-height: 1.3;
    }
    
    .pos-badge { 
        background: linear-gradient(45deg, #007bff, #0056b3); 
        color: white; 
        padding: 10px 20px; 
        border-radius: 25px; 
        font-size: 1.2em; 
        display: inline-block; 
        margin: 15px auto; 
        box-shadow: 0 2px 8px rgba(0,123,255,0.3);
        font-weight: 600;
    }
    
    .front-example { 
        font-size: 1.5em; 
        color: #666; 
        margin-top: 15px; 
        font-style: italic;
        line-height: 1.4;
    }
    
    /* 예문 박스 개선 */
    .example-box { 
        background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
        border-left: 6px solid #007bff; 
        border-radius: 12px; 
        padding: 20px; 
        margin: 20px 0; 
        text-align: left; 
        font-size: 1.2em; 
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .ko-example-translation { 
        margin-top: 10px; 
        color: #555;
        font-size: 1.1em;
        font-style: normal;
        padding: 8px 12px;
        background: rgba(0,123,255,0.08);
        border-radius: 8px;
        border-left: 3px solid #007bff;
    }
    
    /* 문법 정보 박스 개선 */
    .grammar-info { 
        background: linear-gradient(135deg, #e8f5e8, #d4edda); 
        border: 2px solid #28a745; 
        border-radius: 12px; 
        padding: 20px; 
        margin-top: 25px; 
        text-align: left; 
        color: #155724;
        box-shadow: 0 2px 8px rgba(40,167,69,0.15);
    }
    
    .grammar-title { 
        font-weight: bold; 
        color: #155724; 
        margin-bottom: 15px; 
        font-size: 1.3em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .case-structure { 
        background: linear-gradient(135deg, #fff3cd, #ffeaa7); 
        border: 2px solid #ffc107; 
        border-radius: 10px; 
        padding: 15px; 
        margin: 12px 0; 
        font-family: 'Courier New', monospace; 
        font-size: 1.2em; 
        color: #856404;
        font-weight: 600;
    }
    
    .grammar-explanation { 
        background: linear-gradient(135deg, #e7f3ff, #cce7ff); 
        border-left: 5px solid #007bff; 
        border-radius: 8px;
        padding: 15px; 
        margin: 12px 0; 
        font-size: 1.1em; 
        color: #004085;
        line-height: 1.5;
    }
    
    /* 필터 컨테이너 스타일 */
    .filter-container {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #dee2e6;
    }
    
    /* 진행 상황 개선 */
    .progress-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        padding: 15px 20px;
        border-radius: 10px;
        margin: 15px 0;
        font-weight: 600;
        color: #1565c0;
    }
    
    /* 버튼 스타일 개선 */
    .stButton > button {
        border-radius: 10px !important;
        border: 2px solid #007bff !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,123,255,0.3) !important;
    }
    
    /* 사이드바 개선 */
    .sidebar .metric-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 2) 데이터 처리 함수들 (최적화) ---
@st.cache_data
def load_data(file_path: str) -> Optional[pd.DataFrame]:
    """CSV 파일을 로드하고 기본 전처리를 수행합니다."""
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', engine='python')
        df.columns = df.columns.str.strip()
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        # 기본 데이터 정리
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', '')
        
        return df
    except FileNotFoundError:
        st.error(f"❌ 데이터 파일 '{file_path}'을(를) 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"❌ CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def standardize_columns(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Dict[str, str]]:
    """컬럼명을 표준화하고 매핑을 생성합니다."""
    cols_lower = [str(c).lower().strip() for c in df.columns]
    
    # 컬럼 매핑 후보들
    column_candidates = {
        'german_word': ['german_word', 'german', 'word', 'item', 'deutsch', 'wort'],
        'korean_meaning': ['korean_meaning', 'korean', 'meaning', 'bedeutung', '의미', '뜻'],
        'german_example': ['german_example_de', 'german_example', 'example', 'beispiel', '예문', '예시'],
        'ko_example_translation': ['ko_example_translation', 'example_ko', '예문_번역', '예문해석', 'korean_example'],
        'pos': ['pos', 'part of speech', 'wortart', '품사'],
        'verb_case': ['verb_case', 'kasus (verb)', 'case'],
        'verb_prep': ['verb_prep', 'präposition (verb)', 'preposition'],
        'reflexive': ['reflexive', 'reflexiv', '재귀'],
        'complement_structure': ['complement_structure', 'struktur', '문장 구조', 'structure'],
        'theme': ['theme', 'type', 'category', 'thema', 'kategorie', '테마', '유형'],
    }
    
    mapping = {}
    for standard_name, candidates in column_candidates.items():
        for candidate in candidates:
            if candidate in cols_lower:
                original_col = df.columns[cols_lower.index(candidate)]
                mapping[standard_name] = original_col
                break
    
    # 필수 컬럼 확인
    required_columns = ['german_word', 'korean_meaning']
    for required in required_columns:
        if required not in mapping:
            st.error(f"❌ 필수 컬럼이 없습니다: {required}")
            return None, {}
    
    return df, mapping

def safe_get(row: pd.Series, key: str, mapping: Dict[str, str], default: str = "") -> str:
    """안전하게 행에서 값을 가져옵니다."""
    if key in mapping and mapping[key] in row:
        value = row[mapping[key]]
        if pd.isna(value) or str(value).strip() in ['', 'nan', 'None']:
            return default
        return str(value).strip()
    return default

def get_unique_values(df: pd.DataFrame, mapping: Dict[str, str], key: str) -> List[str]:
    """특정 컬럼의 고유값들을 반환합니다."""
    if key not in mapping:
        return []
    
    values = df[mapping[key]].dropna().astype(str).str.strip()
    values = values[values != ''].unique().tolist()
    return sorted([v for v in values if v not in ['nan', 'None', '']])

# --- 3) 문법 설명 함수들 (개선) ---
def get_case_explanation(case_info: str) -> str:
    """격 정보에 대한 설명을 반환합니다."""
    if not case_info:
        return ""
    
    case_lower = case_info.lower()
    explanations = []
    
    case_map = {
        'nom': "**1격 (Nominativ)**: 주어 역할 - 누가/무엇이",
        'akk': "**4격 (Akkusativ)**: 직접목적어 - 무엇을/누구를", 
        'dat': "**3격 (Dativ)**: 간접목적어 - 누구에게/무엇에게",
        'gen': "**2격 (Genitiv)**: 소유격 - ~의"
    }
    
    for case_key, explanation in case_map.items():
        if case_key in case_lower:
            explanations.append(explanation)
    
    return " | ".join(explanations)

def get_prep_explanation(prep_info: str) -> str:
    """전치사에 대한 상세 설명을 반환합니다."""
    if not prep_info:
        return ""
    
    prep_map = {
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
    
    prep_clean = prep_info.lower().strip()
    return prep_map.get(prep_clean, f"전치사: {prep_info}")

# --- 4) 카드 렌더링 함수들 (개선) ---
def render_question_card(row: pd.Series, mapping: Dict[str, str]) -> None:
    """문제 카드를 렌더링합니다."""
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    german_example = safe_get(row, 'german_example', mapping)
    
    st.markdown(f"""
    <div class="card-container">
        <div class="flashcard-front">
            <div class="german-word">{german_word}</div>
            {f'<div class="front-example">"{german_example}"</div>' if german_example else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_answer_card(row: pd.Series, mapping: Dict[str, str]) -> None:
    """정답 카드를 렌더링합니다."""
    german_word = safe_get(row, 'german_word', mapping, '단어 없음')
    korean_meaning = safe_get(row, 'korean_meaning', mapping, '의미 없음')
    pos = safe_get(row, 'pos', mapping, '품사 미상')
    
    st.markdown(f"""
    <div class="card-container">
        <div class="flashcard-back">
            <div class="german-word">{german_word}</div>
            <div class="korean-meaning">{korean_meaning}</div>
            <div class="pos-badge">{pos}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 예문 표시
    german_example = safe_get(row, 'german_example', mapping)
    ko_example = safe_get(row, 'ko_example_translation', mapping)
    
    if german_example:
        translation_html = ""
        if ko_example:
            translation_html = f'<div class="ko-example-translation">🔹 번역: {ko_example}</div>'
        
        st.markdown(f"""
        <div class="example-box">
            <strong>🔸 예문:</strong> {german_example}
            {translation_html}
        </div>
        """, unsafe_allow_html=True)
    
    # 문법 정보 렌더링
    render_grammar_info(row, mapping, pos)

def render_grammar_info(row: pd.Series, mapping: Dict[str, str], pos: str) -> None:
    """문법 정보를 렌더링합니다."""
    grammar_sections = []
    
    # 동사 관련 정보
    if "verb" in pos.lower():
        # 재귀동사 체크
        reflexive = safe_get(row, 'reflexive', mapping)
        if reflexive.lower() in ['ja', 'yes', 'true', '1']:
            grammar_sections.append("🔄 **재귀동사 (Reflexives Verb)** - sich와 함께 사용")
        
        # 문장 구조
        complement_structure = safe_get(row, 'complement_structure', mapping)
        if complement_structure:
            st.markdown(f"""
            <div class="case-structure">
                <strong>📝 문장 구조:</strong> <code>{complement_structure}</code>
            </div>
            """, unsafe_allow_html=True)
            
            # 격 지배 설명
            structure_lower = complement_structure.lower()
            explanations = []
            
            if 'dat' in structure_lower and 'akk' in structure_lower:
                explanations.append("**3격 + 4격 지배**: 누구에게(3격) 무엇을(4격) 주는 동사")
            elif 'dat' in structure_lower:
                explanations.append("**3격 지배**: 간접목적어를 요구하는 동사")
            elif 'akk' in structure_lower:
                explanations.append("**4격 지배**: 직접목적어를 요구하는 동사")
            elif 'gen' in structure_lower:
                explanations.append("**2격 지배**: 소유관계나 특별한 의미관계를 나타내는 동사")
            
            if explanations:
                st.markdown(f"""
                <div class="grammar-explanation">
                    {' | '.join(explanations)}
                </div>
                """, unsafe_allow_html=True)
        
        # 전치사 정보
        prep = safe_get(row, 'verb_prep', mapping)
        if prep:
            prep_explanation = get_prep_explanation(prep)
            st.markdown(f"""
            <div class="grammar-explanation">
                <strong>🔗 전치사:</strong> <code>{prep}</code><br/>
                {prep_explanation}
            </div>
            """, unsafe_allow_html=True)
        elif not complement_structure:
            # 격 정보만 있는 경우
            case = safe_get(row, 'verb_case', mapping)
            if case:
                case_explanation = get_case_explanation(case)
                if case_explanation:
                    st.markdown(f"""
                    <div class="grammar-explanation">
                        <strong>📋 격 지배:</strong> {case}<br/>
                        {case_explanation}
                    </div>
                    """, unsafe_allow_html=True)
    
    # 명사-동사 복합어
    elif "nomen-verb" in pos.lower():
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
        grammar_sections.append(f"🏷️ **테마**: {theme}")
    
    # 추가 정보 섹션
    if grammar_sections:
        sections_html = "".join([f"<li>{section}</li>" for section in grammar_sections])
        st.markdown(f"""
        <div class="grammar-info">
            <div class="grammar-title">📚 추가 정보</div>
            <ul>{sections_html}</ul>
        </div>
        """, unsafe_allow_html=True)

# --- 5) JavaScript를 이용한 개선된 클릭 오버레이 ---
def create_click_overlay(card_id: str) -> bool:
    """JavaScript를 이용해 정확한 클릭 감지를 구현합니다."""
    
    # 고유 키 생성
    overlay_key = f"overlay_{card_id}_{random.randint(1000, 9999)}"
    
    # JavaScript 코드
    js_code = f"""
    <script>
        (function() {{
            // 이전 오버레이 제거
            var existingOverlay = document.getElementById('{overlay_key}');
            if (existingOverlay) {{
                existingOverlay.remove();
            }}
            
            // 카드 컨테이너 찾기
            var cardContainer = document.querySelector('.card-container:last-of-type');
            if (!cardContainer) return;
            
            // 투명 오버레이 생성
            var overlay = document.createElement('div');
            overlay.id = '{overlay_key}';
            overlay.className = 'click-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: transparent;
                border: none;
                border-radius: 20px;
                cursor: pointer;
                z-index: 10;
                transition: background 0.2s ease;
            `;
            
            // 호버 효과
            overlay.addEventListener('mouseenter', function() {{
                this.style.background = 'rgba(0, 123, 255, 0.05)';
            }});
            
            overlay.addEventListener('mouseleave', function() {{
                this.style.background = 'transparent';
            }});
            
            // 클릭 이벤트
            overlay.addEventListener('click', function(e) {{
                e.preventDefault();
                e.stopPropagation();
                
                // Streamlit의 상태 업데이트 트리거
                var event = new CustomEvent('cardFlip', {{
                    detail: {{ cardId: '{card_id}' }}
                }});
                document.dispatchEvent(event);
            }});
            
            // 카드 컨테이너에 오버레이 추가
            cardContainer.style.position = 'relative';
            cardContainer.appendChild(overlay);
        }})();
    </script>
    """
    
    st.markdown(js_code, unsafe_allow_html=True)
    
    # 클릭 감지를 위한 숨겨진 버튼
    click_detected = st.button(
        "클릭 감지용", 
        key=f"hidden_{overlay_key}",
        help="카드를 클릭하세요",
        type="secondary",
        use_container_width=False
    )
    
    # CSS로 버튼 숨기기
    st.markdown(f"""
    <style>
        button[data-testid="baseButton-secondary"][title="카드를 클릭하세요"] {{
            display: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    return click_detected

# --- 6) 필터링 기능 ---
def create_filter_section(df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, any]:
    """필터링 섹션을 생성하고 필터 값들을 반환합니다."""
    st.markdown("### 🔍 학습 필터")
    
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 품사 필터
            pos_options = get_unique_values(df, mapping, 'pos')
            selected_pos = st.multiselect(
                "품사 선택",
                options=['전체'] + pos_options,
                default=['전체'],
                help="학습하고 싶은 품사를 선택하세요"
            )
        
        with col2:
            # 테마 필터  
            theme_options = get_unique_values(df, mapping, 'theme')
            selected_themes = st.multiselect(
                "테마 선택",
                options=['전체'] + theme_options,
                default=['전체'],
                help="학습하고 싶은 테마를 선택하세요"
            )
        
        # 추가 필터 옵션
        with st.expander("🔧 고급 필터 옵션"):
            col3, col4 = st.columns(2)
            
            with col3:
                # 재귀동사만 학습
                reflexive_only = st.checkbox(
                    "재귀동사만 학습",
                    help="재귀동사(sich 동사)만 학습합니다"
                )
                
                # 예문이 있는 단어만
                with_examples = st.checkbox(
                    "예문이 있는 단어만",
                    help="예문이 포함된 단어만 학습합니다"
                )
            
            with col4:
                # 문법 정보가 있는 단어만
                with_grammar = st.checkbox(
                    "문법 정보가 있는 단어만",
                    help="격 정보나 전치사 정보가 있는 단어만 학습합니다"
                )
                
                # 번역이 있는 예문만
                with_translation = st.checkbox(
                    "번역이 있는 예문만",
                    help="한국어 번역이 있는 예문만 학습합니다"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'pos': selected_pos,
        'themes': selected_themes,
        'reflexive_only': reflexive_only,
        'with_examples': with_examples,
        'with_grammar': with_grammar,
        'with_translation': with_translation
    }

def apply_filters(df: pd.DataFrame, mapping: Dict[str, str], filters: Dict[str, any]) -> pd.DataFrame:
    """필터를 적용하여 데이터를 걸러냅니다."""
    filtered_df = df.copy()
    
    # 품사 필터
    if '전체' not in filters['pos'] and filters['pos']:
        if 'pos' in mapping:
            filtered_df = filtered_df[
                filtered_df[mapping['pos']].isin(filters['pos'])
            ]
    
    # 테마 필터
    if '전체' not in filters['themes'] and filters['themes']:
        if 'theme' in mapping:
            filtered_df = filtered_df[
                filtered_df[mapping['theme']].isin(filters['themes'])
            ]
    
    # 재귀동사 필터
    if filters['reflexive_only'] and 'reflexive' in mapping:
        reflexive_col = mapping['reflexive']
        filtered_df = filtered_df[
            filtered_df[reflexive_col].str.lower().isin(['ja', 'yes', 'true', '1'])
        ]
    
    # 예문 필터
    if filters['with_examples'] and 'german_example' in mapping:
        example_col = mapping['german_example']
        filtered_df = filtered_df[
            (filtered_df[example_col].notna()) & 
            (filtered_df[example_col].str.strip() != '') &
            (filtered_df[example_col] != 'nan')
        ]
    
    # 문법 정보 필터
    if filters['with_grammar']:
        grammar_cols = []
        for col_key in ['verb_case', 'verb_prep', 'complement_structure']:
            if col_key in mapping:
                grammar_cols.append(mapping[col_key])
        
        if grammar_cols:
            grammar_condition = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            for col in grammar_cols:
                grammar_condition |= (
                    (filtered_df[col].notna()) & 
                    (filtered_df[col].str.strip() != '') &
                    (filtered_df[col] != 'nan')
                )
            filtered_df = filtered_df[grammar_condition]
    
    # 번역 필터
    if filters['with_translation'] and 'ko_example_translation' in mapping:
        translation_col = mapping['ko_example_translation']
        filtered_df = filtered_df[
            (filtered_df[translation_col].notna()) & 
            (filtered_df[translation_col].str.strip() != '') &
            (filtered_df[translation_col] != 'nan')
        ]
    
    return filtered_df

# --- 7) 학습 통계 및 진행률 관리 ---
class LearningStats:
    """학습 통계를 관리하는 클래스"""
    
    def __init__(self):
        if 'learning_stats' not in st.session_state:
            st.session_state.learning_stats = {
                'total_cards_seen': 0,
                'correct_answers': 0,
                'cards_flipped': 0,
                'session_start_time': pd.Timestamp.now(),
                'difficult_cards': set(),
                'mastered_cards': set()
            }
    
    def increment_cards_seen(self):
        st.session_state.learning_stats['total_cards_seen'] += 1
    
    def increment_flips(self):
        st.session_state.learning_stats['cards_flipped'] += 1
    
    def mark_difficult(self, card_index):
        st.session_state.learning_stats['difficult_cards'].add(card_index)
    
    def mark_mastered(self, card_index):
        st.session_state.learning_stats['mastered_cards'].add(card_index)
        st.session_state.learning_stats['difficult_cards'].discard(card_index)
    
    def get_session_duration(self):
        start_time = st.session_state.learning_stats['session_start_time']
        return pd.Timestamp.now() - start_time
    
    def get_stats_summary(self):
        stats = st.session_state.learning_stats
        duration = self.get_session_duration()
        
        return {
            'total_seen': stats['total_cards_seen'],
            'cards_flipped': stats['cards_flipped'],
            'session_duration': duration,
            'difficult_count': len(stats['difficult_cards']),
            'mastered_count': len(stats['mastered_cards']),
            'avg_flips_per_card': stats['cards_flipped'] / max(1, stats['total_cards_seen'])
        }

def render_progress_section(current_pos: int, total_cards: int, stats: LearningStats):
    """진행률 섹션을 렌더링합니다."""
    progress_percentage = (current_pos + 1) / total_cards
    stats_summary = stats.get_stats_summary()
    
    # 메인 진행률 표시
    st.progress(progress_percentage)
    
    # 상세 진행 정보
    st.markdown(f"""
    <div class="progress-info">
        <div>📖 <strong>{current_pos + 1}</strong> / {total_cards}</div>
        <div>🔄 뒤집기: <strong>{stats_summary['cards_flipped']}</strong>회</div>
        <div>⏱️ 학습시간: <strong>{str(stats_summary['session_duration']).split('.')[0]}</strong></div>
        <div>📊 평균 뒤집기: <strong>{stats_summary['avg_flips_per_card']:.1f}</strong>회/카드</div>
    </div>
    """, unsafe_allow_html=True)

# --- 8) 향상된 네비게이션 ---
def create_navigation_controls(current_pos: int, total_cards: int, stats: LearningStats):
    """네비게이션 컨트롤을 생성합니다."""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 1])
    
    navigation_actions = {}
    
    with col1:
        if st.button("⏮️ 처음", help="첫 번째 카드로 이동"):
            navigation_actions['action'] = 'first'
    
    with col2:
        if st.button("⬅️ 이전", help="이전 카드로 이동", disabled=(current_pos <= 0)):
            navigation_actions['action'] = 'previous'
    
    with col3:
        if st.button("🔄 문제/정답 전환", help="카드를 뒤집습니다", use_container_width=True):
            navigation_actions['action'] = 'flip'
    
    with col4:
        if st.button("➡️ 다음", help="다음 카드로 이동", disabled=(current_pos >= total_cards - 1)):
            navigation_actions['action'] = 'next'
    
    with col5:
        if st.button("⏭️ 마지막", help="마지막 카드로 이동"):
            navigation_actions['action'] = 'last'
    
    # 두 번째 행 - 학습 관리 버튼들
    st.markdown("---")
    col6, col7, col8, col9 = st.columns(4)
    
    with col6:
        if st.button("🔀 카드 섞기", help="카드 순서를 무작위로 섞습니다"):
            navigation_actions['action'] = 'shuffle'
    
    with col7:
        if st.button("😅 어려워요", help="이 카드를 어려운 카드로 표시"):
            current_idx = st.session_state.get('current_card_index', 0)
            stats.mark_difficult(current_idx)
            st.success("어려운 카드로 표시했습니다!")
    
    with col8:
        if st.button("✅ 외웠어요", help="이 카드를 외운 카드로 표시"):
            current_idx = st.session_state.get('current_card_index', 0)
            stats.mark_mastered(current_idx)
            st.success("외운 카드로 표시했습니다!")
    
    with col9:
        if st.button("🎯 어려운 카드만", help="어려운 카드들만 다시 학습"):
            navigation_actions['action'] = 'difficult_only'
    
    return navigation_actions

# --- 9) 향상된 사이드바 ---
def create_enhanced_sidebar(df: pd.DataFrame, mapping: Dict[str, str], stats: LearningStats, filters: Dict[str, any]):
    """향상된 사이드바를 생성합니다."""
    with st.sidebar:
        st.header("📊 학습 대시보드")
        
        # 기본 통계
        stats_summary = stats.get_stats_summary()
        
        # 메트릭 표시
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 단어", len(df), help="현재 필터된 총 단어 수")
            st.metric("뒤집기", stats_summary['cards_flipped'], help="총 카드 뒤집기 횟수")
        
        with col2:
            st.metric("학습완료", stats_summary['mastered_count'], help="외운 것으로 표시한 카드 수")
            st.metric("어려운 카드", stats_summary['difficult_count'], help="어려운 것으로 표시한 카드 수")
        
        # 학습 시간
        duration = stats_summary['session_duration']
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        st.info(f"⏱️ 학습시간: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        
        st.markdown("---")
        
        # 품사별 분포
        if 'pos' in mapping and len(df) > 0:
            st.subheader("📈 품사별 분포")
            pos_counts = df[mapping['pos']].value_counts()
            st.bar_chart(pos_counts)
        
        # 테마별 분포
        if 'theme' in mapping and len(df) > 0:
            st.subheader("🏷️ 테마별 분포")
            theme_counts = df[mapping['theme']].value_counts()
            st.bar_chart(theme_counts)
        
        st.markdown("---")
        
        # 필터 요약
        st.subheader("🔍 적용된 필터")
        active_filters = []
        
        if '전체' not in filters['pos'] and filters['pos']:
            active_filters.append(f"품사: {', '.join(filters['pos'])}")
        
        if '전체' not in filters['themes'] and filters['themes']:
            active_filters.append(f"테마: {', '.join(filters['themes'])}")
        
        if filters['reflexive_only']:
            active_filters.append("재귀동사만")
        
        if filters['with_examples']:
            active_filters.append("예문 포함")
        
        if filters['with_grammar']:
            active_filters.append("문법정보 포함")
            
        if filters['with_translation']:
            active_filters.append("번역 포함")
        
        if active_filters:
            for filter_desc in active_filters:
                st.info(f"✅ {filter_desc}")
        else:
            st.info("🔄 모든 카드 표시")
        
        st.markdown("---")
        
        # 학습 팁
        with st.expander("💡 학습 팁"):
            st.markdown("""
            **효과적인 학습 방법:**
            
            1. **카드 클릭**: 흰색 카드 영역을 클릭해서 뒤집어보세요
            2. **반복 학습**: 어려운 단어는 '어려워요' 버튼으로 표시하세요
            3. **필터 활용**: 특정 품사나 테마만 집중적으로 학습하세요
            4. **문법 주목**: 동사의 격지배와 전치사 정보를 주의깊게 보세요
            5. **예문 활용**: 예문을 통해 실제 사용법을 익히세요
            """)

# --- 10) 메인 애플리케이션 ---
def main():
    """메인 애플리케이션 함수"""
    
    # 제목 및 소개
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1>🇩🇪 German Grammar Flashcard</h1>
        <p style='font-size: 1.2em; color: #666;'>
            독일어 C1 TELC 단어장 - 인터랙티브 학습 도구
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 데이터 로드
    df = load_data('c1_telc_voca.csv')
    if df is None:
        st.error("데이터를 로드할 수 없습니다. CSV 파일이 있는지 확인해주세요.")
        st.stop()
    
    # 세션 상태 초기화
    if 'app_initialized' not in st.session_state:
        st.session_state.df, st.session_state.mapping = standardize_columns(df)
        if st.session_state.df is None:
            st.stop()
        
        st.session_state.show_answer = False
        st.session_state.app_initialized = True
    
    # 통계 객체 초기화
    stats = LearningStats()
    
    # 필터 섹션
    filters = create_filter_section(st.session_state.df, st.session_state.mapping)
    
    # 필터 적용
    filtered_df = apply_filters(st.session_state.df, st.session_state.mapping, filters)
    
    if len(filtered_df) == 0:
        st.warning("⚠️ 선택한 조건에 맞는 단어가 없습니다. 필터 조건을 조정해주세요.")
        return
    
    # 필터가 변경된 경우 인덱스 재설정
    filter_key = str(sorted(filters.items()))
    if 'last_filter_key' not in st.session_state or st.session_state.last_filter_key != filter_key:
        st.session_state.filtered_indices = list(range(len(filtered_df)))
        random.shuffle(st.session_state.filtered_indices)
        st.session_state.current_position = 0
        st.session_state.last_filter_key = filter_key
        st.session_state.show_answer = False
    
    # 현재 위치 확인 및 조정
    if 'current_position' not in st.session_state:
        st.session_state.current_position = 0
    
    if st.session_state.current_position >= len(filtered_df):
        st.session_state.current_position = 0
    
    # 현재 카드 데이터
    current_pos = st.session_state.current_position
    indices = st.session_state.filtered_indices
    current_row = filtered_df.iloc[indices[current_pos]]
    st.session_state.current_card_index = indices[current_pos]
    
    # 진행률 표시
    render_progress_section(current_pos, len(filtered_df), stats)
    
    # 네비게이션 컨트롤
    nav_actions = create_navigation_controls(current_pos, len(filtered_df), stats)
    
    # 네비게이션 액션 처리
    if nav_actions:
        action = nav_actions.get('action')
        if action == 'first':
            st.session_state.current_position = 0
            st.session_state.show_answer = False
            st.rerun()
        elif action == 'previous':
            st.session_state.current_position = max(0, current_pos - 1)
            st.session_state.show_answer = False
            st.rerun()
        elif action == 'next':
            st.session_state.current_position = min(len(filtered_df) - 1, current_pos + 1)
            st.session_state.show_answer = False
            stats.increment_cards_seen()
            st.rerun()
        elif action == 'last':
            st.session_state.current_position = len(filtered_df) - 1
            st.session_state.show_answer = False
            st.rerun()
        elif action == 'flip':
            st.session_state.show_answer = not st.session_state.show_answer
            stats.increment_flips()
            st.rerun()
        elif action == 'shuffle':
            random.shuffle(st.session_state.filtered_indices)
            st.session_state.current_position = 0
            st.session_state.show_answer = False
            st.rerun()
        elif action == 'difficult_only':
            difficult_cards = st.session_state.learning_stats['difficult_cards']
            if difficult_cards:
                st.session_state.filtered_indices = list(difficult_cards)
                st.session_state.current_position = 0
                st.session_state.show_answer = False
                st.success(f"어려운 카드 {len(difficult_cards)}개를 표시합니다!")
                st.rerun()
            else:
                st.info("아직 어려운 카드로 표시된 것이 없습니다.")
    
    st.markdown("---")
    
    # 메인 카드 영역
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 카드 렌더링
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    
    if st.session_state.show_answer:
        render_answer_card(current_row, st.session_state.mapping)
        card_id = "answer"
    else:
        render_question_card(current_row, st.session_state.mapping)
        card_id = "question"
    
    # 클릭 오버레이 - 개선된 버전
    if create_click_overlay(card_id):
        st.session_state.show_answer = not st.session_state.show_answer
        stats.increment_flips()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 키보드 단축키 안내
    st.markdown("""
    <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;'>
        <strong>💡 사용법:</strong> 흰색 카드 영역을 클릭하면 카드가 뒤집어집니다 | 
        네비게이션 버튼으로 카드를 이동할 수 있습니다
    </div>
    """, unsafe_allow_html=True)
    
    # 향상된 사이드바
    create_enhanced_sidebar(filtered_df, st.session_state.mapping, stats, filters)

if __name__ == "__main__":
    main()
