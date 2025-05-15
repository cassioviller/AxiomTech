#!/bin/bash

# Script para iniciar o servidor em desenvolvimento com port forwarding
# Isso permite que o workflow do Replit funcione corretamente enquanto
# mantemos a configuração de porta 6000 para produção/Docker

echo "Iniciando servidor de desenvolvimento com port forwarding 5000 -> 6000"

# Inicia o servidor em background na porta 6000
NODE_ENV=development tsx server/index.ts &
SERVER_PID=$!

# Aguarda o servidor iniciar
sleep 3

# Usa socat para redirecionar a porta 5000 para 6000
socat TCP-LISTEN:5000,fork TCP:localhost:6000 &
SOCAT_PID=$!

# Função para capturar o sinal de interrupção
trap "kill $SERVER_PID $SOCAT_PID; exit" INT TERM EXIT

# Mantém o script em execução
wait $SERVER_PID