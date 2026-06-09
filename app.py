import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="Laboratorio de Políticas Públicas", layout="wide")

st.title("🏛️ Laboratorio Virtual: Políticas Públicas en Economía Cerrada")
st.markdown("**UNSTA - Ingeniería Informática | Asignatura: Economía**")
st.markdown("**Integrantes:** Yamil Beddur, Risso Mattia, Rodriguez Areal Oscar, Vechetti Ignacio")

# --- MOTOR DE CÁLCULO CORE ---
def calcular_mercado(a, b, c, d, politica="Libre", valor=0.0):
    # Equilibrio Inicial
    P_eq = (a - c) / (b + d)
    Q_eq = a - b * P_eq
    
    # Excedentes Iniciales
    P_max_demanda = a / b
    P_min_oferta = -c / d if d != 0 else 0
    
    EC_ini = 0.5 * (P_max_demanda - P_eq) * Q_eq
    EP_ini = 0.5 * (P_eq - P_min_oferta) * Q_eq
    BT_ini = EC_ini + EP_ini
    
    # Inicialización de variables post-intervención
    P_pago, P_recibe, Q_int = P_eq, P_eq, Q_eq
    EC_post, EP_post, gasto, escasez = EC_ini, EP_ini, 0.0, 0.0
    
    if politica == "Subsidio":
        s = valor
        # Qo = c + d(P_d + s) => c + dP_d + ds = a - bP_d => P_d(b+d) = a - c - ds
        P_pago = (a - c - d * s) / (b + d)
        P_recibe = P_pago + s
        Q_int = a - b * P_pago
        
        EC_post = 0.5 * (P_max_demanda - P_pago) * Q_int
        EP_post = 0.5 * (P_recibe - P_min_oferta) * Q_int
        gasto = s * Q_int
        
    elif politica == "Precio Máximo":
        P_max_legal = valor
        if P_max_legal < P_eq:
            P_pago = P_max_legal
            P_recibe = P_max_legal
            Q_d = a - b * P_max_legal
            Q_o = c + d * P_max_legal
            escasez = Q_d - Q_o
            Q_int = Q_o # Domina el lado corto del mercado
            
            # Precio de reserva para la cantidad racionada
            P_reserva = (a - Q_int) / b
            EC_post = 0.5 * (P_max_demanda - P_reserva) * Q_int + (P_reserva - P_max_legal) * Q_int
            EP_post = 0.5 * (P_max_legal - P_min_oferta) * Q_int
            gasto = 0.0
            
    BT_post = EC_post + EP_post - gasto
    delta_bienestar = BT_post - BT_ini
    
    return {
        "P_eq": P_eq, "Q_eq": Q_eq, "EC_ini": EC_ini, "EP_ini": EP_ini, "BT_ini": BT_ini,
        "P_pago": P_pago, "P_recibe": P_recibe, "Q_int": Q_int, "EC_post": EC_post,
        "EP_post": EP_post, "gasto": gasto, "escasez": escasez, "BT_post": BT_post, "delta_bienestar": delta_bienestar
    }

# --- PESTAÑAS DE EXERCICIOS ---
tab1, tab2 = st.tabs(["🚌 Ejercicio 1: Subsidio al Transporte", "🏢 Ejercicio 2: Alquileres Urbanos"])

