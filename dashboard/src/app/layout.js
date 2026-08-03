export const metadata = {
  title: 'Dashboard Econométrico',
  description: 'Análisis de Gasto Público e Importaciones',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body style={{ margin: 0, padding: 0, fontFamily: 'system-ui, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}