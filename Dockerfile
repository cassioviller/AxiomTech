FROM nginx:stable-alpine

# Copiar site estático 
COPY client/public /usr/share/nginx/html

# Configurar para usar porta 6000
RUN sed -i 's/listen[[:space:]]*80;/listen 6000;/g' /etc/nginx/conf.d/default.conf

# Expor porta
EXPOSE 6000

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]