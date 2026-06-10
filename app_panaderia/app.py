import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_ars(valor: float) -> str:
    """$17.316.000 — separador de miles con punto, estilo argentino."""
    return "$" + f"{int(valor):,}".replace(",", ".")

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Panadería · Dashboard",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estado del tema ───────────────────────────────────────────────────────────
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = False

DARK = st.session_state.tema_oscuro

# ── Tokens de diseño ─────────────────────────────────────────────────────────
if DARK:
    BG           = "#0D0D0D"
    BG_CARD      = "#161616"
    BG_PLOT      = "#161616"
    BG_SIDEBAR   = "#111111"
    BORDER       = "#2A2A2A"
    TEXT_MAIN    = "#F0F0F0"
    TEXT_SUB     = "#A0A0A0"
    TEXT_MUTED   = "#555555"
    ACCENT       = "#E8943A"
    ACCENT2      = "#C17B3A"
    GRID         = "#222222"
    SHADOW       = "rgba(0,0,0,0.5)"
    LEGEND_BG    = "#161616"
    BANNER_BG    = "#1E1A14"
    BANNER_BORDER= "#3D2810"
    BANNER_TEXT  = "#E8C49A"
    HEATMAP      = ["#161616","#2A1A0A","#C17B3A","#F5A84A"]
    TREEMAP      = ["#1A1A1A","#2A1A0A","#C17B3A","#F5A84A"]
    BTN_TEMA     = "Modo claro"
else:
    BG           = "#F8F9FA"
    BG_CARD      = "#FFFFFF"
    BG_PLOT      = "#FFFFFF"
    BG_SIDEBAR   = "#111111"
    BORDER       = "#E5E7EB"
    TEXT_MAIN    = "#111827"
    TEXT_SUB     = "#6B7280"
    TEXT_MUTED   = "#9CA3AF"
    ACCENT       = "#D97706"
    ACCENT2      = "#92400E"
    GRID         = "#F3F4F6"
    SHADOW       = "rgba(0,0,0,0.06)"
    LEGEND_BG    = "#FFFFFF"
    BANNER_BG    = "#FFFBEB"
    BANNER_BORDER= "#FDE68A"
    BANNER_TEXT  = "#92400E"
    HEATMAP      = ["#F9FAFB","#FEF3C7","#F59E0B","#92400E"]
    TREEMAP      = ["#F9FAFB","#FEF3C7","#F59E0B","#92400E"]
    BTN_TEMA     = "Modo oscuro"

PALETTE = ["#F59E0B","#EF4444","#10B981","#3B82F6","#8B5CF6","#EC4899"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"], .stMarkdown, p, span, label {{
    font-family: 'Inter', sans-serif !important;
  }}

  .stApp {{ background-color: {BG}; }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid #1F1F1F;
  }}
  [data-testid="stSidebar"] * {{ color: #E5E7EB !important; }}
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: #2A2A2A !important;
    border: 1px solid #444 !important;
    border-radius: 4px !important;
  }}
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {{
    color: #D1D5DB !important;
    font-size: 0.78rem !important;
  }}
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {{
    background-color: #1A1A1A !important;
    border-color: #333 !important;
  }}
  [data-testid="stSidebar"] .stButton button {{
    background-color: #1A1A1A;
    border: 1px solid #333;
    color: #E5E7EB !important;
    font-size: 0.82rem;
    font-weight: 500;
    border-radius: 6px;
    transition: background 0.15s;
  }}
  [data-testid="stSidebar"] .stButton button:hover {{
    background-color: #252525 !important;
    border-color: #555 !important;
  }}

  /* ── Cabecera ── */
  h1 {{
    font-family: 'Inter', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: {TEXT_MAIN} !important;
    margin-bottom: 2px !important;
    line-height: 1.2 !important;
  }}
  h2, h3 {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: {TEXT_MAIN} !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.01em !important;
    margin-top: 0 !important;
  }}

  /* ── Métricas ── */
  [data-testid="stMetric"] {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 16px !important;
    box-shadow: 0 1px 3px {SHADOW};
  }}
  [data-testid="stMetricLabel"] {{
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: {TEXT_SUB} !important;
  }}
  [data-testid="stMetricValue"] {{
    font-family: 'Inter', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: {TEXT_MAIN} !important;
    letter-spacing: -0.02em !important;
  }}
  [data-testid="stMetricDelta"] {{
    font-size: 0.75rem !important;
    font-weight: 500 !important;
  }}

  /* ── Divisor ── */
  hr {{ border-color: {BORDER}; margin: 4px 0 16px 0; }}

  /* ── Banner de insight ── */
  .insight-banner {{
    background: {BANNER_BG};
    border: 1px solid {BANNER_BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 0.82rem;
    font-weight: 500;
    color: {BANNER_TEXT};
    font-family: 'Inter', sans-serif;
    line-height: 1.5;
  }}

  /* ── Expander ── */
  [data-testid="stExpander"] {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
  }}
  [data-testid="stExpander"] summary, [data-testid="stExpander"] p {{
    color: {TEXT_MAIN} !important;
  }}

  .stCaption {{ color: {TEXT_MUTED} !important; font-size: 0.72rem !important; }}
  .stMarkdown p {{ color: {TEXT_SUB}; font-size: 0.88rem; }}

  /* ── Ocultar botón nativo del sidebar (texto Material Icons roto) ────────── */
  [data-testid="stSidebarCollapseButton"],
  [data-testid="collapsedControl"],
  [data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
  }}



  /* expander eliminado — se usa botón nativo sin íconos problemáticos */



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

    def limpiar_numero(s: pd.Series) -> pd.Series:
        s = s.astype(str).str.strip().str.replace(r"[\$\s]", "", regex=True)
        tiene_punto = s.str.contains(r"\.", regex=True)
        tiene_coma  = s.str.contains(r",",  regex=True)
        s = s.where(~(tiene_punto & ~tiene_coma), s.str.replace(".", "", regex=False))
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
    with st.spinner(""):
        df_raw = cargar_datos(CSV_URL)
