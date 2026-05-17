import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os
import numpy as np

# 1. 학교 성적 분석 시스템 레이아웃 세팅
st.set_page_config(page_title="학교 맞춤형 성적 데이터 분석 시스템", layout="wide")
st.title("🏫 학교 맞춤형 학생 성적 분석 및 추이 예측 시스템")
st.write("엑셀에 '이름', '날짜', '학급'과 과목 점수들을 입력하면 학생별 성적 추이를 분석하고 상담용 PDF를 생성합니다.")

# 2. 기초 데이터 세팅 (테스트용 기본 성적 구조)
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame({
        '이름': ['김철수', '김철수', '이영희', '이영희'],
        '날짜': pd.to_datetime(['2026-03-20', '2026-06-15', '2026-03-20', '2026-06-15']),
        '국어': [80, 88, 90, 95],
        '영어': [85, 92, 88, 90],
        '수학': [70, 78, 95, 98],
        '학급': ['1반', '1반', '1반', '1반']
    })

# 📥 엑셀 파일 업로드 기능
uploaded_file = st.file_uploader("📥 분석할 성적 엑셀 파일을 업로드하세요 (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    uploaded_df = pd.read_excel(uploaded_file)
    
    # [핵심 체크] 필수 칸 검사
    if '날짜' in uploaded_df.columns and '이름' in uploaded_df.columns:
        uploaded_df['날짜'] = pd.to_datetime(uploaded_df['날짜'])
        st.session_state.sales_data = uploaded_df
        st.success("🎯 성적 데이터를 완벽하게 분석 엔진에 로드했습니다!")
    else:
        st.error("❌ 에러: 엑셀 파일에 '날짜'와 '이름' 칸이 필수적으로 있어야 합니다.")
        st.stop()

st.markdown("---")

# ✍️ 1단계: 데이터 직접 편집창
st.subheader("✍️ 1단계: 로드된 성적 데이터 실시간 편집기")
edited_df = st.data_editor(st.session_state.sales_data, num_rows="dynamic", use_container_width=True)
st.session_state.sales_data = edited_df

if len(edited_df) >= 2:
    df = edited_df.copy()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 숫자로 된 과목 열 추출
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # 학급이나 학년 같은 분류용 열 제외하기 위해 과목만 필터링
    excluded_subjects = ['연도', '월', 'Time_Index']
    subject_options = [col for col in numeric_cols if col not in excluded_subjects]

    if subject_options:
        st.markdown("### 🎯 분석 과목 선택")
        selected_subject = st.selectbox("📊 분석하고 싶은 과목을 선택하세요", subject_options)
    else:
        st.error("분석할 수 있는 점수 칸(국어, 영어, 수학 등)이 존재하지 않습니다.")
        st.stop()

    # 성적 통계 계산
    total_avg = df[selected_subject].mean()
    max_score = df[selected_subject].max()
    
    st.markdown("---")
    st.subheader(f"📊 2단계: [{selected_subject}] 과목 실시간 종합 대시보드")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"📈 전체 학생 [{selected_subject}] 평균점수", value=f"{round(total_avg, 1)} 점")
    with col2:
        st.metric(label=f"🥇 [{selected_subject}] 최고점수", value=f"{int(max_score)} 점")

    # 3. 실시간 웹 대시보드 시각화
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        fig1 = px.line(
            df.sort_values(by='날짜'), 
            x='날짜', 
            y=selected_subject, 
            color='이름', 
            markers=True,
            title=f'📈 시간 흐름에 따른 학생별 [{selected_subject}] 성적 성장 추이'
        )
        fig1.update_layout(xaxis_title='시험 날짜', yaxis_title='점수')
        st.plotly_chart(fig1, use_container_width=True)
        
    with fig_col2:
        # 날짜 타입 변환 예외 처리 완료된 안전한 막대 차트
        df_bar = df.sort_values(by='날짜').copy()
        if ptypes := df_bar['날짜'].dtype:
            df_bar['날짜_문자열'] = df_bar['날짜'].dt.strftime('%Y-%m-%d')
        else:
            df_bar['날짜_문자열'] = df_bar['날짜'].astype(str)
            
        fig2 = px.bar(
            df_bar,
            x='이름',
            y=selected_subject,
            color='날짜_문자열',
            barmode='group',
            text=selected_subject,
            title=f'📊 학생별 [{selected_subject}] 시험별 점수 비교'
        )
        fig2.update_layout(xaxis_title='학생 이름', yaxis_title='점수')
        st.plotly_chart(fig2, use_container_width=True)

    # 4. 교사용/학부모 상담용 PDF 종합 보고서 출력
    st.markdown("---")
    st.subheader("📥 3단계: 학부모 상담 및 보관용 성적 통계 PDF 보고서 출력")
    
    if st.button("📄 종합 성적 PDF 보고서 생성하기"):
        try:
            import matplotlib.pyplot as plt
            import time
            
            # 웹 차트 저장 시 운영체제별 한글 깨짐 대응 (맑은고딕 우선 적용)
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            # 1번 그래프 생성 (선형 추이)
            plt.figure(figsize=(7, 4))
            for name, group in df.groupby('이름'):
                group_sorted = group.sort_values(by='날짜')
                plt.plot(group_sorted['날짜'].dt.strftime('%Y-%m-%d'), group_sorted[selected_subject], marker='o', label=name, linewidth=2)
            plt.title(f'날짜별 [{selected_subject}] 성적 변동 추이')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig('chart1.png', dpi=200)
            plt.close()
            
            # 2번 그래프 생성 (막대그래프)
            plt.figure(figsize=(7, 4))
            latest_date = df['날짜'].max()
            df_latest = df[df['날짜'] == latest_date]
            plt.bar(df_latest['이름'], df_latest[selected_subject], color='#1f77b4', alpha=0.8)
            plt.title(f'최근 시험 [{selected_subject}] 성적 비교')
            plt.grid(True, linestyle='--', alpha=0.3, axis='y')
            plt.tight_layout()
            plt.savefig('chart2.png', dpi=200)
            plt.close()
            
            time.sleep(0.5)
            
            # 서버 OS 환경 종속적 폰트 주소를 지우고 기본 내장 폰트(Helvetica)로 우회 
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()
            
            # 표준 폰트로 변환하여 인프라 다운 방지
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(190, 15, f"STUDENT PERFORMANCE ANALYTICS REPORT", ln=True, align="C")
            pdf.set_draw_color(31, 119, 180)
            pdf.line(10, 27, 200, 27)
            pdf.ln(10)
            
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(190, 8, f"[ANALYSIS INFO] Target Subject: {selected_subject}", ln=True)
            pdf.cell(190, 8, f"[ANALYSIS INFO] Total Class Average: {round(total_avg, 2)} points", ln=True)
            pdf.cell(190, 8, f"[ANALYSIS INFO] Highest Score: {int(max_score)} points", ln=True)
            pdf.ln(5)
            pdf.image("chart1.png", x=15, y=65, w=180)
            
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(190, 10, f"Section 02. Recent Exam Score Comparison Map", ln=True)
            pdf.line(10, 22, 200, 22)
            pdf.ln(5)
            pdf.image("chart2.png", x=15, y=30, w=180)
            
            pdf.output("student_perf_report.pdf")
            os.remove("chart1.png")
            os.remove("chart2.png")
            
            st.success(f"🎉 성공! [{selected_subject}] 분석이 반영된 맞춤형 교사용 PDF 보고서가 완성되었습니다!")
            
            with open("student_perf_report.pdf", "rb") as f:
                st.download_button(
                    label="📥 성적 분석 마스터 리포트 다운로드",
                    data=f,
                    file_name=f"Student_Report_{selected_subject}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"PDF 리포트 생성 중 오류가 났습니다: {e}")
else:
    st.warning("⚠️ 분석을 가동하려면 최소 2개 이상의 데이터 행이 필요합니다.")


