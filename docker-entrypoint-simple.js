#!/usr/bin/env node

// Script simples para servir arquivos estáticos sem verificações complexas

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

// Configuração básica
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 6000;

// Caminho padrão para os arquivos estáticos
const staticPath = '/app/dist';

console.log('Iniciando servidor...');
console.log(`Porta: ${PORT}`);
console.log(`Diretório: ${staticPath}`);

// Listar arquivos no diretório para debug
try {
  console.log('Arquivos em /app/dist:');
  console.log(fs.readdirSync('/app/dist'));
} catch (err) {
  console.error('Erro ao listar diretório:', err.message);
}

// Middleware para logs
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
  next();
});

// Rota de debug
app.get('/ping', (req, res) => {
  res.send('pong');
});

// Rota de diagnóstico
app.get('/info', (req, res) => {
  res.json({
    staticPath,
    files: fs.existsSync(staticPath) ? fs.readdirSync(staticPath) : [],
    env: process.env.NODE_ENV,
    port: PORT
  });
});

// Servir arquivos estáticos
app.use(express.static(staticPath));

// Rota para todas as outras solicitações - SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(staticPath, 'index.html'));
});

// Iniciar o servidor
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Servidor rodando em http://0.0.0.0:${PORT}`);
});