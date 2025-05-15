# Definindo a imagem base Node.js
FROM node:20-alpine AS builder

# Definindo diretório de trabalho
WORKDIR /app

# Copiando arquivos de dependências para aproveitar o cache do Docker
COPY package.json package-lock.json ./

# Instalando dependências com flags de produção para otimização
RUN npm ci --production=false --no-audit --no-fund

# Copiando os arquivos do projeto (usando .dockerignore para ignorar arquivos desnecessários)
COPY . .

# Compilando o aplicativo
RUN npm run build

# Imagem de produção - mínima
FROM node:20-alpine AS runner

# Adicionando labels para documentação
LABEL maintainer="Axiom Strategic Technologies"
LABEL description="Site institucional da Axiom Strategic Technologies"
LABEL version="1.0"

# Definindo diretório de trabalho
WORKDIR /app

# Configurando ambiente de produção
ENV NODE_ENV=production
ENV PORT=6000
ENV HOST=0.0.0.0

# Instalando apenas pacotes mínimos necessários para produção
COPY --from=builder /app/package.json /app/package-lock.json ./
RUN npm ci --production --no-audit --no-fund && npm cache clean --force

# Copiando apenas os arquivos necessários para produção
COPY --from=builder /app/dist ./dist

# Assegurando que as imagens estejam acessíveis em todos os possíveis caminhos
COPY --from=builder /app/client/public/images ./dist/images
COPY --from=builder /app/client/public/images ./dist/assets/images
COPY --from=builder /app/client/public/images ./dist/client/public/images

# Definindo usuário não-root para segurança
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 expressjs && \
    chown -R expressjs:nodejs /app
USER expressjs

# Verificação de saúde para EasyPanel
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:6000/ || exit 1

# Expondo a porta para o aplicativo
EXPOSE 6000

# Comando para iniciar o aplicativo em produção
CMD ["node", "dist/index.js"]

# Instruções para deploy EasyPanel:
# 1. No EasyPanel, crie uma nova aplicação
# 2. Selecione "Usar Dockerfile"
# 3. Configure a porta de serviço para 6000
# 4. Configure o domínio desejado
# 5. Inicie o deploy