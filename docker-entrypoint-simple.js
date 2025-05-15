#!/usr/bin/env node

// Script simples para servir a aplicação em produção sem verificações ou diagnósticos

import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 6000;

// Caminho para os arquivos estáticos - baseado nos logs do container
const staticPath = path.join(__dirname, "dist", "public");

// Caminhos alternativos a serem tentados se o padrão não funcionar
const alternativePaths = [
  path.join(__dirname, "dist", "public"),
  path.join(__dirname, "dist"),
  "/app/dist/public",
  "/app/dist"
];

// Encontra o primeiro caminho existente
let finalPath = staticPath;
for (const testPath of alternativePaths) {
  try {
    if (fs.existsSync(testPath)) {
      finalPath = testPath;
      console.log(`Usando caminho: ${finalPath}`);
      break;
    }
  } catch (err) {
    console.log(`Erro ao verificar caminho ${testPath}: ${err.message}`);
  }
}

// Log simples
console.log(`Starting server...`);
console.log(`Static path: ${finalPath}`);

// Permitir todos os CORS para facilitar o acesso
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "*");
  next();
});

// Verificar se index.html existe no caminho
let indexHtmlExists = false;
try {
  indexHtmlExists = fs.existsSync(path.join(finalPath, "index.html"));
  console.log(`index.html ${indexHtmlExists ? "encontrado" : "NÃO encontrado"} em ${path.join(finalPath, "index.html")}`);
} catch (err) {
  console.error(`Erro ao verificar index.html:`, err.message);
}

// Servir arquivos estáticos
app.use(express.static(finalPath));

// Rota para verificar diretamente o index.html
app.get("/checkindex", (req, res) => {
  res.send({
    staticPath: finalPath,
    indexExists: indexHtmlExists,
    envVars: {
      NODE_ENV: process.env.NODE_ENV,
      PORT: process.env.PORT,
      HOST: process.env.HOST
    }
  });
});

// Rota principal - envia index.html para qualquer caminho
app.get("*", (req, res) => {
  if (!indexHtmlExists) {
    return res.status(404).send(`
      <html>
        <head><title>Erro - Arquivo não encontrado</title></head>
        <body>
          <h1>Erro: index.html não encontrado</h1>
          <p>O arquivo index.html não foi encontrado em ${path.join(finalPath, "index.html")}</p>
          <h2>Conteúdo do diretório:</h2>
          <pre>${JSON.stringify(fs.readdirSync(finalPath), null, 2)}</pre>
        </body>
      </html>
    `);
  }
  
  res.sendFile(path.join(finalPath, "index.html"));
});

// Rota simples para indicar que o servidor está ativo
app.get('/ping', (req, res) => {
  res.status(200).send('pong');
});

// Tenta iniciar o servidor
try {
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Try accessing at http://localhost:${PORT}/`);
    console.log(`Serving static files from ${finalPath}`);
    
    // Lista os arquivos no diretório para debug
    try {
      const files = fs.readdirSync(finalPath);
      console.log(`Files in ${finalPath}:`, files);
    } catch (err) {
      console.error(`Error listing directory ${finalPath}:`, err.message);
    }
  });
} catch (err) {
  console.error(`Error starting server:`, err);
}