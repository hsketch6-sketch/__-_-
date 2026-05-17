import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os
import numpy as np

# 1. 무한 예외처리 자동화 시스템 레이아웃 세팅
st.set_page_config(page_title="범용 AI 데이터 분석 시스템", layout="wide")
st.title("🤖 학교·기업 겸용 무한 자동화 AI 데이터 예측 시스템")
st.write("엑셀에 '거래처', '지역', '반', '학생이름' 등 어떤 칸이 있어도, 그리고 '매출' 대신 '금액/점수'가 적혀있어도 자동으로 찾아내어 분석합니다.")

# 2. 기초 데이터 세팅 (테스트용 기본 범용 구조)
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame({
        '날짜': pd.to_datetime(['2023-01-01', '2024-01-01', '2025-01-01', '2026-05-01']),
        '품목': ['반도체', '의료기기', '서류가방', '신발'],
        '소속(반)': ['1반', '2반', '3반', '1반'],
        '금액(점수)': [10000000, 20000000, 15000000, 30000000]
    })

# 📥 엑셀 파일 업로드 기능 (학교/회사 파일 수용)
uploaded_file = st.file_uploader("📥 분석할 엑셀 파일을 업로드하세요 (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    uploaded_df = pd.read_excel(uploaded_file)
    
    # 💡 [핵심 예외처리 1] '날짜' 칸이 있는지 가장 먼저 검사
    if '날짜' in uploaded_df.columns:
        uploaded_df['날짜'] = pd.to_datetime(uploaded_df['날짜'])
        
        # 💡 [핵심 예외처리 2] '매출' 칸이 없다면 숫자로 된 가장 첫 번째 칸을 찾아 '매출'로 이름을 강제 통일시킵니다.
        if '매출' not in uploaded_df.columns:
            numeric_cols = uploaded_df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                # 가장 첫 번째 숫자 열의 이름을 '매출'로 변경하여 시스템 엔진에 연결
                uploaded_df = uploaded_df.rename(columns={numeric_cols[0]: '매출'})
                st.info(f"💡 시스템 감지: [{numeric_cols[0]}] 칸을 숫자 분석 데이터로 지정했습니다.")
            else:
                st.error("❌ 에러: 엑셀 파일에 숫자가 적힌 칸(금액, 점수 등)이 최소 하나는 존재해야 합니다.")
                st.stop()
        
        st.session_state.sales_data = uploaded_df
        st.success("🎯 새로운 대형 데이터를 완벽하게 분석 엔진에 로드했습니다!")
    else:
        st.error("❌ 에러: 엑셀 파일에 기본 기준이 되는 '날짜' 칸이 필수적으로 있어야 합니다. (칸 제목을 '날짜'로 고쳐서 올려주세요!)")
        st.stop()

st.markdown("---")

# ✍️ 1단계: 데이터 직접 편집창
st.subheader("✍️ 1단계: 로드된 데이터 실시간 웹 편집기")
edited_df = st.data_editor(st.session_state.sales_data, num_rows="dynamic", use_container_width=True)
st.session_state.sales_data = edited_df

# 만약 사용자가 수동으로 '매출' 칸 이름이 없어진 데이터를 만들었을 때를 대비한 2중 안전장치
if '매출' not in edited_df.columns:
    num_cols = edited_df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        edited_df = edited_df.rename(columns={num_cols[0]: '매출'})

if len(edited_df) >= 3:
    df = edited_df.copy()
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    
    # 💰 KPI 대시보드 계산
    total_sales = df['매출'].sum()
    avg_sales = df['매출'].mean()
    
    st.markdown("---")
    st.subheader("📊 2단계: 무한 자동 감지 실시간 AI 대시보드")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="📊 실시간 수치(금액/점수) 총합", value=f"{int(total_sales):,}")
    with col2:
        st.metric(label="📈 데이터 평균값", value=f"{int(avg_sales):,}")

    # 🛠️ [무한 자동화] 엑셀에 들어온 날짜, 연산용 열을 제외한 모든 글자 칸을 마우스 옵션으로 자동 추출
    all_columns = df.columns.tolist()
    excluded_cols = ['날짜', '매출', '연도', '월', 'Time_Index']
    analysis_options = [col for col in all_columns if col not in excluded_cols]

    if analysis_options:
        st.markdown("### 🎯 클릭 한번으로 학교/회사 맞춤형 입체 분석")
        selected_target = st.selectbox("📊 분석하고 싶은 기준 칸(열)을 선택하세요", analysis_options)
    else:
        st.error("분석할 수 있는 글자 칸(품목, 반, 지역 등)이 존재하지 않습니다.")
        st.stop()

    # 🤖 AI 시계열 미래 예측 연산
    df_date = df.groupby('날짜')['매출'].sum().reset_index().sort_values(by='날짜')
    df_date['Time_Index'] = np.arange(len(df_date))
    x = df_date['Time_Index']
    y = df_date['매출']
    w, b = np.polyfit(x, y, 1)
    
    last_date = df_date['날짜'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=6, freq='MS')
    future_indices = np.arange(len(df_date), len(df_date) + 6)
    future_preds = w * future_indices + b
    df_future = pd.DataFrame({'날짜': future_dates, '매출': future_preds})

    # 3. 실시간 웹 대시보드 시각화
    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_date['날짜'], y=df_date['매출'], name='과거 실제 데이터', mode='lines+markers', line=dict(color='#1f77b4', width=2)))
        fig1.add_trace(go.Scatter(x=df_future['날짜'], y=df_future['매출'], name='AI 향후 6개월 예측', mode='lines+markers', line=dict(color='#ffd700', width=3, dash='dash')))
        fig1.update_layout(title='날짜별 변동 트렌드 및 AI 미래 예측 분석', xaxis_title='날짜', yaxis_title='수치')
        st.plotly_chart(fig1, use_container_width=True)
        
    with fig_col2:
        df_dynamic = df.groupby(selected_target)['매출'].sum().reset_index()
        fig2 = px.pie(df_dynamic, values='매출', names=selected_target, title=f'🚨 [자동 분석] {selected_target}별 데이터 기여도 비중')
        st.plotly_chart(fig2, use_container_width=True)

    # 4. 임원/교장선생님 보고용 PDF 종합 보고서 출력
    st.markdown("---")
    st.subheader("📥 3단계: 보고용 AI 통합 분석 보고서 출력")
    
    if st.button("📄 종합 PDF 보고서 생성하기"):
        try:
            import matplotlib.pyplot as plt
            import time
            
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            plt.figure(figsize=(7, 4))
            plt.plot(df_date['날짜'], df_date['매출'], marker='o', color='#1f77b4', label='실제 데이터', linewidth=2)
            plt.plot(df_future['날짜'], df_future['매출'], marker='x', color='#d4af37', label='AI 미래 예측', linestyle='--', linewidth=2)
            plt.title('날짜별 데이터 변동 및 AI 향후 6개월 예측 트렌드')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig('chart1.png', dpi=200)
            plt.close()
            
            plt.figure(figsize=(6, 4))
            plt.pie(df_dynamic['매출'], labels=df_dynamic[selected_target], autopct='%1.1f%%', startangle=90, 
                    colors=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'])
            plt.title(f'{selected_target}별 데이터 비중 현황')
            plt.tight_layout()
            plt.savefig('chart2.png', dpi=200)
            plt.close()
            
            time.sleep(0.5)
            
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            font_path = r"C:\Windows\Fonts\batang.ttc"
            pdf.add_font("Batang", "", font_path, uni=True)
            pdf.add_page()
            
            pdf.set_font("Batang", "", 24)
            pdf.cell(190, 15, "AI INTEGRATED DATA PERFORMANCE REPORT", ln=True, align="C")
            pdf.set_draw_color(31, 119, 180)
            pdf.line(10, 27, 200, 27)
            pdf.ln(10)
            
            pdf.set_font("Batang", "", 12)
            pdf.cell(190, 8, f"[AI SUMMARY] Total Sum: {int(total_sales):,}", ln=True)
            pdf.cell(190, 8, f"[AI SUMMARY] Target Analysis Category: {selected_target}", ln=True)
            pdf.cell(190, 8, f"[AI SUMMARY] Predicted Next Point Value: {int(future_preds[0]):,}", ln=True)
            pdf.ln(5)
            pdf.image("chart1.png", x=15, y=65, w=180)
            
            pdf.add_page()
            pdf.set_font("Batang", "", 14)
            pdf.cell(190, 10, f"Analysis 01. Dynamic {selected_target} Contribution Analysis", ln=True)
            pdf.line(10, 22, 200, 22)
            pdf.ln(5)
            pdf.image("chart2.png", x=15, y=30, w=180)
            
            pdf.output("ceo_ai_predict_report.pdf")
            os.remove("chart1.png")
            os.remove("chart2.png")
            
            st.success(f"🎉 성공! [{selected_target}] 분석이 반영된 무적의 범용 컬러 PDF 리포트가 완성되었습니다!")
            
            with open("ceo_ai_predict_report.pdf", "rb") as f:
                st.download_button(
                    label="📥 AI 예측 마스터 리포트 다운로드",
                    data=f,
                    file_name="종합_AI_데이터_분석_보고서.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"라이브러리 연산 중 오류가 났습니다: {e}")
else:
    st.warning("⚠️ 분석을 가동하려면 최소 3개 이상의 데이터 행이 필요합니다.")