except Exception as e:
    st.error(f"❌ No se pudo cargar el CSV.\n\n`{e}`")
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='font-size:1.1rem;font-weight:700;color:#F9FAFB;"
        f"letter-spacing:-0.02em;padding:4px 0 12px 0;'>🥐 Panadería</div>",
        unsafe_allow_html=True
    )

    productos_disponibles = sorted(df_raw["Producto"].unique())
    productos_sel = st.multiselect(
        "Productos",
        options=productos_disponibles,
        default=productos_disponibles,
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    fecha_min = df_raw["Fecha"].min().date()
    fecha_max = df_raw["Fecha"].max().date()
    st.markdown(
        "<div style='font-size:0.75rem;font-weight:600;color:#9CA3AF;"
        "letter-spacing:0.04em;text-transform:uppercase;margin-bottom:4px;'>"
        "Período</div>",
        unsafe_allow_html=True,
    )
    rango_fechas = st.date_input(
        "Período",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        format="DD/MM/YYYY",
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button(BTN_TEMA, use_container_width=True):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button("Actualizar datos", use_container_width=True,
                 help="Limpia el caché y vuelve a leer el CSV."):
        st.cache_data.clear()
        st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    ultima_carga = df_raw.attrs.get("cargado_en", "—")
    st.caption(f"Datos: {fecha_min.strftime('%d/%m/%Y')} → {fecha_max.strftime('%d/%m/%Y')}")
    st.caption(f"Registros: {len(df_raw):,}   ·   Última carga: {ultima_carga}")

# ── Filtrado ──────────────────────────────────────────────────────────────────
if not productos_sel:
    st.warning("Seleccioná al menos un producto.")
    st.stop()

df = df_raw[df_raw["Producto"].isin(productos_sel)].copy()

if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
    fi, ff = rango_fechas
    df = df[(df["Fecha"].dt.date >= fi) & (df["Fecha"].dt.date <= ff)]

if df.empty:
    st.warning("Sin datos para los filtros seleccionados.")
    st.stop()

# ── Cálculos de insights ──────────────────────────────────────────────────────
df["Mes"]    = df["Fecha"].dt.to_period("M")
df["Semana"] = df["Fecha"].dt.to_period("W")

por_mes      = df.groupby("Mes")["Total_Venta"].sum()
por_producto = df.groupby("Producto")["Total_Venta"].sum().sort_values(ascending=False)

mejor_mes    = por_mes.idxmax()
peor_mes     = por_mes.idxmin()
top_producto = por_producto.index[0]
bot_producto = por_producto.index[-1]

MESES_ES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",
            6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",
            10:"Octubre",11:"Noviembre",12:"Diciembre"}

mejor_mes_str = MESES_ES[mejor_mes.month]
peor_mes_str  = MESES_ES[peor_mes.month]

venta_total     = df["Total_Venta"].sum()
cantidad_total  = df["Cantidad Vendida"].sum()
promedio_ticket = df["Total_Venta"].mean()

# Variación mes a mes (últimos dos meses con datos)
meses_ord = por_mes.sort_index()
if len(meses_ord) >= 2:
    delta_pct = (meses_ord.iloc[-1] - meses_ord.iloc[-2]) / meses_ord.iloc[-2] * 100
    delta_label = f"{delta_pct:+.1f}% vs mes anterior"
else:
    delta_label = None

LAYOUT_BASE = dict(
    plot_bgcolor  = BG_PLOT,
    paper_bgcolor = BG_PLOT,
    font_family   = "Inter",
    font_color    = TEXT_MAIN,
)

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown("# Dashboard Comercial")
st.markdown(
    f"<p style='color:{TEXT_MUTED};font-size:0.82rem;margin-top:-8px;margin-bottom:20px;'>"
    f"Panadería · Análisis de ventas</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Ingreso", fmt_ars(venta_total), delta=delta_label)
with c2:
    st.metric("Unidades Vendidas", f"{int(cantidad_total):,}".replace(",","."))
with c3:
    st.metric("Ticket Promedio", fmt_ars(promedio_ticket))

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1 — Barras: Total Ingreso por Producto
# ══════════════════════════════════════════════════════════════════════════════
top2 = por_producto.head(2)
insight_barras = (
    f"🏆 <b>{top_producto}</b> lidera con {fmt_ars(por_producto[top_producto])} "
    f"— {por_producto[top_producto]/venta_total*100:.1f}% del total. "
    f"<b>{bot_producto}</b> es el de menor ingreso con {fmt_ars(por_producto[bot_producto])}."
)
st.markdown(f"<div class='insight-banner'>{insight_barras}</div>", unsafe_allow_html=True)
st.markdown("### Total Ingreso por Producto")

vp = por_producto.reset_index()
vp.columns = ["Producto", "Total_Venta"]
vp["label_ars"] = vp["Total_Venta"].apply(fmt_ars)

fig_barras = px.bar(
    vp, x="Producto", y="Total_Venta",
    text="label_ars", color="Producto",
    color_discrete_sequence=PALETTE,
    custom_data=["label_ars"],
)
fig_barras.update_traces(
    texttemplate="%{text}",
    textposition="outside",
    textfont=dict(size=12, color=TEXT_MAIN, family="Inter"),
    marker_line_width=0,
    width=0.5,
    hovertemplate="<b>%{x}</b><br>Total Ingreso: %{customdata[0]}<extra></extra>",
)
fig_barras.update_layout(
    **LAYOUT_BASE,
    showlegend=False,
    xaxis=dict(title="", tickfont=dict(size=12, color=TEXT_SUB), gridcolor="rgba(0,0,0,0)", tickangle=0),
    yaxis=dict(title="", tickformat="$,.0f", tickfont=dict(size=11, color=TEXT_MUTED),
               gridcolor=GRID, gridwidth=1, zeroline=False, showticklabels=False),
    margin=dict(t=40, b=40, l=0, r=0),
    height=340,
    uniformtext=dict(minsize=10, mode="show"),
)
st.plotly_chart(fig_barras, use_container_width=True, config={"responsive": True})

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2 — Barras apiladas por semana
# ══════════════════════════════════════════════════════════════════════════════
df_sem = df.groupby(["Semana", "Producto"], as_index=False)["Total_Venta"].sum()

# Mapear cada período semanal a "Sem 1", "Sem 2", etc. (ordenado cronológicamente)
semanas_unicas = sorted(df_sem["Semana"].unique())
semana_a_label = {s: f"Sem {i+1}" for i, s in enumerate(semanas_unicas)}
df_sem["Semana_str"] = df_sem["Semana"].map(semana_a_label)
df_sem["Ingreso_str"] = df_sem["Total_Venta"].apply(fmt_ars)

semana_top    = df.groupby("Semana")["Total_Venta"].sum().idxmax()
semana_top_v  = df.groupby("Semana")["Total_Venta"].sum().max()
semana_top_str= semana_a_label[semana_top]  # "Sem N" en lugar del rango de fechas

insight_sem = (
    f"📅 La semana con mayor ingreso fue <b>{semana_top_str}</b> "
    f"con {fmt_ars(semana_top_v)}. "
    f"El mes más fuerte fue <b>{mejor_mes_str}</b> "
    f"({fmt_ars(por_mes[mejor_mes])}) y el más débil <b>{peor_mes_str}</b> "
    f"({fmt_ars(por_mes[peor_mes])})."
)
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='insight-banner'>{insight_sem}</div>", unsafe_allow_html=True)
st.markdown("### Ingreso Semanal por Producto")

fig_sem = px.bar(
    df_sem, x="Semana_str", y="Total_Venta",
    color="Producto", color_discrete_sequence=PALETTE,
    custom_data=["Producto","Ingreso_str"],
    barmode="stack",
)
fig_sem.update_traces(
    hovertemplate="<b>%{customdata[0]}</b><br>Semana: %{x}<br>Ingreso: %{customdata[1]}<extra></extra>",
    marker_line_width=0,
)
fig_sem.update_layout(
    **LAYOUT_BASE,
    legend=dict(
        title=None,
        bgcolor=LEGEND_BG, bordercolor=BORDER, borderwidth=1,
        font=dict(size=10, color=TEXT_SUB),
        orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
        itemwidth=40,
    ),
    xaxis=dict(title="", tickfont=dict(size=10, color=TEXT_MUTED),
               gridcolor="rgba(0,0,0,0)", tickangle=-35),
    yaxis=dict(title="", tickformat="$,.0f", tickfont=dict(size=11, color=TEXT_MUTED),
               gridcolor=GRID, gridwidth=1, zeroline=False),
    margin=dict(t=40, b=50, l=0, r=0),
    height=340,
    hovermode="closest",
)
st.plotly_chart(fig_sem, use_container_width=True, config={"responsive": True})

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3 — Treemap: Participación
# ══════════════════════════════════════════════════════════════════════════════
vt = por_producto.reset_index()
vt.columns = ["Producto","Total_Venta"]
vt["Porcentaje"] = (vt["Total_Venta"] / vt["Total_Venta"].sum() * 100).round(1)
top1_pct = vt.loc[vt["Total_Venta"].idxmax(), "Porcentaje"]
top2_sum  = vt.nlargest(2,"Total_Venta")["Porcentaje"].sum()

insight_tree = (
    f"🍰 <b>{top_producto}</b> concentra el <b>{top1_pct:.1f}%</b> del ingreso total. "
    f"Los dos productos líderes suman el <b>{top2_sum:.1f}%</b>."
)
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='insight-banner'>{insight_tree}</div>", unsafe_allow_html=True)
st.markdown("### Participación por Producto")

fig_treemap = px.treemap(
    vt, path=["Producto"], values="Total_Venta",
    color="Total_Venta", color_continuous_scale=TREEMAP,
    custom_data=["Porcentaje"],
)
fig_treemap.update_traces(
    texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}%",
    textfont=dict(family="Inter", size=14),
    marker=dict(line=dict(width=2, color=BG)),
    hovertemplate="<b>%{label}</b><br>Ingreso: $%{value:,.0f}<br>Participación: %{customdata[0]:.1f}%<extra></extra>",
)
fig_treemap.update_layout(
    **LAYOUT_BASE, coloraxis_showscale=False,
    margin=dict(t=8, b=8, l=8, r=8), height=300,
)
st.plotly_chart(fig_treemap, use_container_width=True, config={"responsive": True})

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 4 — Heatmap Mensual
# ══════════════════════════════════════════════════════════════════════════════
df_piv = df.copy()
df_piv["MesStr"] = df_piv["Fecha"].dt.to_period("M").astype(str)

