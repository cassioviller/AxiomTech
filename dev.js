// Script intermediário para iniciar o servidor e redirecionar a porta
// Este script é usado por Replit para contornar a limitação de configuração

console.log('Iniciando servidor na porta 6000 com redirecionamento da porta 5000');

import { spawn } from 'child_process';
import http from 'http';

// Iniciamos o servidor principal em segundo plano
const childProcess = spawn(
  'node_modules/.bin/tsx', 
  ['server/index.ts'], 
  {
    env: { ...process.env, NODE_ENV: 'development' },
    stdio: 'inherit'
  }
);

// Quando este script for encerrado, encerramos também o processo filho
process.on('SIGTERM', () => {
  childProcess.kill('SIGTERM');
  process.exit(0);
});

process.on('SIGINT', () => {
  childProcess.kill('SIGINT');
  process.exit(0);
});

// Criamos um servidor proxy que redireciona a porta 5000 para 6000
// Isso é necessário porque o Replit espera que a porta 5000 esteja aberta
setTimeout(() => {
  const server = http.createServer((req, res) => {
    res.writeHead(302, {
      'Location': `http://localhost:6000${req.url}`
    });
    res.end();
  });
  
  server.listen(5000, () => {
    console.log('Redirecionamento da porta 5000 para 6000 configurado para compatibilidade Replit');
  });
}, 3000); // Esperamos 3 segundos para o servidor principal iniciar