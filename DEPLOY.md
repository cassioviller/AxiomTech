# Instruções para Deploy no EasyPanel

Este documento contém as configurações necessárias para fazer o deploy do site da Axiom Strategic Technologies no EasyPanel.

Você tem duas opções de deploy: usando Nixpacks ou usando Dockerfile diretamente.

## Opção 1: Deploy usando Nixpacks

### Configurações para o formulário do EasyPanel

### Versão
1.34.1 (ou a mais recente disponível)

### Comando de Instalação
```
npm ci
```

### Comando de Build
```
npm run build
```

### Comando de Início
```
NODE_ENV=production PORT=5001 node dist/index.js
```

### Pacotes Nix
```
nodejs_20
```

### Pacotes APT
Deixe em branco.

## Variáveis de Ambiente

| Nome | Valor | Descrição |
|------|-------|-----------|
| PORT | 5001  | Porta onde a aplicação irá rodar |
| NODE_ENV | production | Define o modo de produção |

## Verificações após o Deploy

1. Confirme que o site está acessível na URL fornecida pelo EasyPanel
2. Verifique se todas as imagens estão carregando corretamente
3. Teste a navegação entre seções e a funcionalidade do botão de WhatsApp

## Opção 2: Deploy usando Dockerfile

Se o Nixpacks estiver apresentando problemas, você pode usar o Dockerfile diretamente:

1. No EasyPanel, selecione a opção "Custom Dockerfile" (Dockerfile personalizado)
2. O sistema usará automaticamente o arquivo `Dockerfile` presente na raiz do projeto
3. Não é necessário configurar nenhum campo adicional

### Verificações após o Deploy usando Dockerfile

1. Confirme que o site está acessível na URL fornecida pelo EasyPanel
2. Verifique se todas as imagens estão carregando corretamente
3. Teste a navegação entre seções e a funcionalidade do botão de WhatsApp

## Solução de Problemas

- Se as imagens não aparecerem, verifique se a pasta `dist/images` foi corretamente copiada durante o build
- Em caso de problemas com a porta, verifique se ela está liberada no firewall
- Para logs de erro, consulte os logs da aplicação no EasyPanel

## Estrutura de Arquivos Importantes

- `server/index.ts` - Ponto de entrada do servidor
- `client/public/images/` - Pasta de imagens personalizáveis
- `nixpacks.toml` - Configuração do Nixpacks (opção 1)
- `Dockerfile` - Arquivo para build direto com Docker (opção 2)
- `package.json` - Scripts de build e start