pivot = (
    df_piv.groupby(["Producto","MesStr"])["Total_Venta"]
    .sum().unstack(fill_value=0).astype(int)
)
pivot.columns.name = None
pivot.index.name   = "Producto"
pivot["TOTAL"]     = pivot.sum(axis=1)
pivot              = pivot.sort_values("TOTAL", ascending=False)

MESES_MAP = {"2026-01":"Ene","2026-02":"Feb","2026-03":"Mar","2026-04":"Abr","2026-05":"May"}
pivot.columns = [MESES_MAP.get(c, c) for c in pivot.columns]

mes_cols   = [c for c in pivot.columns if c != "TOTAL"]
z_vals     = pivot[mes_cols].values

# Insight: producto con mayor crecimiento mes a mes
if len(mes_cols) >= 2:
    crec = pivot[mes_cols[-1]] - pivot[mes_cols[-2]]
    prod_crec  = crec.idxmax()
    prod_caida = crec.idxmin()
    insight_heat = (
        f"📈 En el último mes <b>{prod_crec}</b> fue el producto con mayor crecimiento "
        f"({fmt_ars(crec[prod_crec])}). "
        f"<b>{prod_caida}</b> tuvo la mayor caída ({fmt_ars(crec[prod_caida])})."
    )
else:
    insight_heat = "📊 Seleccioná un rango más amplio para ver variaciones mensuales."

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='insight-banner'>{insight_heat}</div>", unsafe_allow_html=True)
st.markdown("### Ingresos Mensuales por Producto")

