from flask import Flask, render_template
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data import get_data, get_summary

app = Flask(__name__)

COLORS = {"Vale": "#1f77b4", "Itaú": "#ff7f0e", "Petrobras": "#2ca02c"}


def build_cotacao_chart(close_df):
    fig = go.Figure()
    for name in close_df.columns:
        series = close_df[name].dropna()
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            name=name,
            line=dict(color=COLORS[name], width=2),
            hovertemplate="%{x|%d/%m/%Y}<br>R$ %{y:.2f}<extra>" + name + "</extra>",
        ))
    fig.update_layout(
        title="Cotação de Fechamento (R$)",
        xaxis_title="Data",
        yaxis_title="Preço (R$)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
        height=400,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def build_performance_chart(close_df):
    fig = go.Figure()
    for name in close_df.columns:
        series = close_df[name].dropna()
        perf = (series / series.iloc[0] - 1) * 100
        fig.add_trace(go.Scatter(
            x=perf.index,
            y=perf.values,
            name=name,
            line=dict(color=COLORS[name], width=2),
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:.2f}%<extra>" + name + "</extra>",
        ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title="Performance Acumulada no Ano (%)",
        xaxis_title="Data",
        yaxis_title="Variação (%)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
        height=400,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def build_volume_chart(volume_df):
    monthly = volume_df.resample("ME").sum()
    monthly.index = monthly.index.strftime("%b/%Y")

    fig = go.Figure()
    for name in monthly.columns:
        fig.add_trace(go.Bar(
            x=monthly.index,
            y=monthly[name],
            name=name,
            marker_color=COLORS[name],
            hovertemplate="%{x}<br>%{y:,.0f} ações<extra>" + name + "</extra>",
        ))
    fig.update_layout(
        title="Volume Negociado Mensal",
        xaxis_title="Mês",
        yaxis_title="Volume (ações)",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=60, b=40),
        height=400,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


@app.route("/")
def index():
    data = get_data()
    close_df = data["close"]
    volume_df = data["volume"]

    summary = get_summary(close_df)
    chart_cotacao = build_cotacao_chart(close_df)
    chart_performance = build_performance_chart(close_df)
    chart_volume = build_volume_chart(volume_df)

    return render_template(
        "index.html",
        summary=summary,
        chart_cotacao=chart_cotacao,
        chart_performance=chart_performance,
        chart_volume=chart_volume,
    )


if __name__ == "__main__":
    app.run(debug=True)
