# Axiom Strategic Technologies - Site Institucional

Site one-page moderno e profissional para a empresa Axiom Strategic Technologies, liderada por Cássio Viller. Uma consultoria de alto nível que oferece soluções de engenharia inteligente e automação de processos para grandes corporações.

## Características

- Design moderno e responsivo para todos os dispositivos
- Navegação suave entre seções
- Animações de scroll para melhor engajamento
- Otimizado para desempenho e SEO
- Contato direto via WhatsApp

## Estrutura do Projeto

O projeto é baseado em React com TypeScript, utilizando uma arquitetura moderna com:

- Frontend: React, TypeScript, TailwindCSS
- Backend: Express.js para servir a aplicação
- Bundler: Vite para desenvolvimento rápido

## Personalização das Imagens

Todas as imagens do site estão localizadas em `/client/public/images/`. Para personalizar qualquer imagem:

1. Substitua o arquivo desejado mantendo o mesmo nome na pasta
2. Consulte o arquivo `README.md` dentro da pasta de imagens para mais detalhes

## Deploy via EasyPanel

Este projeto pode ser facilmente implantado usando o EasyPanel com Docker:

1. **Preparação do código**:
   - Faça clone do repositório
   - Certifique-se de personalizar as imagens conforme necessário

2. **No EasyPanel**:
   - Crie uma nova aplicação
   - Escolha a opção "Usando Dockerfile"
   - Aponte para o repositório do seu projeto
   - Configure a porta 6000 para acesso externo

3. **Variáveis de ambiente** (específicas para o EasyPanel):
   - `NODE_ENV`: Production
   - `PORT`: 6000
   - `HOST`: 0.0.0.0

4. **Implantação**:
   - Inicie o build
   - O EasyPanel construirá a imagem Docker usando o Dockerfile
   - A aplicação estará disponível na URL configurada

## Desenvolvimento

### Opção 1: Desenvolvimento direto (sem Docker)

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Construir para produção
npm run build

# Iniciar em modo produção
npm run start
```

### Opção 2: Desenvolvimento com Docker

```bash
# Construir e iniciar o container
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Parar o container
docker-compose down
```

Ao usar Docker, você pode acessar o site em `http://localhost:6000`

## Atualizando Imagens após Deploy

Para facilitar a atualização das imagens do site após o deploy sem precisar reconstruir a aplicação inteira:

### No EasyPanel:

1. Acesse o painel de controle do EasyPanel
2. Encontre sua aplicação e abra o terminal/console
3. Navegue até a pasta `/app/dist/client/images/`
4. Use o comando `cp` para substituir as imagens existentes ou faça upload de novas imagens

### Se estiver usando Docker Compose:

O volume montado em `docker-compose.yml` permite substituir as imagens diretamente na pasta `client/public/images/` do seu repositório local, e as alterações serão refletidas automaticamente.

## Suporte

Para suporte, entre em contato diretamente pelo WhatsApp: +55 12 98207-1116