fig_heat = go.Figure()
fig_heat.add_trace(go.Heatmap(
    z=z_vals, x=mes_cols, y=pivot.index.tolist(),
    colorscale=[[0,HEATMAP[0]],[0.3,HEATMAP[1]],[0.65,HEATMAP[2]],[1,HEATMAP[3]]],
    showscale=True,
    colorbar=dict(
        tickformat="$,.0f", tickfont=dict(color=TEXT_SUB, size=10),
        thickness=12, len=0.8,
        title=dict(text="", font=dict(size=10)),
    ),
    hovertemplate="<b>%{y}</b> · %{x}<br>Ingreso: $%{z:,.0f}<extra></extra>",
    text=[[fmt_ars(v) for v in row] for row in z_vals],
    texttemplate="%{text}",
    textfont=dict(family="Inter", size=11, color=TEXT_MAIN),
))

for prod, total in zip(pivot.index, pivot["TOTAL"].values):
    fig_heat.add_annotation(
        x=len(mes_cols) - 0.5 + 0.72, y=prod,
        text=f"<b>{fmt_ars(total)}</b>",
        showarrow=False,
        font=dict(size=11, family="Inter", color=TEXT_MAIN),
        xref="x", yref="y",
    )

fig_heat.add_shape(
    type="line",
    x0=len(mes_cols)-0.5+0.22, x1=len(mes_cols)-0.5+0.22,
    y0=-0.5, y1=len(pivot)-0.5,
    line=dict(color=ACCENT, width=1.5, dash="dot"),
)

