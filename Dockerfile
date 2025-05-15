FROM node:18-alpine AS builder

WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar dependências
RUN npm ci

# Construir a aplicação
RUN npm run build

# Segunda etapa - apenas para servir os arquivos compilados
FROM nginx:alpine

# Copiar os arquivos compilados da etapa de build
COPY --from=builder /app/dist/public /usr/share/nginx/html

# Criar configuração do Nginx para a porta 6000
RUN echo 'server { \
    listen 6000; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expor porta
EXPOSE 6000

# Iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]