'use client';
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import data from '../data/dashboard_data.json';

export default function DashboardPage() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <header style={{ marginBottom: '2rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '1rem' }}>
        <h1 style={{ color: '#0f172a', fontSize: '1.875rem', fontWeight: 'bold' }}>{data.metadata.titulo}</h1>
        <p style={{ color: '#64748b' }}>Metodología: <strong>{data.metadata.metodologia}</strong> | Cobertura: {data.metadata.periodo_cobertura}</p>
      </header>

      {/* Tarjetas de Diagnóstico */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Observaciones</span>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b' }}>{data.metadata.observaciones}</p>
        </div>
        <div style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Rango Cointegración</span>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2563eb' }}>r = {data.diagnosticos.cointegracion_rank}</p>
        </div>
        <div style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Ecuaciones VECM</span>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#059669' }}>{data.diagnosticos.num_ecuaciones}</p>
        </div>
      </div>

      {/* Gráfico 1: Series Históricas */}
      <div style={{ background: '#fff', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Evolución de las Variables Macro (Logs)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.series_historicas}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="fecha" />
            {/* Se ajusta el eje Y dinámicamente según el mínimo y máximo de los datos */}
            <YAxis domain={['auto', 'auto']} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="gasto_gobierno" name="Gasto Público" stroke="#2563eb" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="importaciones" name="Importaciones" stroke="#dc2626" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="pib_real" name="PIB Real" stroke="#059669" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico 2: Función Impulso Respuesta */}
      <div style={{ background: '#fff', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
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
    </div>
  );
}