fig_heat.update_layout(
    **LAYOUT_BASE,
    xaxis=dict(title="", side="top", tickfont=dict(size=12, color=TEXT_SUB), gridcolor="rgba(0,0,0,0)"),
    yaxis=dict(title="", tickfont=dict(size=12, color=TEXT_SUB), autorange="reversed", gridcolor="rgba(0,0,0,0)"),
    margin=dict(t=36, b=16, l=8, r=90),
    height=280,
)
st.plotly_chart(fig_heat, use_container_width=True, config={"responsive": True})
st.caption("El color más oscuro = mayor ingreso. La columna derecha es el acumulado del período.")

# ── Tabla detalle ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

if "mostrar_tabla" not in st.session_state:
    st.session_state.mostrar_tabla = False

lbl_tabla = "Ocultar registros" if st.session_state.mostrar_tabla else "Ver registros"
if st.button(lbl_tabla, use_container_width=False):
    st.session_state.mostrar_tabla = not st.session_state.mostrar_tabla
    st.rerun()

if st.session_state.mostrar_tabla:
    dd = df.copy()
    dd["Fecha"]           = dd["Fecha"].dt.strftime("%d/%m/%Y")
    dd["Precio Unitario"] = dd["Precio Unitario"].apply(lambda x: fmt_ars(x))
    dd["Total_Venta"]     = dd["Total_Venta"].apply(lambda x: fmt_ars(x))
    st.dataframe(
        dd[["Fecha","Producto","Precio Unitario","Cantidad Vendida","Total_Venta"]],
        use_container_width=True, hide_index=True,
    )
    st.caption(f"{len(df):,} registros")
