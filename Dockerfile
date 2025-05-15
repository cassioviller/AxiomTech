FROM node:18-alpine

WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar dependências
RUN npm ci

# Configurar porta e ambiente
ENV PORT=6000
ENV NODE_ENV=production

# Construir a aplicação
RUN npm run build

# Expor porta
EXPOSE 6000

# Iniciar a aplicação em modo produção
CMD ["node", "dist/index.js"]