# --- EJERCICIO 1 ---
with tab1:
    st.header("Análisis de Subsidio Estatal Colectivo")
    st.markdown("Ecuaciones asignadas: $Q_d = 1500 - 25P_d \\quad | \\quad Q_o = 15P_o$")
    
    s_input = st.slider("Ajustar subsidio unitario (s):", 0, 25, 8, step=1)
    res1 = calcular_mercado(1500.0, 25.0, 0.0, 15.0, "Subsidio", float(s_input))
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📋 Métricas del Escenario")
        st.metric("Precio de Equilibrio Inicial", f"${res1['P_eq']:.2f}")
        st.metric("Cantidad Inicial Transada", f"{res1['Q_eq']:.1f} viajes")
        st.write(f"📉 **Precio pagado por usuarios:** ${res1['P_pago']:.2f}")
        st.write(f"📈 **Precio recibido por empresas:** ${res1['P_recibe']:.2f}")
        st.write(f"🔄 **Nueva Cantidad de Equilibrio:** {res1['Q_int']:.1f} u.")
        st.error(f"🏛️ **Gasto Público del Gobierno:** ${res1['gasto']:.2f}")
        st.warning(f"📉 **Impacto Social (Δ Welfare):** ${res1['delta_bienestar']:.2f}")
        
    with col2:
        # Gráfico Ex 1
        p_space = np.linspace(0, 65, 100)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=1500 - 25*p_space, y=p_space, name='Demanda', line=dict(color='teal', width=3)))
        fig1.add_trace(go.Scatter(x=15*p_space, y=p_space, name='Oferta Original', line=dict(color='orange', width=2)))
        if s_input > 0:
            fig1.add_trace(go.Scatter(x=15*(p_space + s_input), y=p_space, name='Oferta Subsidiada', line=dict(color='green', dash='dash')))
            fig1.add_trace(go.Scatter(x=[res1['Q_int']], y=[res1['P_pago']], mode='markers', name='Punto Consumidor', marker=dict(color='blue', size=10)))
            fig1.add_trace(go.Scatter(x=[res1['Q_int']], y=[res1['P_recibe']], mode='markers', name='Punto Productor', marker=dict(color='darkgreen', size=10)))
        fig1.update_layout(template="plotly_white", title="Efecto del Subsidio en el Transporte", xaxis_title="Cantidad de Viajes", yaxis_title="Precio por Viaje")
        st.plotly_chart(fig1, use_container_width=True)
        
    st.subheader("📊 Simulación de Escenarios Obligatorios")
    subsidios_sim = [0, 5, 10, 15, 20]
    tabla1_data = []
    for s in subsidios_sim:
        r = calcular_mercado(1500.0, 25.0, 0.0, 15.0, "Subsidio", float(s))
        tabla1_data.append({"Subsidio ($)": s, "Cantidad Equilibrio": round(r['Q_int'], 2), "Gasto Público ($)": round(r['gasto'], 2), "Bienestar Total ($)": round(r['BT_post'], 2)})
    df1 = pd.DataFrame(tabla1_data)
    st.dataframe(df1, use_container_width=True)

# --- EJERCICIO 2 ---
with tab2:
    st.header("Regulación de Alquileres de Vivienda")
    st.markdown("Ecuaciones asignadas: $Q_d = 1800 - 20P \\quad | \\quad Q_o = 12P$")
    
    pmax_input = st.slider("Ajustar Precio Máximo Legal (Pmax):", 20, 80, 40, step=5)
    res2 = calcular_mercado(1800.0, 20.0, 0.0, 12.0, "Precio Máximo", float(pmax_input))
    
    col3, col4 = st.columns([1, 2])
    with col3:
        st.subheader("📋 Métricas del Escenario")
        st.metric("Precio Natural Vaciado", f"${res2['P_eq']:.2f}")
        st.metric("Cantidad Natural Vaciado", f"{res2['Q_eq']:.1f} viviendas")
        
        if pmax_input < res2['P_eq']:
            st.error(f"⚠️ **ESCASEZ DETECTADA:** {res2['escasez']:.1f} unidades")
            st.caption(f"Cantidad Demandada: {1800.0 - 20.0*pmax_input:.1f} | Cantidad Ofrecida: {12.0*pmax_input:.1f}")
        else:
            st.success("Regulación inofensiva: Límite sobre el equilibrio.")
            
        st.write(f"📉 **Pérdida de Eficiencia Social (PES):** ${abs(res2['delta_bienestar']):.2f}")
        
    with col4:
        # Gráfico Ex 2
        p_space2 = np.linspace(0, 100, 100)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=1800 - 20*p_space2, y=p_space2, name='Demanda', line=dict(color='teal', width=3)))
        fig2.add_trace(go.Scatter(x=12*p_space2, y=p_space2, name='Oferta', line=dict(color='orange', width=3)))
        fig2.add_hline(y=pmax_input, line_dash="dash", line_color="red", annotation_text="Pmax Legal")
        fig2.update_layout(template="plotly_white", title="Efecto del Control de Alquileres", xaxis_title="Cantidad de Departamentos", yaxis_title="Tarifa Mensual")
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("📊 Simulación de Escenarios Obligatorios")
    pmax_sim = [70, 60, 50, 40, 30]
    tabla2_data = []
    for p in pmax_sim:
        r = calcular_mercado(1800.0, 20.0, 0.0, 12.0, "Precio Máximo", float(p))
        qd_s = 1800.0 - 20.0*p
        qo_s = 12.0*p
        tabla2_data.append({"Precio Máximo ($)": p, "Cantidad Demandada": qd_s, "Cantidad Ofrecida": qo_s, "Escasez (Unidades)": max(0.0, r['escasez'])})
    df2 = pd.DataFrame(tabla2_data)
    st.dataframe(df2, use_container_width=True)