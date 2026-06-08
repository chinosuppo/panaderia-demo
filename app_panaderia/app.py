import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Panadería",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos CSS personalizados ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Fondo general */
    .stApp {
        background-color: #FAF7F2;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2C1810;
    }
    [data-testid="stSidebar"] * {
        color: #F5EDD8 !important;
    }
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
        background-color: #3D2318;
        border-color: #8B5E3C;
    }

    /* Título principal */
    h1 {
        font-family: 'DM Serif Display', serif !important;
        color: #2C1810 !important;
        font-size: 2.4rem !important;
        letter-spacing: -0.5px;
    }

    /* Subtítulos */
    h2, h3 {
        font-family: 'DM Serif Display', serif !important;
        color: #4A2E1A !important;
    }

    /* Tarjetas de métricas */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8DDD0;
        border-radius: 12px;
        padding: 20px 24px !important;
        box-shadow: 0 2px 8px rgba(44, 24, 16, 0.06);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: #8B5E3C !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'DM Serif Display', serif !important;
        font-size: 2rem !important;
        color: #2C1810 !important;
    }

    /* Divisor */
    hr {
        border-color: #E8DDD0;
        margin: 8px 0 24px 0;
    }

    /* Texto pequeño */
    .caption-text {
        font-size: 0.78rem;
        color: #9B8070;
        margin-top: -12px;
        margin-bottom: 16px;
    }
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
    """Carga y pre-procesa el CSV desde Google Sheets."""
    df = pd.read_csv(url)

    # Normalizar nombres de columnas (quitar espacios extra)
    df.columns = df.columns.str.strip()

    # Conversión de fecha
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")

    # Limpiar columnas numéricas por si vienen con formato raro
    df["Precio Unitario"] = (
        df["Precio Unitario"].astype(str).str.replace(r"[^\d.]", "", regex=True)
    )
    df["Cantidad Vendida"] = (
        df["Cantidad Vendida"].astype(str).str.replace(r"[^\d.]", "", regex=True)
    )

    df["Precio Unitario"] = pd.to_numeric(df["Precio Unitario"], errors="coerce")
    df["Cantidad Vendida"] = pd.to_numeric(df["Cantidad Vendida"], errors="coerce")

    # Columna derivada
    df["Total_Venta"] = df["Precio Unitario"] * df["Cantidad Vendida"]

    # Eliminar filas con datos críticos faltantes
    df.dropna(subset=["Fecha", "Producto", "Total_Venta"], inplace=True)
    df.sort_values("Fecha", inplace=True)

    return df


# Cargar con manejo de errores
try:
    with st.spinner("Cargando datos…"):
        df_raw = cargar_datos(CSV_URL)
except Exception as e:
    st.error(f"❌ No se pudo cargar el CSV. Verificá la URL o tu conexión.\n\n`{e}`")
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

    # Rango de fechas
    fecha_min = df_raw["Fecha"].min().date()
    fecha_max = df_raw["Fecha"].max().date()
    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

    st.markdown("---")
    st.caption(f"📅 Datos: {fecha_min} → {fecha_max}")
    st.caption(f"📦 {len(df_raw):,} registros cargados")


# ── Filtrado ──────────────────────────────────────────────────────────────────
if not productos_sel:
    st.warning("⚠️ Seleccioná al menos un producto en el panel lateral.")
    st.stop()

# Aplicar filtro de productos
df = df_raw[df_raw["Producto"].isin(productos_sel)].copy()

# Aplicar filtro de fechas (manejar si el usuario seleccionó solo una fecha)
if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas
    df = df[(df["Fecha"].dt.date >= fecha_inicio) & (df["Fecha"].dt.date <= fecha_fin)]

if df.empty:
    st.warning("Sin datos para la combinación de filtros seleccionada.")
    st.stop()


# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown("# Dashboard Comercial — Gestión Panadería")
st.markdown('<p class="caption-text">Análisis de ventas · Enero–Mayo 2026</p>', unsafe_allow_html=True)
st.markdown("---")


# ── Métricas ──────────────────────────────────────────────────────────────────
venta_total = df["Total_Venta"].sum()
cantidad_total = df["Cantidad Vendida"].sum()
promedio_ticket = df["Total_Venta"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Venta Total",
        value=f"${venta_total:,.0f}",
    )
with col2:
    st.metric(
        label="📦 Cantidad Total Vendida",
        value=f"{cantidad_total:,.0f} uds.",
    )
