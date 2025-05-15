# Definindo a imagem base Node.js
FROM node:20-alpine AS builder

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos de dependências para aproveitar o cache do Docker
COPY package.json package-lock.json ./

# Instalando dependências com flags de produção para otimização
RUN npm ci --production=false --no-audit --no-fund

# Copiando os arquivos do projeto
COPY . .

# Compilando o aplicativo
RUN npm run build

# Verificando quais arquivos foram gerados pelo build (para debugging)
RUN ls -la dist
RUN ls -la dist/public || true
RUN find /app/dist -type f -name "*.html" | xargs ls -la || true

# Imagem de produção - mínima
FROM node:20-alpine AS runner

# Adicionando labels para documentação
LABEL maintainer="Axiom Strategic Technologies"
LABEL description="Site institucional da Axiom Strategic Technologies"
LABEL version="1.0"

# Definindo diretório de trabalho
WORKDIR /app

# Configurando ambiente de produção
ENV NODE_ENV=production
ENV PORT=6000
ENV HOST=0.0.0.0

# Copiando os arquivos necessários para produção
COPY --from=builder /app/dist ./dist

# Instalando apenas express para servir o conteúdo estático
RUN npm init -y && \
    npm install express && \
    npm cache clean --force

# Criando um script simples para servir arquivos estáticos
RUN echo '#!/usr/bin/env node\n\
\n\
/**\n\
 * Script simplificado para servir o site Axiom no EasyPanel\n\
 * Sem health checks ou verificações complexas\n\
 */\n\
\n\
const express = require("express");\n\
const path = require("path");\n\
const fs = require("fs");\n\
\n\
const app = express();\n\
const PORT = process.env.PORT || 6000;\n\
\n\
// Caminho para os arquivos estáticos\n\
const staticPath = "/app/dist/public";\n\
\n\
// Detectar qual caminho existe no sistema\n\
if (!fs.existsSync(staticPath)) {\n\
  console.warn(`Aviso: ${staticPath} não encontrado.`);\n\
\n\
  // Listar o conteúdo do diretório dist para debug\n\
  const distPath = "/app/dist";\n\
  if (fs.existsSync(distPath)) {\n\
    console.log(`Conteúdo do diretório ${distPath}:`);\n\
    fs.readdirSync(distPath).forEach(file => {\n\
      console.log(`- ${file}`);\n\
    });\n\
  }\n\
}\n\
\n\
// Log de inicialização\n\
console.log(`Servidor iniciando na porta ${PORT}`);\n\
console.log(`Servindo arquivos estáticos de ${staticPath}`);\n\
\n\
// Permitir CORS para facilitar acesso\n\
app.use((req, res, next) => {\n\
  res.header("Access-Control-Allow-Origin", "*");\n\
  res.header("Access-Control-Allow-Headers", "*");\n\
  next();\n\
});\n\
\n\
// Log para debug\n\
app.use((req, res, next) => {\n\
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);\n\
  next();\n\
});\n\
\n\
// Rota para verificar se o servidor está rodando\n\
app.get("/ping", (req, res) => {\n\
  res.status(200).send("pong");\n\
});\n\
\n\
// Rota para status interno\n\
app.get("/status", (req, res) => {\n\
  res.json({\n\
    serverTime: new Date().toISOString(),\n\
    staticPath,\n\
    staticPathExists: fs.existsSync(staticPath),\n\
    nodeEnv: process.env.NODE_ENV,\n\
    port: PORT\n\
  });\n\
});\n\
\n\
// Servir arquivos estáticos\n\
app.use(express.static(staticPath));\n\
app.use(express.static("/app/dist"));\n\
\n\
// Rota principal - enviar index.html para qualquer caminho\n\
app.get("*", (req, res) => {\n\
  // Tenta encontrar o index.html em diferentes locais\n\
  const possiblePaths = [\n\
    path.join(staticPath, "index.html"),\n\
    "/app/dist/index.html",\n\
    "/app/dist/public/index.html"\n\
  ];\n\
\n\
  // Tenta cada caminho possível\n\
  for (const htmlPath of possiblePaths) {\n\
    if (fs.existsSync(htmlPath)) {\n\
      return res.sendFile(htmlPath);\n\
    }\n\
  }\n\
\n\
  // Se nenhum index.html for encontrado, mostra uma página de erro\n\
  res.status(404).send(`\n\
    <html>\n\
      <head><title>Erro - Arquivo não encontrado</title></head>\n\
      <body>\n\
        <h1>Erro: index.html não encontrado</h1>\n\
        <p>Não foi possível encontrar o arquivo index.html</p>\n\
        <h2>Caminhos verificados:</h2>\n\
        <pre>${JSON.stringify(possiblePaths, null, 2)}</pre>\n\
        <h2>Conteúdo de /app/dist:</h2>\n\
        <pre>${fs.existsSync("/app/dist") ? JSON.stringify(fs.readdirSync("/app/dist"), null, 2) : "Diretório não encontrado"}</pre>\n\
      </body>\n\
    </html>\n\
  `);\n\
});\n\
\n\
// Iniciar o servidor\n\
app.listen(PORT, "0.0.0.0", () => {\n\
  console.log(`Servidor rodando em http://0.0.0.0:${PORT}`);\n\
});\n\
' > server.js && chmod +x server.js

# Definindo usuário não-root para segurança
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 expressjs && \
    chown -R expressjs:nodejs /app
USER expressjs

# Expondo a porta para o aplicativo
EXPOSE 6000

# Comando para iniciar o aplicativo em produção
CMD ["node", "server.js"]

# Instruções para deploy EasyPanel:
# 1. No EasyPanel, crie uma nova aplicação
# 2. Selecione "Usar Dockerfile"
# 3. Configure a porta de serviço para 6000
# 4. Configure o domínio desejado
# 5. Inicie o deploy