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

    st.divider()

    # ---------------------------------------------------------
    # 그래프 5. 장르별 총 관객 박스플롯
    # ---------------------------------------------------------
    st.subheader("5. 장르별 총 관객 분포")

    boxplot_df = df.dropna(
        subset=["genre", "movieNm", "total_audi"]
    ).copy()

    # 영화가 10편 이상인 장르만 선택
    genre_movie_counts = boxplot_df["genre"].value_counts()

    selected_genres = genre_movie_counts[
        genre_movie_counts >= 10
    ].index

    boxplot_df = boxplot_df[
        boxplot_df["genre"].isin(selected_genres)
    ].copy()

    fig5 = px.box(
        boxplot_df,
        x="genre",
        y="total_audi",
        points="outliers",
        hover_name="movieNm",
        title="영화가 10편 이상인 장르의 총 관객 분포",
        labels={
            "genre": "장르",
            "total_audi": "총 관객 수",
        },
    )

    fig5.update_traces(
        marker=dict(
            size=8,
            color="#636EFA",
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "총 관객: %{y:,}명"
            "<extra></extra>"
        ),
    )

    fig5.update_layout(
        xaxis_title="장르",
        yaxis_title="총 관객 수",
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: 영화가 10편 이상인 장르만 비교하면 "
        "장르별 총 관객의 중앙값과 분포, 그리고 다른 영화와 비교해 "
        "특히 관객이 많은 영화(이상치)를 확인할 수 있습니다."
    )
    st.divider()

    # ---------------------------------------------------------
    # 그래프 6. 첫 주 관객을 크기로 표현한 버블 그래프
    # ---------------------------------------------------------
    st.subheader("6. 개봉일 스크린 수와 총 관객 — 첫 주 관객 버블")

    bubble_df = df.dropna(
        subset=[
            "movieNm",
            "genre",
            "first_scrn",
            "total_audi",
            "first_week_audi",
        ]
    ).copy()

    bubble_df["first_week_audi"] = pd.to_numeric(
        bubble_df["first_week_audi"],
        errors="coerce",
    )

    # 숫자로 변환할 수 없는 값 제거
    bubble_df = bubble_df.dropna(
        subset=["first_week_audi"]
    )

    fig6 = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre",
        hover_name="movieNm",
        size_max=45,
        title="개봉일 스크린 수와 총 관객 — 버블 크기는 첫 주 관객",
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객 수",
            "first_week_audi": "첫 주 관객",
            "genre": "장르",
        },
    )

    fig6.update_traces(
        marker=dict(
            opacity=0.7,
            line=dict(
                width=0.5,
                color="white",
            ),
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "개봉일 스크린 수: %{x:,}개<br>"
            "총 관객: %{y:,}명<br>"
            "첫 주 관객: %{marker.size:,}명"
            "<extra></extra>"
        ),
    )

    fig6.update_layout(
        xaxis_title="개봉일 스크린 수",
        yaxis_title="총 관객 수",
        legend_title="장르",
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "개봉일 스크린 수와 총 관객의 관계를 살펴보면서 "
        "첫 주 관객이 많은 영화일수록 버블이 크게 나타나는 것을 함께 확인할 수 있습니다."
    )
    st.divider()

    # ---------------------------------------------------------
    # 그래프 7. 제작 국가 → 장르 선버스트
    # ---------------------------------------------------------
    st.subheader("7. 제작 국가별 장르 구성")

    sunburst_df = df.dropna(
        subset=["nation", "genre", "movieNm"]
    ).copy()

    # 제작 국가와 장르별 영화 편수 집계
    sunburst_counts = (
        sunburst_df
        .groupby(["nation", "genre"])
        .size()
        .reset_index(name="movie_count")
    )

    fig7 = px.sunburst(
        sunburst_counts,
        path=["nation", "genre"],
        values="movie_count",
        title="제작 국가 → 장르별 영화 구성",
        labels={
            "nation": "제작 국가",
            "genre": "장르",
            "movie_count": "영화 편수",
        },
    )

    fig7.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value}편"
            "<extra></extra>"
        ),
        textinfo="label+percent parent",
    )

    fig7.update_layout(
        margin=dict(t=60, b=20, l=20, r=20),
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "제작 국가별로 어떤 장르의 영화가 많이 만들어졌는지와 "
        "각 국가 안에서 장르가 차지하는 비중을 한눈에 비교할 수 있습니다."
    )
    st.divider()

    # ---------------------------------------------------------
    # 그래프 8. 장르별 최고 흥행 영화
    # ---------------------------------------------------------
    st.subheader("8. 장르별 최고 흥행 영화")

    top_by_genre_df = df.dropna(
        subset=["genre", "movieNm", "total_audi"]
    ).copy()

    # 각 장르에서 총 관객이 가장 많은 영화 1편 선택
    top_by_genre = (
        top_by_genre_df
        .loc[
            top_by_genre_df.groupby("genre")["total_audi"].idxmax()
        ]
        .sort_values("total_audi", ascending=True)
    )

    fig8 = px.bar(
        top_by_genre,
        x="total_audi",
        y="genre",
        orientation="h",
        text="movieNm",
        title="장르별 최고 흥행 영화",
        labels={
            "total_audi": "총 관객 수",
            "genre": "장르",
            "movieNm": "영화",
        },
    )

    fig8.update_traces(
        textposition="outside",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "장르: %{y}<br>"
            "총 관객: %{x:,}명"
            "<extra></extra>"
        ),
    )

    fig8.update_layout(
        xaxis_title="총 관객 수",
        yaxis_title="장르",
        margin=dict(t=60, b=20, l=20, r=100),
    )

    st.plotly_chart(fig8, use_container_width=True)

    st.info(
        "이 그래프로 알 수 있는 것: "
        "각 장르에서 총 관객 수가 가장 많은 영화를 비교하면 "
        "장르별 최고 흥행작의 관객 규모를 한눈에 볼 수 있습니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
