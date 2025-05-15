FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json primeiro para aproveitar o cache
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar o resto dos arquivos
COPY . .

# Construir a aplicação
RUN npm run build

# Configurar porta
ENV PORT=6000
ENV NODE_ENV=production

# Expor porta
EXPOSE 6000

# Iniciar a aplicação em modo produção
CMD ["node", "dist/index.js"]