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
   - Configure a porta 5000 para acesso externo

3. **Variáveis de ambiente** (se necessário):
   - `NODE_ENV`: Production
   - Outras variáveis específicas que possam ser necessárias

4. **Implantação**:
   - Inicie o build
   - O EasyPanel construirá a imagem Docker usando o Dockerfile
   - A aplicação estará disponível na URL configurada

## Desenvolvimento

Para desenvolvimento local:

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

## Suporte

Para suporte, entre em contato diretamente pelo WhatsApp: +55 12 98207-1116