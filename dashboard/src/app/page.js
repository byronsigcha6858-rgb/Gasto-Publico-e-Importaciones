'use client';
import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import data from '../data/dashboard_data.json';

export default function DashboardPage() {
  // Transformación automática a Índice Base 100 (2010-Q3 = 100)
  const seriesTransformadas = useMemo(() => {
    if (!data.series_historicas || data.series_historicas.length === 0) return [];
    
    const baseGasto = Math.exp(data.series_historicas[0].gasto_gobierno);
    const baseImp = Math.exp(data.series_historicas[0].importaciones);
    const basePib = Math.exp(data.series_historicas[0].pib_real);

    return data.series_historicas.map(item => ({
      ...item,
      gasto_idx: (Math.exp(item.gasto_gobierno) / baseGasto) * 100,
      imp_idx: (Math.exp(item.importaciones) / baseImp) * 100,
      pib_idx: (Math.exp(item.pib_real) / basePib) * 100,
    }));
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      
      {/* Encabezado Principal */}
      <header style={{ marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '1rem' }}>
        <h1 style={{ color: '#0f172a', fontSize: '1.875rem', fontWeight: 'bold' }}>{data.metadata.titulo}</h1>
        <p style={{ color: '#64748b' }}>
          Metodología: <strong>{data.metadata.metodologia}</strong> | Cobertura: {data.metadata.periodo_cobertura}
        </p>
      </header>

      {/* 📌 SECCIÓN 1: Resumen Ejecutivo del Modelo */}
      <div style={{ background: '#fff', padding: '1.5rem', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', marginBottom: '1.5rem', border: '1px solid #e2e8f0' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#0f172a', marginBottom: '0.75rem' }}>
          Resumen Ejecutivo del Modelo
        </h2>
        <p style={{ color: '#334155', lineHeight: '1.6', marginBottom: '1rem' }}>
          Este estudio utiliza series macroeconómicas trimestrales en logaritmos del Banco Central del Ecuador (BCE). Se estimó un modelo de <strong>Vectores de Corrección de Errores (VECM)</strong> para analizar la relación de cointegración de largo plazo y la dinámica de corto plazo entre el Gasto Público, las Importaciones y el PIB Real.
        </p>

        {/* CPTA: Hallazgo Clave */}
        <div style={{ background: '#eff6ff', borderLeft: '4px solid #2563eb', padding: '1rem', borderRadius: '6px' }}>
          <h3 style={{ color: '#1d4ed8', fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.25rem' }}>
            Hallazgo Clave:
          </h3>
          <p style={{ color: '#1e40af', margin: 0, fontSize: '0.95rem', lineHeight: '1.5' }}>
            Existe una relación de cointegración ($r = 1$) estadísticamente significativa. Un incremento en el Gasto del Gobierno genera una respuesta positiva y persistente sobre las Importaciones, evidenciando un efecto de filtración (leakage) hacia la demanda externa en el mercado ecuatoriano.
          </p>
        </div>
      </div>

      {/* 📊 SECCIÓN 2: Tarjetas de Diagnóstico */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', border: '1px solid #e2e8f0' }}>
          <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Observaciones</span>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b', margin: '0.25rem 0 0 0' }}>{data.metadata.observaciones} obs.</p>
        </div>
        <div style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', border: '1px solid #e2e8f0' }}>
          <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Rango Cointegración</span>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2563eb', margin: '0.25rem 0 0 0' }}>r = {data.diagnosticos.cointegracion_rank}</p>
        </div>
        <div style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', border: '1px solid #e2e8f0' }}>
          <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Ecuaciones VECM</span>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#059669', margin: '0.25rem 0 0 0' }}>{data.diagnosticos.num_ecuaciones}</p>
        </div>
      </div>

      {/* 📈 SECCIÓN 3: Gráfico 1 - Series Históricas */}
      <div style={{ background: '#fff', padding: '1.5rem', borderRadius: '8px', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', border: '1px solid #e2e8f0' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.25rem' }}>Evolución Comparativa de Variables Macro</h2>
        <p style={{ color: '#64748b', marginBottom: '1rem', fontSize: '0.875rem' }}>Índice de Crecimiento Acumulado (Base 100 = 2010-Q3). Permite visualizar qué variable creció más rápido.</p>
        
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={seriesTransformadas}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="fecha" />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip formatter={(value) => [`${Number(value).toFixed(2)} pts`, '']} />
            <Legend />
            <Line type="monotone" dataKey="gasto_idx" name="Gasto Público (Índice)" stroke="#2563eb" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="imp_idx" name="Importaciones (Índice)" stroke="#dc2626" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="pib_idx" name="PIB Real (Índice)" stroke="#059669" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 🌊 SECCIÓN 4: Gráfico 2 - IRF */}
      <div style={{ background: '#fff', padding: '1.5rem', borderRadius: '8px', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', border: '1px solid #e2e8f0' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>Función Impulso-Respuesta (IRF)</h2>
        <p style={{ color: '#64748b', marginBottom: '1rem', fontSize: '0.875rem' }}>Respuesta dinámica de las Importaciones ante un choque positivo en el Gasto del Gobierno.</p>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data.irf_gasto_hacia_importaciones}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="periodo" label={{ value: 'Trimestres (Horizonte)', position: 'insideBottom', offset: -5 }} />
            <YAxis domain={['auto', 'auto']} />
            <Tooltip />
            <Area type="monotone" dataKey="respuesta" name="Efecto Trimestral" stroke="#2563eb" fill="#93c5fd" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* 📝 SECCIÓN 5: Conclusiones Econométricas Principales */}
      <div style={{ background: '#0f172a', padding: '1.5rem', borderRadius: '8px', color: '#f8fafc', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#38bdf8' }}>
          Conclusiones Econométricas Principales:
        </h3>
        <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: '#cbd5e1', margin: 0 }}>
          El Gasto Público actúa como un motor de arrastre sobre las Importaciones en el corto y largo plazo. Las perturbaciones fiscales se transmiten rápidamente a la demanda externa, alcanzando su pico de respuesta entre el segundo y tercer trimestre posterior al choque fiscal antes de estabilizarse.
        </p>
      </div>

    </div>
  );
}