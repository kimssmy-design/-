import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 1. 페이지 기본 설정
st.set_page_config(page_title="체육복신청명단", layout="centered")

# --- 구글 시트 저장 함수 ---
def save_to_google_sheet(data_list):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # [확인] 구글 시트 파일 이름을 정확히 적어주세요.
    spreadsheet = client.open("체육복신청명단") 
    sheet = spreadsheet.get_worksheet(0)
    sheet.append_row(data_list)

# --- [데이터] 규격표 데이터 (이미지 분석 결과) ---
weights = ["40kg", "45kg", "48kg", "52kg", "56kg", "60kg", "64kg", "68kg", "72kg", "76kg", "80kg", "90kg", "100kg"]
heights = ["140cm", "145cm", "155cm", "160cm", "165cm", "170cm", "175cm", "180cm", "185cm", "190cm"]
size_matrix = [
    ["80호", "85호", "85호", "85호", "90호", "90호", "95호", "95호", None, None, None, None, None],
    ["80호", "85호", "85호", "90호", "90호", "95호", "95호", "95호", "100호", "100호", None, None, None],
    [None, "90호", "90호", "90호", "90호", "95호", "95호", "95호", "100호", "105호", "105호", None, None],
    [None, "90호", "90호", "90호", "90호", "95호", "95호", "100호", "100호", "105호", "105호", "110호", None],
    [None, "90호", "95호", "95호", "95호", "95호", "100호", "100호", "100호", "105호", "110호", "110호", None],
    [None, None, "95호", "95호", "95호", "100호", "100호", "100호", "105호", "105호", "110호", "110호", None],
    [None, None, None, None, "100호", "100호", "100호", "100호", "105호", "105호", "110호", "115호", None],
    [None, None, None, None, None, "100호", "105호", "105호", "105호", "105호", "110호", "115호", "120호"],
    [None, None, None, None, None, None, None, "110호", "110호", "110호", "110호", "115호", "120호"],
    [None, None, None, None, None, None, None, None, None, "115호", "115호", "115호", "120호"]
]
df_size = pd.DataFrame(size_matrix, index=heights, columns=weights)

if 'step' not in st.session_state:
    st.session_state.step = 'info'

# --- 1단계: 안내 페이지 (선생님 문구 그대로 반영) ---
if st.session_state.step == 'info':
    st.title("📢 하복 체육복 공동구매 안내")
    
    st.success("""안녕하십니까? 우리학교 교육활동에 관심과 성원을 보내주셔서 감사합니다 😊
본교에서는 학생들의 생활편의를 위해 교복, 생활복, 체육복을 착용하며 사복 착용은 제한하고 있습니다.
4월부터는 학교 지정 복장 착용 지도를 강화하오니 가정에서도 협조 부탁드립니다 🙏
체육복은 치수 확인 후 3/27까지 신청해 주시기 바라며, 이후에는 개별 구매 부탁드립니다 💛
체육복 착용 등교가 가능하며, 체육 시간에는 지정 체육복 착용을 지도하고 있습니다 👍""")
    
    with st.expander("📝 상세 안내 및 입금 정보 확인", expanded=True):
        st.write("""
        - **신청 기한:** ~ 3/27(금)까지
        - **가격:** 하복 33,000원(상의 20,000원, 하의 13,000원)
        - **체육복 제작 업체:** 한국스포츠(주) / 010-8637-5795(이찬형 실장)
        - **입금 계좌:** 우리은행 1002-651-124780 이찬형
        - **주의사항:** 임시 계좌로 3/27(금)까지만 입금이 가능합니다.
        - **입금자명:** 반드시 **'학번 성명'**으로 입금 (예: 1100 홍길동)
        """)

    st.subheader("📏 내 사이즈 찾기")
    col1, col2 = st.columns(2)
    with col1: user_h = st.selectbox("학생 키(cm)", heights, index=3)
    with col2: user_w = st.selectbox("학생 몸무게(kg)", weights, index=5)
    
    recommended = df_size.loc[user_h, user_w]
    if recommended:
        st.metric(label="권장 사이즈", value=recommended)
        st.session_state.recommended_size = recommended
    else:
        st.warning("⚠️ 해당 규격은 별도 문의가 필요합니다.")
        st.session_state.recommended_size = "직접 입력"

    if st.button("위 사이즈로 신청서 작성하기 ➡️"):
        st.session_state.step = 'form'

# --- 2단계: 신청서 작성 및 전송 ---
elif st.session_state.step == 'form':
    st.title("📝 체육복 신청서 작성")
    default_size = st.session_state.get('recommended_size', "95호")
    
    with st.form("purchase_form"):
        st_id = st.text_input("학번", placeholder="예: 10101")
        name = st.text_input("학생 성명")
        all_sizes = ["80호", "85호", "90호", "95호", "100호", "105호", "110호", "115호", "120호", "직접 입력"]
        final_size = st.selectbox("최종 선택 사이즈", all_sizes, index=all_sizes.index(default_size) if default_size in all_sizes else 3)
        
        st.divider()
        st.warning(f"💡 입금 시 입금자명을 반드시 **'{st_id if st_id else '학번'} {name if name else '성명'}'**(으)로 해주세요.")
        confirm_pay = st.checkbox("금액(33,000원) 입금을 완료했습니다.")
        
        submitted = st.form_submit_button("신청서 제출하기")
        
        if submitted:
            if not st_id or not name or not confirm_pay:
                st.error("학번, 성명 입력 및 입금 확인 체크가 필요합니다.")
            else:
                try:
                    # 구글 시트에 [학번, 이름, 사이즈, 입금여부] 순서로 저장
                    save_to_google_sheet([st_id, name, final_size, "입금완료"])
                    st.balloons()
                    st.success(f"접수 완료! {name} 학생({final_size})의 신청이 기록되었습니다.")
                except Exception as e:
                    st.error(f"시트 전송 중 오류가 발생했습니다: {e}")
                
    if st.button("⬅️ 안내 및 사이즈 다시 확인"):
        st.session_state.step = 'info'