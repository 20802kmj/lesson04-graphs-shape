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

    # 숫자형 데이터로 변환
    df["total_audi"] = pd.to_numeric(df["total_audi"], errors="coerce")
    df["first_scrn"] = pd.to_numeric(df["first_scrn"], errors="coerce")

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

    treemap_df = df.dropna(
        subset=["genre", "movieNm", "total_audi"]
    ).copy()

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

    st.divider()

    # ---------------------------------------------------------
    # 그래프 3. 총 관객 히스토그램
    # ---------------------------------------------------------
    st.subheader("3. 영화별 총 관객 분포")

    histogram_df = df.dropna(
        subset=["movieNm", "total_audi"]
    ).copy()

    min_audi = histogram_df["total_audi"].min()
    max_audi = histogram_df["total_audi"].max()

    if min_audi == max_audi:
        bins = 1
        histogram_df["audience_bin"] = "동일한 관객 수"
        most_common_bin = "동일한 관객 수"
    else:
        bins = 10

        histogram_df["audience_bin"] = pd.cut(
            histogram_df["total_audi"],
            bins=bins,
            include_lowest=True,
        )

        bin_counts = (
            histogram_df["audience_bin"]
            .value_counts()
            .sort_index()
        )

        most_common_bin = bin_counts.idxmax()

    fig3 = px.histogram(
        histogram_df,
        x="total_audi",
        nbins=bins,
        title="영화별 총 관객 분포",
        labels={
            "total_audi": "총 관객 수",
            "count": "영화 편수",
        },
    )

    fig3.update_traces(
        hovertemplate=(
            "총 관객 구간: %{x}<br>"
            "영화 편수: %{y}편"
            "<extra></extra>"
        )
    )

    fig3.update_layout(
        xaxis_title="총 관객 수",
        yaxis_title="영화 편수",
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig3, use_container_width=True)

    top_movie = histogram_df.loc[
        histogram_df["total_audi"].idxmax()
    ]

    top_movie_name = top_movie["movieNm"]
    top_movie_audience = int(top_movie["total_audi"])

    st.info(
        f"이 그래프로 알 수 있는 것: 대부분의 영화는 "
        f"{most_common_bin} 구간에 몰려 있으며, "
        f"가장 관객이 많은 영화는 **{top_movie_name}**으로 "
        f"총 관객은 **{top_movie_audience:,}명**입니다."
    )

    st.divider()

    # ---------------------------------------------------------
    # 그래프 4. 개봉일 스크린 수와 총 관객의 관계
    # ---------------------------------------------------------
    st.subheader("4. 개봉일 스크린 수와 총 관객의 관계")

    scatter_df = df.dropna(
        subset=["movieNm", "genre", "first_scrn", "total_audi"]
    ).copy()

    fig4 = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        title="개봉일 스크린 수와 총 관객",
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객 수",
            "genre": "장르",
        },
    )

    fig4.update_traces(
        marker=dict(
            size=9,
            opacity=0.75,
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "개봉일 스크린 수: %{x:,}개<br>"
            "총 관객: %{y:,}명"
            "<extra></extra>"
        ),
    )

    fig4.update_layout(
        xaxis_title="개봉일 스크린 수",
        yaxis_title="총 관객 수",
        legend_title="장르",
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.info("이 그래프로 알 수 있는 것: ________________________________")

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
