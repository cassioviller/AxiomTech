# Portfólio do Cássio Viller: site estático (portfolio/site) servido pelo nginx.
# O nginx responde Range (206), de que os vídeos do site precisam para a rolagem buscar quadros por currentTime.
FROM nginx:1.27-alpine

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY portfolio/site/ /usr/share/nginx/html/
# video/alta é um link simbólico para portfolio/video-alta (os mestres em HD, usados por alta.html)
RUN rm -f /usr/share/nginx/html/video/alta
COPY portfolio/video-alta/ /usr/share/nginx/html/video/alta/

EXPOSE 5001
