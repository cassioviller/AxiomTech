FROM nginx:alpine

COPY client/public /usr/share/nginx/html

RUN mkdir -p /usr/share/nginx/html/images

# Configurar para usar uma porta específica (6000)
RUN sed -i 's/listen       80;/listen       6000;/g' /etc/nginx/conf.d/default.conf
RUN sed -i 's/listen  \[::\]:80;/listen  \[::\]:6000;/g' /etc/nginx/conf.d/default.conf

# Expor porta 6000
EXPOSE 6000

CMD ["nginx", "-g", "daemon off;"]