import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_ars(valor: float) -> str:
    """Formatea un número con separador de miles (punto), estilo argentino. Ej: $17.316.000"""
    return "$" + f"{int(valor):,}".replace(",", ".")

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Panadería",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estado del tema ───────────────────────────────────────────────────────────
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = False

DARK = st.session_state.tema_oscuro

# ── Tokens de diseño según tema ───────────────────────────────────────────────
if DARK:
    BG          = "#0F0A07"
    BG_CARD     = "#1C1209"
    BG_PLOT     = "#1C1209"
    BG_SIDEBAR  = "#0A0604"
    BORDER      = "#3D2810"
    TEXT_MAIN   = "#F5EDD8"
    TEXT_SUB    = "#C4A07A"
    TEXT_MUTED  = "#7A5C40"
    ACCENT      = "#E8943A"
    GRID        = "#2A1A0A"
    SHADOW      = "rgba(0,0,0,0.4)"
    HR_COLOR    = "#3D2810"
    SIDEBAR_TXT = "#F5EDD8"
    LEGEND_BG   = "#1C1209"
    HEATMAP_0   = "#1C1209"
    HEATMAP_1   = "#4A2810"
    HEATMAP_2   = "#C17B3A"
    HEATMAP_3   = "#F5A84A"
    TREEMAP_SCALE = ["#1C1209", "#4A2810", "#C17B3A", "#F5A84A"]
    BTN_TEMA_LABEL = "☀️  Tema Claro"
else:
    BG          = "#FAF7F2"
    BG_CARD     = "#FFFFFF"
    BG_PLOT     = "#FAF7F2"
    BG_SIDEBAR  = "#2C1810"
    BORDER      = "#E8DDD0"
    TEXT_MAIN   = "#2C1810"
    TEXT_SUB    = "#4A2E1A"
    TEXT_MUTED  = "#9B8070"
    ACCENT      = "#8B5E3C"
    GRID        = "#EDE3D8"
    SHADOW      = "rgba(44,24,16,0.06)"
    HR_COLOR    = "#E8DDD0"
    SIDEBAR_TXT = "#F5EDD8"
    LEGEND_BG   = "#FFFFFF"
    HEATMAP_0   = "#FBF3E8"
    HEATMAP_1   = "#E8C49A"
    HEATMAP_2   = "#C17B3A"
    HEATMAP_3   = "#6B2010"
    TREEMAP_SCALE = ["#F5EDD8", "#C17B3A", "#8B3A2A", "#4A2E1A"]
    BTN_TEMA_LABEL = "🌙  Tema Oscuro"

PALETTE = [
    "#C17B3A", "#E8943A", "#4A7C59", "#2C7BB5",
    "#9B59B6", "#F0C040", "#5A8A6E", "#C0394B",
]