with col3:
    st.metric(
        label="🧾 Promedio por Ticket",
        value=f"${promedio_ticket:,.0f}",
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Paleta de colores ─────────────────────────────────────────────────────────
PALETTE = [
    "#C17B3A", "#8B3A2A", "#4A7C59", "#2C5F8A",
    "#7A4E8B", "#C4A035", "#5A8A6E", "#A03A5A",
]


# ── Gráfico 1: Barras — Total de Venta por Producto ───────────────────────────
st.markdown("### Venta Total por Producto")

ventas_producto = (
    df.groupby("Producto", as_index=False)["Total_Venta"]
    .sum()
    .sort_values("Total_Venta", ascending=False)
)

fig_barras = px.bar(
    ventas_producto,
    x="Producto",
    y="Total_Venta",
    text="Total_Venta",
    color="Producto",
    color_discrete_sequence=PALETTE,
)

fig_barras.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    marker_line_width=0,
    width=0.55,
)

fig_barras.update_layout(
    plot_bgcolor="#FAF7F2",
    paper_bgcolor="#FAF7F2",
    font_family="DM Sans",
    font_color="#4A2E1A",
    showlegend=False,
    xaxis=dict(title="", tickfont_size=13, gridcolor="rgba(0,0,0,0)"),
    yaxis=dict(
        title="Venta Total ($)",
        tickformat="$,.0f",
        gridcolor="#EDE3D8",
        gridwidth=1,
        zeroline=False,
    ),
    margin=dict(t=20, b=10, l=10, r=10),
    height=400,
)

st.plotly_chart(fig_barras, use_container_width=True)


# ── Gráfico 2: Líneas — Evolución temporal de ventas ─────────────────────────
st.markdown("### Evolución de Ventas en el Tiempo")

ventas_tiempo = (
    df.groupby(["Fecha", "Producto"], as_index=False)["Total_Venta"].sum()
)

fig_lineas = px.line(
    ventas_tiempo,
    x="Fecha",
    y="Total_Venta",
    color="Producto",
    color_discrete_sequence=PALETTE,
    line_shape="spline",
    markers=True,
)

fig_lineas.update_traces(
    marker=dict(size=5, line=dict(width=1.5, color="white")),
    line=dict(width=2.5),
)

fig_lineas.update_layout(
    plot_bgcolor="#FAF7F2",
    paper_bgcolor="#FAF7F2",
    font_family="DM Sans",
    font_color="#4A2E1A",
    legend=dict(
        title="Producto",
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#E8DDD0",
        borderwidth=1,
        font_size=12,
    ),
    xaxis=dict(
        title="",
        tickformat="%d %b",
        gridcolor="#EDE3D8",
        gridwidth=1,
    ),
    yaxis=dict(
        title="Venta Total ($)",
        tickformat="$,.0f",
        gridcolor="#EDE3D8",
        gridwidth=1,
        zeroline=False,
    ),
    margin=dict(t=20, b=10, l=10, r=10),
    height=420,
    hovermode="x unified",
)

st.plotly_chart(fig_lineas, use_container_width=True)


# ── Gráfico 3: Treemap — Participación por Producto ──────────────────────────
st.markdown("### Participación de Ventas por Producto")

ventas_treemap = (
    df.groupby("Producto", as_index=False)["Total_Venta"]
    .sum()
    .assign(
        Porcentaje=lambda d: (d["Total_Venta"] / d["Total_Venta"].sum() * 100).round(1),
        Label=lambda d: d["Producto"] + "<br>" + d["Porcentaje"].astype(str) + "%",
    )
)

fig_treemap = px.treemap(
    ventas_treemap,
    path=["Producto"],
    values="Total_Venta",
    color="Total_Venta",
    color_continuous_scale=[
        "#F5EDD8", "#C17B3A", "#8B3A2A", "#4A2E1A"
    ],
    custom_data=["Porcentaje"],
)

fig_treemap.update_traces(
    texttemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{customdata[0]:.1f}%",
    textfont=dict(family="DM Sans", size=14),
    marker=dict(line=dict(width=2, color="#FAF7F2")),
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Venta Total: $%{value:,.0f}<br>"
        "Participación: %{customdata[0]:.1f}%"
        "<extra></extra>"
    ),
)

fig_treemap.update_layout(
    paper_bgcolor="#FAF7F2",
    font_family="DM Sans",
    font_color="#2C1810",
    coloraxis_showscale=False,
    margin=dict(t=10, b=10, l=10, r=10),
    height=400,
)

