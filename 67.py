import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import os
import numpy as np

# 1. 무한 자동화 시스템 레이아웃 세팅
st.set_page_config(page_title="무한 자동화 AI 분석 시스템", layout="wide")
st.title("🤖 어떤 칸이든 다 분석하는 무한 자동화 AI 매출 예측 시스템")
st.write("엑셀에 '거래처', '지역', '담당자' 등 어떤 칸을 마음대로 추가해 올려도 코드를 고칠 필요 없이 자동 분석합니다.")

# 2. 기초 데이터 세팅 (테스트용 기본 데이터 구조)
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = pd.DataFrame({
        '날짜': pd.to_datetime(['2023-01-01', '2024-01-01', '2025-01-01', '2026-05-01']),
        '품목': ['반도체', '의료기기', '서류가방', '신발'],
        '거래처': ['삼성전자', '네이버', '애플', '카카오'],
        '지역': ['서울', '경기', '부산', '서울'],
        '매출': [10000000, 20000000, 15000000, 30000000]
    })

# 엑셀 파일 업로드 기능
uploaded_file = st.file_uploader("📥 기존 엑셀 파일 업로드 (여기에 칸을 맘대로 늘려서 올려보세요!)", type=["xlsx"])
if uploaded_file is not None:
    uploaded_df = pd.read_excel(uploaded_file)
    if '날짜' in uploaded_df.columns and '매출' in uploaded_df.columns:
        uploaded_df['날짜'] = pd.to_datetime(uploaded_df['날짜'])
        st.session_state.sales_data = uploaded_df
        st.success("새로운 대형 데이터를 완벽하게 가져왔습니다!")
    else:
        st.error("엑셀 파일에 '날짜'와 '매출' 칸은 필수적으로 있어야 합니다.")

st.markdown("---")

# ✍️ 1단계: 데이터 직접 편집창
st.subheader("✍️ 1단계: 매출 데이터 실시간 편집")
edited_df = st.data_editor(st.session_state.sales_data, num_rows="dynamic", use_container_width=True)
st.session_state.sales_data = edited_df

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
        st.metric(label="💰 실시간 총 매출액", value=f"{total_sales:,} 원")
    with col2:
        st.metric(label="📊 평균 매출액", value=f"{int(avg_sales):,} 원")

    # 🛠️ 엑셀에 들어온 모든 칸 이름을 파이썬이 자동으로 긁어오기
    all_columns = df.columns.tolist()
    excluded_cols = ['날짜', '매출', '연도', '월', 'Time_Index']
    analysis_options = [col for col in all_columns if col not in excluded_cols]

    st.markdown("### 🎯 마우스 클릭 하나로 모든 항목 입체 분석")
    selected_target = st.selectbox("📊 분석하고 싶은 기준 칸(열)을 선택하세요", analysis_options)

    # 🤖 AI 시계열 매출 미래 예측 연산
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
        fig1.add_trace(go.Scatter(x=df_date['날짜'], y=df_date['매출'], name='과거 실제 매출', mode='lines+markers', line=dict(color='#1f77b4', width=2)))
        fig1.add_trace(go.Scatter(x=df_future['날짜'], y=df_future['매출'], name='AI 향후 6개월 예측', mode='lines+markers', line=dict(color='#ffd700', width=3, dash='dash')))
        fig1.update_layout(title='월별 매출 변동 트렌드 및 AI 미래 예측 분석', xaxis_title='날짜', yaxis_title='매출')
        st.plotly_chart(fig1, use_container_width=True)
        
    with fig_col2:
        df_dynamic = df.groupby(selected_target)['매출'].sum().reset_index()
        fig2 = px.pie(df_dynamic, values='매출', names=selected_target, title=f'🚨 [자동 감지] {selected_target}별 매출 기여도 비중')
        st.plotly_chart(fig2, use_container_width=True)

    # 4. 임원용 PDF 종합 보고서 출력
    st.markdown("---")
    st.subheader("📥 3단계: 최고경영자 보고용 AI 통합 분석 보고서 출력")
    
    if st.button("📄 종합 PDF 보고서 생성하기"):
        try:
            import matplotlib.pyplot as plt
            import time
            
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
            
            plt.figure(figsize=(7, 4))
            plt.plot(df_date['날짜'], df_date['매출'], marker='o', color='#1f77b4', label='실제 매출', linewidth=2)
            plt.plot(df_future['날짜'], df_future['매출'], marker='x', color='#d4af37', label='AI 미래 예측', linestyle='--', linewidth=2)
            plt.title('월별 매출 변동 및 AI 향후 6개월 예측 트렌드')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig('chart1.png', dpi=200)
            plt.close()
            
            plt.figure(figsize=(6, 4))
            plt.pie(df_dynamic['매출'], labels=df_dynamic[selected_target], autopct='%1.1f%%', startangle=90, 
                    colors=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'])
            plt.title(f'{selected_target}별 매출 비중 현황')
            plt.tight_layout()
            plt.savefig('chart2.png', dpi=200)
            plt.close()
            
            time.sleep(0.5)
            
            # 📄 PDF 객체 생성 및 한글 폰트 추가 치트키
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            
            # 💡 윈도우 시스템 폴더에 있는 진짜 한글 폰트(바탕체) 파일을 가져와 PDF 엔진에 주입합니다!
            font_path = r"C:\Windows\Fonts\batang.ttc"
            pdf.add_font("Batang", "", font_path, uni=True)
            pdf.add_font("BatangB", "", font_path, uni=True) # 굵은 글씨용 추가
            
            pdf.add_page()
            
            # 폰트를 Helvetica 대신 방금 주입한 진짜 한글 폰트 'Batang'으로 설정!
            pdf.set_font("Batang", "", 24)
            pdf.cell(190, 15, "AI INTEGRATED MANAGEMENT REPORT", ln=True, align="C")
            pdf.set_draw_color(31, 119, 180)
            pdf.line(10, 27, 200, 27)
            pdf.ln(10)
            
            pdf.set_font("Batang", "", 12)
            pdf.cell(190, 8, f"[AI SUMMARY] Total Revenue: {total_sales:,} KRW", ln=True)
            pdf.cell(190, 8, f"[AI SUMMARY] Selected Target Analysis: {selected_target}", ln=True) # 💡 이제 '품목' 글자 안 터짐!
            # 💡 future_preds 뒤에 [0]을 붙여서 '다음 달 첫 번째 예측값'만 정수로 바꿉니다!
            pdf.cell(190, 8, f"[AI SUMMARY] Predicted Next Month Revenue: {int(future_preds[0]):,} KRW", ln=True)

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
            
            st.success(f"🎉 사용자가 고른 [{selected_target}] 분석이 완벽한 한글 컬러 리포트로 완성되었습니다!")
            
            with open("ceo_ai_predict_report.pdf", "rb") as f:
                st.download_button(
                    label="📥 AI 예측 마스터 리포트 다운로드",
                    data=f,
                    file_name="CEO_AI_예측_종합_분석_보고서.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"라이브러리 연산 중 오류가 났습니다: {e}")
else:
    st.warning("⚠️ 분석을 가동하려면 최소 3개 이상의 매출 행 데이터가 필요합니다.")