# ── CSS dinámico ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background-color: {BG};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR};
    }}
    [data-testid="stSidebar"] * {{
        color: {SIDEBAR_TXT} !important;
    }}
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {{
        background-color: {"#0A0604" if DARK else "#3D2318"};
        border-color: {"#5A3010" if DARK else "#8B5E3C"};
    }}

    /* Títulos */
    h1 {{
        font-family: 'DM Serif Display', serif !important;
        color: {TEXT_MAIN} !important;
        font-size: 2.4rem !important;
        letter-spacing: -0.5px;
    }}
    h2, h3 {{
        font-family: 'DM Serif Display', serif !important;
        color: {TEXT_SUB} !important;
    }}

    /* Tarjetas métricas */
    [data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 20px 24px !important;
        box-shadow: 0 2px 8px {SHADOW};
    }}
    [data-testid="stMetricLabel"] {{
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: {ACCENT} !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'DM Serif Display', serif !important;
        font-size: 2rem !important;
        color: {TEXT_MAIN} !important;
    }}

    /* Divisor */
    hr {{
        border-color: {HR_COLOR};
        margin: 8px 0 24px 0;
    }}

    /* Caption */
    .caption-text {{
        font-size: 0.78rem;
        color: {TEXT_MUTED};
        margin-top: -12px;
        margin-bottom: 16px;
    }}

    /* Expander */
    [data-testid="stExpander"] {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}
    [data-testid="stExpander"] summary {{
        color: {TEXT_MAIN} !important;
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        background-color: {BG_CARD};
    }}

    /* Texto general en main */
    .stMarkdown p, .stMarkdown li {{
        color: {TEXT_MAIN};
    }}
    .stCaption {{
        color: {TEXT_MUTED} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────────────────
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTK9uOQGUs1QH0D22EGHM0Rye-32NFJu1RhFO4_KZiqP4nX2PTxMzR9WRWblSyqMLogoYHNGx92IfSr"
    "/pub?output=csv"
)

@st.cache_data(ttl=600, show_spinner=False)
def cargar_datos(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")

    def limpiar_numero(serie: pd.Series) -> pd.Series:
        s = serie.astype(str).str.strip().str.replace(r"[\$\s]", "", regex=True)
        tiene_punto = s.str.contains(r"\.", regex=True)
        tiene_coma  = s.str.contains(r",",  regex=True)
        s = s.where(~(tiene_punto & ~tiene_coma),
                    s.str.replace(".", "", regex=False))
        s = s.str.replace(",", ".", regex=False)
        s = s.str.replace(r"[^\d.]", "", regex=True)
        return pd.to_numeric(s, errors="coerce")

    df["Precio Unitario"] = limpiar_numero(df["Precio Unitario"])
    df["Cantidad Vendida"] = limpiar_numero(df["Cantidad Vendida"])
    df["Total_Venta"]      = df["Precio Unitario"] * df["Cantidad Vendida"]
    df.dropna(subset=["Fecha", "Producto", "Total_Venta"], inplace=True)
    df.sort_values("Fecha", inplace=True)
    df.attrs["cargado_en"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    return df

try:
    with st.spinner("Cargando datos…"):
        df_raw = cargar_datos(CSV_URL)
except Exception as e:
    st.error(f"❌ No se pudo cargar el CSV.\n\n`{e}`")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥐 Panadería")
    st.markdown("---")

    productos_disponibles = sorted(df_raw["Producto"].unique())
    productos_sel = st.multiselect(
        "Filtrar por Producto",
        options=productos_disponibles,
        default=productos_disponibles,
        help="Seleccioná uno o más productos para filtrar el dashboard.",
    )

    st.markdown("---")

    fecha_min = df_raw["Fecha"].min().date()
    fecha_max = df_raw["Fecha"].max().date()
    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

    st.markdown("---")

    # Botón tema
    if st.button(BTN_TEMA_LABEL, use_container_width=True):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

    st.markdown("---")

    # Botón recarga
    if st.button("🔄  Actualizar datos", use_container_width=True,
                 help="Limpia el caché y vuelve a leer el CSV desde Google Sheets."):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    ultima_carga = df_raw.attrs.get("cargado_en", "—")
    st.caption(f"📅 Datos: {fecha_min} → {fecha_max}")
    st.caption(f"📦 {len(df_raw):,} registros cargados")
    st.caption(f"🕐 Última carga: {ultima_carga}")

# ── Filtrado ──────────────────────────────────────────────────────────────────
if not productos_sel:
    st.warning("⚠️ Seleccioná al menos un producto en el panel lateral.")
    st.stop()

df = df_raw[df_raw["Producto"].isin(productos_sel)].copy()

if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df = df[(df["Fecha"].dt.date >= fecha_inicio) & (df["Fecha"].dt.date <= fecha_fin)]

if df.empty:
    st.warning("Sin datos para la combinación de filtros seleccionada.")
    st.stop()

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown("# Dashboard Comercial — Gestión Panadería")
st.markdown(f'<p class="caption-text">Análisis de ventas · Enero–Mayo 2026</p>',
            unsafe_allow_html=True)
st.markdown("---")

# ── Métricas ──────────────────────────────────────────────────────────────────
venta_total    = df["Total_Venta"].sum()
cantidad_total = df["Cantidad Vendida"].sum()
promedio_ticket= df["Total_Venta"].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Total Ingreso",         fmt_ars(venta_total))
with col2:
    st.metric("📦 Cantidad Total Vendida", f"{cantidad_total:,.0f} uds.")
with col3:
    st.metric("🧾 Promedio por Ticket",   fmt_ars(promedio_ticket))

st.markdown("<br>", unsafe_allow_html=True)

# ── Layout compartido para los gráficos ──────────────────────────────────────
LAYOUT_BASE = dict(
    plot_bgcolor  = BG_PLOT,
    paper_bgcolor = BG_PLOT,
    font_family   = "DM Sans",
    font_color    = TEXT_MAIN,
)

# ── Gráfico 1: Barras ─────────────────────────────────────────────────────────
st.markdown("### Total Ingreso por Producto")

ventas_producto = (
    df.groupby("Producto", as_index=False)["Total_Venta"]
    .sum().sort_values("Total_Venta", ascending=False)
)

# Etiqueta encima de cada barra con formato argentino (punto como miles)
ventas_producto["label_ars"] = ventas_producto["Total_Venta"].apply(fmt_ars)

fig_barras = px.bar(
    ventas_producto, x="Producto", y="Total_Venta",
    text="label_ars",          # etiqueta ya formateada
    color="Producto",
    color_discrete_sequence=PALETTE,
    custom_data=["label_ars"], # disponible como %{customdata[0]} por fila
)

fig_barras.update_traces(
    texttemplate="%{text}",
    textposition="outside",
    textfont=dict(size=13, color=TEXT_MAIN, family="DM Sans"),
    marker_line_width=0,
    width=0.55,
    # %{x} = nombre del producto (correcto por trace), %{customdata[0]} = label_ars
    hovertemplate=(
        "<b>Producto:</b> %{x}<br>"
        "<b>Total Ingreso:</b> %{customdata[0]}"
        "<extra></extra>"
    ),
)
fig_barras.update_layout(
    **LAYOUT_BASE,
    showlegend=False,
    xaxis=dict(title="", tickfont=dict(size=13, color=TEXT_MAIN), gridcolor="rgba(0,0,0,0)", tickangle=0),
    yaxis=dict(title="Total Ingreso ($)", tickformat="$,.0f", tickfont=dict(size=12, color=TEXT_MAIN),
               gridcolor=GRID, gridwidth=1, zeroline=False),
    margin=dict(t=50, b=60, l=10, r=10),
    height=440,
    uniformtext=dict(minsize=11, mode="show"),
)
st.plotly_chart(fig_barras, use_container_width=True)

# ── Gráfico 2: Líneas ─────────────────────────────────────────────────────────
st.markdown("### Evolución de Total Ingreso en el Tiempo")

ventas_tiempo = df.groupby(["Fecha", "Producto"], as_index=False)["Total_Venta"].sum()
ventas_tiempo["Fecha_str"]   = ventas_tiempo["Fecha"].dt.strftime("%d/%m/%Y")
ventas_tiempo["Ingreso_str"] = ventas_tiempo["Total_Venta"].apply(fmt_ars)

# custom_data como lista de columnas → px.line hace el slice por trace automáticamente
fig_lineas = px.line(
    ventas_tiempo, x="Fecha", y="Total_Venta",
    color="Producto", color_discrete_sequence=PALETTE,
    line_shape="spline", markers=True,
    custom_data=["Producto", "Fecha_str", "Ingreso_str"],
)
fig_lineas.update_traces(
    marker=dict(size=5, line=dict(width=1.5, color=BG_PLOT)),
    line=dict(width=2.5),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Fecha: %{customdata[1]}<br>"
        "Total Ingreso: %{customdata[2]}"
        "<extra></extra>"
    ),
)
fig_lineas.update_layout(
    **LAYOUT_BASE,
    legend=dict(
        title=dict(text="Producto", font=dict(size=13, color=TEXT_MAIN, family="DM Sans")),
        bgcolor=LEGEND_BG,
        bordercolor=ACCENT,
        borderwidth=1.5,
        font=dict(size=12, color=TEXT_MAIN, family="DM Sans"),
        x=1.01, xanchor="left", y=1, yanchor="top",
    ),
    xaxis=dict(title="", tickformat="%d/%m/%Y", tickfont=dict(size=12, color=TEXT_MAIN),
               gridcolor=GRID, gridwidth=1),
    yaxis=dict(title="Total Ingreso ($)", tickformat="$,.0f", tickfont=dict(size=12, color=TEXT_MAIN),
               gridcolor=GRID, gridwidth=1, zeroline=False),
    margin=dict(t=20, b=10, l=10, r=160),
    height=420,
    hovermode="closest",
)
st.plotly_chart(fig_lineas, use_container_width=True)

# ── Gráfico 3: Treemap ────────────────────────────────────────────────────────
st.markdown("### Participación de Ventas por Producto")

ventas_treemap = (
    df.groupby("Producto", as_index=False)["Total_Venta"].sum()
    .assign(Porcentaje=lambda d: (d["Total_Venta"] / d["Total_Venta"].sum() * 100).round(1))
)

fig_treemap = px.treemap(
    ventas_treemap, path=["Producto"], values="Total_Venta",
    color="Total_Venta",
    color_continuous_scale=TREEMAP_SCALE,
    custom_data=["Porcentaje"],
)
fig_treemap.update_traces(
    texttemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{customdata[0]:.1f}%",
    textfont=dict(family="DM Sans", size=14),
    marker=dict(line=dict(width=2, color=BG_PLOT)),
    hovertemplate="<b>%{label}</b><br>Total Ingreso: $%{value:,.0f}<br>Participación: %{customdata[0]:.1f}%<extra></extra>",
)
fig_treemap.update_layout(
    **LAYOUT_BASE,
    coloraxis_showscale=False,
    margin=dict(t=10, b=10, l=10, r=10),
    height=400,
)
st.plotly_chart(fig_treemap, use_container_width=True)

# ── Gráfico 4: Heatmap Pivot Mensual ─────────────────────────────────────────
st.markdown("### Ventas Mensuales por Producto")

df_pivot = df.copy()
df_pivot["Mes"] = df_pivot["Fecha"].dt.to_period("M").astype(str)

pivot = (
    df_pivot.groupby(["Producto", "Mes"])["Total_Venta"]
    .sum().unstack(fill_value=0).astype(int)
)
pivot.columns.name = None
pivot.index.name   = "Producto"
pivot["TOTAL"]     = pivot.sum(axis=1)
pivot              = pivot.sort_values("TOTAL", ascending=False)

meses_map = {
    "2026-01": "Enero", "2026-02": "Febrero", "2026-03": "Marzo",
    "2026-04": "Abril",  "2026-05": "Mayo",
}
pivot.columns = [meses_map.get(c, c) for c in pivot.columns]

meses_cols = [c for c in pivot.columns if c != "TOTAL"]
z_values   = pivot[meses_cols].values

fig_heatmap = go.Figure()
fig_heatmap.add_trace(go.Heatmap(
    z=z_values, x=meses_cols, y=pivot.index.tolist(),
    colorscale=[
        [0.0, HEATMAP_0], [0.3, HEATMAP_1],
        [0.6, HEATMAP_2], [1.0, HEATMAP_3],
    ],
    showscale=True,
    colorbar=dict(
        title=dict(text="$ Ventas", font=dict(size=11, family="DM Sans", color=TEXT_MAIN)),
        tickformat="$,.0f", tickfont=dict(color=TEXT_MAIN),
        thickness=14, len=0.85,
    ),
    hovertemplate="<b>%{y}</b> — %{x}<br>Venta: $%{z:,.0f}<extra></extra>",
    text=[[f"${v:,.0f}" for v in row] for row in z_values],
    texttemplate="%{text}",
    textfont=dict(family="DM Sans", size=12, color=TEXT_MAIN),
))

for prod, total in zip(pivot.index, pivot["TOTAL"].values):
    fig_heatmap.add_annotation(
        x=len(meses_cols) - 0.5 + 0.75, y=prod,
        text=f"<b>${total:,.0f}</b>",
        showarrow=False,
        font=dict(size=12, family="DM Sans", color=TEXT_MAIN),
        xref="x", yref="y",
    )

fig_heatmap.add_shape(
    type="line",
    x0=len(meses_cols) - 0.5 + 0.25, x1=len(meses_cols) - 0.5 + 0.25,
    y0=-0.5, y1=len(pivot) - 0.5,
    line=dict(color=ACCENT, width=2, dash="dot"),
)

fig_heatmap.update_layout(
    **LAYOUT_BASE,
    xaxis=dict(title="", side="top",
               tickfont=dict(size=13, color=TEXT_MAIN), gridcolor="rgba(0,0,0,0)"),
    yaxis=dict(title="", tickfont=dict(size=13, color=TEXT_MAIN),
               autorange="reversed", gridcolor="rgba(0,0,0,0)"),
    margin=dict(t=40, b=20, l=10, r=80),
    height=320,
)

st.plotly_chart(fig_heatmap, use_container_width=True)
st.caption("💡 El color más oscuro indica mayor volumen de ventas en ese mes. La columna derecha muestra el total acumulado del período.")

# ── Tabla de detalle ──────────────────────────────────────────────────────────
with st.expander("📋 Ver tabla de datos filtrados"):
    df_display = df.copy()
    df_display["Fecha"]          = df_display["Fecha"].dt.strftime("%d/%m/%Y")
    df_display["Precio Unitario"]= df_display["Precio Unitario"].apply(lambda x: f"${x:,.0f}")
    df_display["Total_Venta"]    = df_display["Total_Venta"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(
        df_display[["Fecha", "Producto", "Precio Unitario", "Cantidad Vendida", "Total_Venta"]],
        use_container_width=True, hide_index=True,
    )
    st.caption(f"{len(df):,} registros mostrados")
