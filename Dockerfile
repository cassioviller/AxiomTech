# Usar uma imagem oficial do Nginx - nada de complicações
FROM nginx:alpine

# Copiar arquivos HTML estáticos pré-construídos (não vamos construir nada)
COPY ./client/public /usr/share/nginx/html/

# Criar uma configuração simples para o Nginx
RUN echo 'server { listen 6000; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf

# Criar um arquivo index.html simples
RUN echo '<!DOCTYPE html><html><head><title>Axiom Strategic Technologies</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>body{font-family:Arial,sans-serif;text-align:center;padding:50px;} h1{color:#333;} a{display:inline-block;margin-top:20px;background:#4CAF50;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;}</style></head><body><h1>Axiom Strategic Technologies</h1><p>Soluções estratégicas para sua empresa.</p><a href="https://wa.me/5511999999999">Contato via WhatsApp</a></body></html>' > /usr/share/nginx/html/index.html

# Expor a porta 6000
EXPOSE 6000

# Executar o Nginx em foreground
CMD ["nginx", "-g", "daemon off;"]