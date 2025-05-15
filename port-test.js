const http = require('http');

// Criar um servidor HTTP simples que retorna "OK" para qualquer requisição
const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('OK\n');
});

// Tentar vincular na porta 6000
server.listen(6000, '0.0.0.0', () => {
  console.log('Servidor de teste rodando em http://0.0.0.0:6000/');
});

// Capturar erros
server.on('error', (e) => {
  console.error(`Erro ao iniciar servidor na porta 6000: ${e.message}`);
});