st.plotly_chart(fig_treemap, use_container_width=True)


# ── Gráfico 4: Tabla Pivot Mensual ────────────────────────────────────────────
st.markdown("### Ventas Mensuales por Producto")

# Crear columna de mes
df_pivot = df.copy()
df_pivot["Mes"] = df_pivot["Fecha"].dt.to_period("M").astype(str)

# Tabla pivot: filas = Producto, columnas = Mes
pivot = (
    df_pivot.groupby(["Producto", "Mes"])["Total_Venta"]
    .sum()
    .unstack(fill_value=0)
    .astype(int)
)
pivot.columns.name = None
pivot.index.name = "Producto"

# Agregar columna de total
pivot["TOTAL"] = pivot.sum(axis=1)
pivot = pivot.sort_values("TOTAL", ascending=False)

# Nombres de meses más legibles
meses_map = {
    "2026-01": "Enero", "2026-02": "Febrero", "2026-03": "Marzo",
    "2026-04": "Abril", "2026-05": "Mayo",
}
pivot.columns = [meses_map.get(c, c) for c in pivot.columns]

# Heatmap con go.Heatmap para colorear la tabla
meses_cols = [c for c in pivot.columns if c != "TOTAL"]
z_values = pivot[meses_cols].values

fig_heatmap = go.Figure()

# Capa de calor
fig_heatmap.add_trace(go.Heatmap(
    z=z_values,
    x=meses_cols,
    y=pivot.index.tolist(),
    colorscale=[
        [0.0, "#FBF3E8"],
        [0.3, "#E8C49A"],
        [0.6, "#C17B3A"],
        [1.0, "#6B2010"],
    ],
    showscale=True,
    colorbar=dict(
        title=dict(text="$ Ventas", font=dict(size=11, family="DM Sans")),
        tickformat="$,.0f",
        thickness=14,
        len=0.85,
    ),
    hovertemplate="<b>%{y}</b> — %{x}<br>Venta: $%{z:,.0f}<extra></extra>",
    text=[[f"${v:,.0f}" for v in row] for row in z_values],
    texttemplate="%{text}",
    textfont=dict(family="DM Sans", size=12, color="#2C1810"),
))

# Columna TOTAL superpuesta como anotaciones
total_values = pivot["TOTAL"].values
for i, (prod, total) in enumerate(zip(pivot.index, total_values)):
    fig_heatmap.add_annotation(
        x=len(meses_cols) - 0.5 + 0.75,
        y=prod,
        text=f"<b>${total:,.0f}</b>",
        showarrow=False,
        font=dict(size=12, family="DM Sans", color="#2C1810"),
        xref="x",
        yref="y",
    )

# Línea vertical para separar el total (simulada con shape)
fig_heatmap.add_shape(
    type="line",
    x0=len(meses_cols) - 0.5 + 0.25,
    x1=len(meses_cols) - 0.5 + 0.25,
    y0=-0.5,
    y1=len(pivot) - 0.5,
    line=dict(color="#C17B3A", width=2, dash="dot"),
)

fig_heatmap.update_layout(
    plot_bgcolor="#FAF7F2",
    paper_bgcolor="#FAF7F2",
    font_family="DM Sans",
    font_color="#2C1810",
    xaxis=dict(
        title="",
        side="top",
        tickfont=dict(size=13, color="#4A2E1A"),
        gridcolor="rgba(0,0,0,0)",
    ),
    yaxis=dict(
        title="",
        tickfont=dict(size=13, color="#4A2E1A"),
        autorange="reversed",
        gridcolor="rgba(0,0,0,0)",
    ),
    margin=dict(t=40, b=20, l=10, r=80),
    height=320,
)

st.plotly_chart(fig_heatmap, use_container_width=True)
st.caption("💡 El color más oscuro indica mayor volumen de ventas en ese mes. La columna derecha muestra el total acumulado del período.")


# ── Tabla de detalle ──────────────────────────────────────────────────────────
with st.expander("📋 Ver tabla de datos filtrados"):
    df_display = df.copy()
    df_display["Fecha"] = df_display["Fecha"].dt.strftime("%d/%m/%Y")
    df_display["Precio Unitario"] = df_display["Precio Unitario"].apply(lambda x: f"${x:,.0f}")
    df_display["Total_Venta"] = df_display["Total_Venta"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(
        df_display[["Fecha", "Producto", "Precio Unitario", "Cantidad Vendida", "Total_Venta"]],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"{len(df):,} registros mostrados")