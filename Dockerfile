FROM nginx:alpine

# Copiar arquivos
COPY client/public /usr/share/nginx/html

# Configurar porta para 6000
RUN echo 'server { \
    listen 6000 default_server; \
    listen [::]:6000 default_server; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expor porta
EXPOSE 6000

# Iniciar
CMD ["nginx", "-g", "daemon off;"]