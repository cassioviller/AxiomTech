# Instruções para Deploy no EasyPanel usando Nixpacks

Este documento contém as configurações necessárias para fazer o deploy do site da Axiom Strategic Technologies no EasyPanel usando Nixpacks.

## Configurações para o formulário do EasyPanel

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

## Solução de Problemas

- Se as imagens não aparecerem, verifique se a pasta `dist/images` foi corretamente copiada durante o build
- Em caso de problemas com a porta, verifique se ela está liberada no firewall
- Para logs de erro, consulte os logs da aplicação no EasyPanel

## Estrutura de Arquivos Importantes

- `server/index.ts` - Ponto de entrada do servidor
- `client/public/images/` - Pasta de imagens personalizáveis
- `nixpacks.toml` - Configuração do Nixpacks
- `package.json` - Scripts de build e start