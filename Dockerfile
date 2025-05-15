# Estágio de build
FROM node:20-alpine AS build

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos de dependência
COPY package*.json ./
RUN npm ci

# Copiando código fonte
COPY . .

# Compilando o aplicativo
RUN npm run build

# Estágio de produção com Nginx
FROM nginx:alpine

# Copiando os arquivos estáticos para o Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Arquivo de configuração nginx com HEREDOC para evitar problemas de formatação
RUN cat > /etc/nginx/conf.d/default.conf << 'EOL'
server {
    listen 6000;
    listen [::]:6000;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }
    
    # Habilitar gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOL

# Criando arquivo de fallback
RUN echo '<!DOCTYPE html><html><head><title>Axiom Technologies</title></head><body><h1>Axiom Technologies</h1><p>Site em construção</p></body></html>' > /usr/share/nginx/html/index.html

# Expondo a porta
EXPOSE 6000

# Comando para iniciar o Nginx em foreground
CMD ["nginx", "-g", "daemon off;"]