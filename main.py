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
