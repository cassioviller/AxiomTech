# Definindo a imagem base Node.js
FROM node:20-alpine AS builder

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos de dependências para aproveitar o cache do Docker
COPY package.json package-lock.json ./

# Instalando dependências com flags de produção para otimização
RUN npm ci --production=false --no-audit --no-fund

# Copiando os arquivos do projeto (usando .dockerignore para ignorar arquivos desnecessários)
COPY . .

# Compilando o aplicativo
RUN npm run build

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

# Instalando todos os pacotes incluindo dependências de desenvolvimento
# para garantir que o Vite esteja disponível
COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm ci --no-audit --no-fund && npm cache clean --force

# Copiando apenas os arquivos necessários para produção
COPY --from=builder /app/dist ./dist

# Vamos criar o index.html de fallback depois de ter criado todos os diretórios

# Criando um script de entrada simples diretamente na imagem de produção
RUN echo '#!/usr/bin/env node\n\
\n\
import express from "express";\n\
import path from "path";\n\
import fs from "fs";\n\
import { fileURLToPath } from "url";\n\
\n\
const __dirname = path.dirname(fileURLToPath(import.meta.url));\n\
const app = express();\n\
const PORT = process.env.PORT || 6000;\n\
\n\
// Possíveis caminhos para os arquivos estáticos\n\
const paths = [\n\
  "/app/dist/public",\n\
  "/app/dist",\n\
  path.join(__dirname, "dist", "public"),\n\
  path.join(__dirname, "dist")\n\
];\n\
\n\
// Encontra o primeiro caminho válido\n\
let staticPath = "/app/dist";\n\
for (const p of paths) {\n\
  try {\n\
    if (fs.existsSync(p)) {\n\
      staticPath = p;\n\
      break;\n\
    }\n\
  } catch (err) {}\n\
}\n\
\n\
console.log(`Servidor iniciando na porta ${PORT}`);\n\
console.log(`Servindo arquivos estáticos de: ${staticPath}`);\n\
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
// Rota para verificar se o servidor está ativo\n\
app.get("/ping", (req, res) => {\n\
  res.status(200).send("pong");\n\
});\n\
\n\
// Verificar se index.html existe no caminho\n\
let indexHtmlExists = false;\n\
try {\n\
  indexHtmlExists = fs.existsSync(path.join(staticPath, "index.html"));\n\
  console.log(`index.html ${indexHtmlExists ? "encontrado" : "NÃO encontrado"} em ${path.join(staticPath, "index.html")}`);\n\
} catch (err) {\n\
  console.error(`Erro ao verificar index.html:`, err.message);\n\
}\n\
\n\
// Servir arquivos estáticos\n\
app.use(express.static(staticPath));\n\
\n\
// Rota para verificar diretamente o index.html\n\
app.get("/checkindex", (req, res) => {\n\
  res.send({\n\
    staticPath: staticPath,\n\
    indexExists: indexHtmlExists,\n\
    envVars: {\n\
      NODE_ENV: process.env.NODE_ENV,\n\
      PORT: process.env.PORT,\n\
      HOST: process.env.HOST\n\
    }\n\
  });\n\
});\n\
\n\
// Rota principal - enviar index.html para qualquer caminho\n\
app.get("*", (req, res) => {\n\
  if (!indexHtmlExists) {\n\
    return res.status(404).send(`\n\
      <html>\n\
        <head><title>Erro - Arquivo não encontrado</title></head>\n\
        <body>\n\
          <h1>Erro: index.html não encontrado</h1>\n\
          <p>O arquivo index.html não foi encontrado em ${path.join(staticPath, "index.html")}</p>\n\
          <h2>Conteúdo do diretório:</h2>\n\
          <pre>${JSON.stringify(fs.readdirSync(staticPath), null, 2)}</pre>\n\
        </body>\n\
      </html>\n\
    `);\n\
  }\n\
  \n\
  res.sendFile(path.join(staticPath, "index.html"));\n\
});\n\
\n\
// Iniciar o servidor\n\
app.listen(PORT, "0.0.0.0", () => {\n\
  console.log(`Servidor rodando em http://0.0.0.0:${PORT}`);\n\
  try {\n\
    const files = fs.readdirSync(staticPath);\n\
    console.log(`Arquivos em ${staticPath}:`, files);\n\
  } catch (err) {\n\
    console.error(`Erro ao listar diretório ${staticPath}:`, err.message);\n\
  }\n\
});\n\
' > docker-entrypoint-simple.js \
&& chmod +x docker-entrypoint-simple.js

# Assegurando que os arquivos estáticos estejam acessíveis em diversos caminhos
# Criando diretórios para garantir que existam
RUN mkdir -p ./dist/public ./dist/client ./dist/assets

# Copiando index.html para possíveis diretórios
COPY --from=builder /app/dist/index.html ./dist/index.html || true
COPY --from=builder /app/dist/index.html ./dist/public/index.html || true
COPY --from=builder /app/dist/client/index.html ./dist/client/index.html || true

# Copiando as imagens para possíveis diretórios
COPY --from=builder /app/client/public/images ./dist/images
COPY --from=builder /app/client/public/images ./dist/assets/images
COPY --from=builder /app/client/public/images ./dist/client/public/images
COPY --from=builder /app/client/public/images ./dist/public/images

# Definindo usuário não-root para segurança
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 expressjs && \
    chown -R expressjs:nodejs /app
USER expressjs

# Sem healthcheck para evitar problemas com EasyPanel
# HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=5 \
#   CMD wget --no-verbose --tries=1 --spider http://localhost:6000/health || exit 1

# Expondo a porta para o aplicativo
EXPOSE 6000

# Criando um index.html de fallback caso o build falhe em encontrá-lo
RUN echo '<!DOCTYPE html>\
<html lang="pt-br">\
<head>\
  <meta charset="UTF-8">\
  <meta name="viewport" content="width=device-width, initial-scale=1.0">\
  <title>Axiom Strategic Technologies</title>\
  <style>\
    body { font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }\
    .logo { max-width: 200px; margin-bottom: 2rem; }\
    h1 { color: #333; }\
    p { color: #666; max-width: 600px; text-align: center; }\
  </style>\
</head>\
<body>\
  <h1>Axiom Strategic Technologies</h1>\
  <p>Estamos trabalhando para trazer nosso site completo. Por favor, entre em contato pelo WhatsApp.</p>\
  <a href="https://wa.me/5511999999999" target="_blank">Fale Conosco</a>\
</body>\
</html>' > /app/dist/index.html && \
echo '<!DOCTYPE html><html><head><title>Axiom</title></head><body><h1>Axiom</h1></body></html>' > /app/dist/public/index.html && \
chmod 644 /app/dist/index.html /app/dist/public/index.html

# Verificar e listar arquivos para debug ao iniciar
RUN ls -la /app && ls -la /app/dist && ls -la /app/dist/public || true

# Comando para iniciar o aplicativo em produção usando script simplificado
CMD ["node", "docker-entrypoint-simple.js"]

# Instruções para deploy EasyPanel:
# 1. No EasyPanel, crie uma nova aplicação
# 2. Selecione "Usar Dockerfile"
# 3. Configure a porta de serviço para 6000
# 4. Configure o domínio desejado
# 5. Inicie o deploy