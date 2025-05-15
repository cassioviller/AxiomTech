#!/usr/bin/env node

// Script para servir a aplicação em produção sem depender do Vite
// Usado como ponto de entrada no Docker

import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 6000;

// Detecta automaticamente onde os arquivos estáticos estão
function findDistPath() {
  const possiblePaths = [
    path.join(__dirname, "dist"),
    path.join(__dirname, "dist", "client"),
    "/app/dist",
    "/app/dist/client"
  ];

  for (const p of possiblePaths) {
    if (fs.existsSync(p) && fs.existsSync(path.join(p, "index.html"))) {
      console.log(`Serving static files from: ${p}`);
      return p;
    }
  }

  // Tenta encontrar qualquer diretório que contenha index.html
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      console.log(`Directory exists: ${p}, searching for index.html`);
      try {
        const files = fs.readdirSync(p);
        console.log(`Files in ${p}:`, files);
        
        // Procura recursivamente um index.html
        const queue = [p];
        while (queue.length > 0) {
          const dir = queue.shift();
          const entries = fs.readdirSync(dir, { withFileTypes: true });
          
          for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
              queue.push(fullPath);
            } else if (entry.name === "index.html") {
              console.log(`Found index.html in: ${dir}`);
              return dir;
            }
          }
        }
      } catch (err) {
        console.error(`Error listing directory ${p}:`, err);
      }
    }
  }

  console.error("Could not find a valid dist path with index.html");
  return path.join(__dirname, "dist"); // Fallback
}

const staticPath = findDistPath();

// Adiciona cabeçalhos para possíveis problemas de CORS
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

// Serve os arquivos estáticos
app.use(express.static(staticPath));

// Adiciona rota healthcheck para diagnóstico
app.get('/health', (req, res) => {
  // Verifica se os arquivos importantes existem
  const indexFile = path.join(staticPath, "index.html");
  const testFile = path.join(staticPath, "test.html");
  const indexExists = fs.existsSync(indexFile);
  const testExists = fs.existsSync(testFile);
  
  // Obtém informações do sistema 
  const systemInfo = {
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch,
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage(),
    env: {
      NODE_ENV: process.env.NODE_ENV,
      PORT: process.env.PORT,
      HOST: process.env.HOST
    }
  };
  
  // Obtém todas as rotas registradas
  const routes = [];
  app._router.stack.forEach(function(r) {
    if (r.route && r.route.path) {
      routes.push(r.route.path);
    }
  });
  
  // Cria links para teste
  const host = req.headers.host || `localhost:${PORT}`;
  const protocol = req.secure ? 'https' : 'http';
  const baseUrl = `${protocol}://${host}`;
  
  // Retorna informações detalhadas
  res.status(200).send({
    status: 'ok',
    message: 'Server is running properly',
    time: new Date().toISOString(),
    path: staticPath,
    testLinks: {
      main: `${baseUrl}/`,
      testPage: `${baseUrl}/test.html`,
      health: `${baseUrl}/health`
    },
    files: {
      indexHtml: {
        path: indexFile,
        exists: indexExists,
        size: indexExists ? fs.statSync(indexFile).size : null,
      },
      testHtml: {
        path: testFile,
        exists: testExists,
        size: testExists ? fs.statSync(testFile).size : null,
      }
    },
    allFiles: fs.readdirSync(staticPath),
    routes: routes,
    system: systemInfo,
    headers: req.headers
  });
});

// Para qualquer outra rota, serve o index.html (deve vir após todas as outras rotas)
app.get("*", (req, res) => {
  res.sendFile(path.join(staticPath, "index.html"));
});

// Função para iniciar o servidor com um pequeno atraso
const startServer = () => {
  console.log('Preparando para iniciar o servidor...');
  
  // Atraso de 2 segundos antes de iniciar o servidor
  // Isso pode ajudar com problemas de timing em alguns ambientes
  setTimeout(() => {
    app.listen(PORT, "0.0.0.0", () => {
      console.log(`Server running on port ${PORT}`);
      console.log(`Serving static files from: ${staticPath}`);
      console.log(`Health check available at: http://localhost:${PORT}/health`);
      console.log(`Servidor pronto para receber conexões!`);
    });
  }, 2000);
};

// Inicia o servidor
startServer();