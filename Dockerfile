# Definindo a imagem base Node.js
FROM node:20-alpine AS builder

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos de dependências
COPY package.json package-lock.json ./

# Instalando dependências
RUN npm ci

# Copiando os arquivos do projeto
COPY . .

# Compilando o aplicativo
RUN npm run build

# Imagem de produção
FROM node:20-alpine AS runner

# Definindo diretório de trabalho
WORKDIR /app

# Configurando ambiente de produção
ENV NODE_ENV=production

# Copiando apenas os arquivos necessários para produção
COPY --from=builder /app/package.json /app/package-lock.json ./
COPY --from=builder /app/server ./server
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/client/public/images ./dist/images

# Expondo a porta para o aplicativo
EXPOSE 5000

# Comando para iniciar o aplicativo em produção
CMD ["node", "server/index.js"]

# Instruções para deploy EasyPanel:
# 1. Configure seu projeto no EasyPanel
# 2. Use esta imagem Docker para o deploy
# 3. Defina a porta 5000 para acesso externo
# 4. Configure as variáveis de ambiente conforme necessário