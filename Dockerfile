FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package.json e package-lock.json primeiro para aproveitar o cache
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar o resto dos arquivos
COPY . .

# Construir a aplicação
RUN npm run build

# Segunda etapa - servidor web
FROM nginx:alpine

# Copiar os arquivos compilados
COPY --from=builder /app/dist/public /usr/share/nginx/html

# Configurar a porta 6000
RUN sed -i 's/listen\s*80;/listen 6000;/g' /etc/nginx/conf.d/default.conf
RUN sed -i 's/listen\s*\[::\]:80/listen [::]:6000/g' /etc/nginx/conf.d/default.conf

# Configurar o Nginx para aplicações SPA
RUN sed -i '/location \/ {/a \        try_files $uri $uri/ /index.html;' /etc/nginx/conf.d/default.conf

# Expor porta
EXPOSE 6000

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]