FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json primeiro para aproveitar o cache
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar o resto dos arquivos
COPY . .

# Definir a porta do servidor
ENV PORT=6000

# Expor a porta
EXPOSE 6000

# Comando para iniciar a aplicação
CMD ["npm", "run", "dev"]