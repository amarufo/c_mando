"""Paleta de colores y plantilla de gráficos del cuadro de mando.

Los mismos valores están en `static/css/dph.css` (variables CSS). Si se cambia la
paleta, se actualizan ambos archivos.
"""

import plotly.graph_objects as go

PALETA = {
    "primario": "#0B3C5D",  # azul petróleo: encabezados, series principales
    "secundario": "#1D6FA5",  # azul medio
    "acento": "#F2A900",  # ámbar de obra: resaltes y alertas leves
    "claro": "#F4F6F8",  # fondo
    "texto": "#1F2933",
    "gris": "#6B7785",
}

SEMAFORO = {
    "ok": "#2E9E6B",
    "alerta": "#F2A900",
    "critico": "#D64545",
    "neutro": "#6B7785",
    "sin_datos": "#B8C0CC",
    "error": "#8B1E1E",
}

# Orden de colores para series categóricas.
SERIE = [
    "#0B3C5D",
    "#1D6FA5",
    "#F2A900",
    "#2E9E6B",
    "#8C6BB1",
    "#D64545",
    "#5BC0BE",
    "#6B7785",
]


def aplicar_tema(fig: go.Figure, titulo: str = "", alto: int = 340) -> go.Figure:
    """Estilo común: fondo blanco, tipografía del sitio, leyenda abajo y colores de la paleta."""
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=14, color=PALETA["primario"]), x=0.0),
        height=alto,
        margin=dict(l=40, r=20, t=46 if titulo else 20, b=60),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            size=12,
            color=PALETA["texto"],
        ),
        colorway=SERIE,
        legend=dict(orientation="h", y=-0.2, x=0),
        hovermode="x unified",
        autosize=True,
    )
    fig.update_xaxes(showgrid=False, linecolor="#D5DAE0")
    fig.update_yaxes(gridcolor="#E8ECF0", zeroline=False)
    return fig


def a_html(fig: go.Figure) -> str:
    """Fragmento HTML del gráfico; plotly.min.js se carga una sola vez desde la plantilla base."""
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"displaylogo": False, "responsive": True},
    )
