import pandas as pd
import plotly.express as px
import streamlit as st


DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 여러 장르가 세로막대(|)로 연결되어 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 총 관객을 숫자로 변환
    df["total_audi"] = pd.to_numeric(df["total_audi"], errors="coerce")

    return df


try:
    df = load_data()

    st.write(
        "1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 "
        f"{len(df)}편의 데이터를 살펴봅니다."
    )

    st.divider()

    # ---------------------------------------------------------
    # 그래프 1. 장르별 영화 편수
    # ---------------------------------------------------------
    st.subheader("1. 장르별 영화 편수")

    genre_counts = (
        df["genre"]
        .value_counts()
        .rename_axis("genre")
        .reset_index(name="count")
    )

    fig1 = px.pie(
        genre_counts,
        names="genre",
        values="count",
        hole=0.55,
        title="장르별 영화 편수",
    )

    fig1.update_traces(
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "편수: %{value}편<br>"
            "비율: %{percent}<extra></extra>"
        ),
    )

    fig1.update_layout(
        legend_title_text="장르",
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info("이 그래프로 알 수 있는 것: ________________________________")

    st.divider()

    # ---------------------------------------------------------
    # 그래프 2. 장르별 영화 트리맵
    # ---------------------------------------------------------
    st.subheader("2. 장르별 영화와 총 관객")

    treemap_df = df.dropna(subset=["genre", "movieNm", "total_audi"]).copy()

    fig2 = px.treemap(
        treemap_df,
        path=["genre", "movieNm"],
        values="total_audi",
        title="장르 안에 들어 있는 영화와 총 관객",
    )

    fig2.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        ),
        textinfo="label",
    )

    fig2.update_layout(
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.info("이 그래프로 알 수 있는 것: ________________________________")

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
