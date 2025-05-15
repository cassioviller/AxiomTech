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

// Serve os arquivos estáticos
app.use(express.static(staticPath));

// Para qualquer outra rota, serve o index.html
app.get("*", (req, res) => {
  res.sendFile(path.join(staticPath, "index.html"));
});

// Inicia o servidor
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Serving static files from: ${staticPath}`);
});