#!/bin/bash

# Este script executa o aplicativo e configura o Replit para visualizar na porta 6000
# Instrução: execute este script diretamente no terminal ou configure o Replit para usar este script

echo "Iniciando servidor na porta 6000 e configurando preview do Replit"

# Adiciona configuração para o preview usar a porta 6000 em vez da 5000
cat > .replit.preview << EOL
entrypoint = ".replit"

[deployment]
run = ["sh", "-c", "npm run start"]

[[ports]]
localPort = 6000
externalPort = 80
EOL

# Inicia o servidor com redirecionamento para compatibilidade com a configuração Replit
node dev.js