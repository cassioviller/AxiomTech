# Imagem base extremamente simples
FROM nginx:stable-alpine

# Criar pasta para nosso conteúdo
RUN mkdir -p /usr/share/nginx/html

# Criar um arquivo index.html diretamente no Dockerfile
RUN echo '<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Axiom Strategic Technologies</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        header {
            background-color: #004080;
            color: white;
            padding: 50px 0;
            margin-bottom: 40px;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }
        .btn {
            display: inline-block;
            background-color: #28a745;
            color: white;
            padding: 10px 25px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 20px;
        }
        .services {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin: 40px 0;
        }
        .service {
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 250px;
            max-width: 300px;
        }
        footer {
            background-color: #333;
            color: white;
            padding: 20px 0;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Axiom Strategic Technologies</h1>
            <p>Transformando o futuro de negócios com soluções tecnológicas inovadoras</p>
            <a href="https://wa.me/5511999999999" class="btn">Fale Conosco</a>
        </div>
    </header>
    
    <main class="container">
        <h2>Nossos Serviços</h2>
        <div class="services">
            <div class="service">
                <h3>Consultoria Estratégica</h3>
                <p>Avaliamos seu negócio e implementamos soluções sob medida para otimizar processos e aumentar eficiência.</p>
            </div>
            <div class="service">
                <h3>Desenvolvimento de Software</h3>
                <p>Criamos aplicações customizadas e sistemas integrados com foco em resultados.</p>
            </div>
            <div class="service">
                <h3>Chatbots e IA</h3>
                <p>Implantamos soluções de inteligência artificial e chatbots para automatizar atendimento e melhorar experiência do cliente.</p>
            </div>
        </div>
        
        <h2>Entre em contato</h2>
        <p>Para mais informações sobre nossos serviços, entre em contato via WhatsApp.</p>
        <a href="https://wa.me/5511999999999" class="btn">Enviar mensagem</a>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; 2025 Axiom Strategic Technologies. Todos os direitos reservados.</p>
        </div>
    </footer>
</body>
</html>' > /usr/share/nginx/html/index.html

# Configurar Nginx para usar a porta 6000
RUN echo "server {\n\
    listen 6000;\n\
    root /usr/share/nginx/html;\n\
    location / {\n\
        index index.html;\n\
    }\n\
}" > /etc/nginx/conf.d/default.conf

# Expor porta
EXPOSE 6000

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]