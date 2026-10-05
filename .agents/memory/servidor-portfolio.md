---
name: Servidor do portfólio
description: Restrições para servir vídeos e diagnosticar falhas de execução do portfólio.
---

Preserve suporte HTTP Range ao alterar o servidor estático. Cancelamentos de downloads pelo navegador devem encerrar apenas a conexão, sem esconder erros inesperados.

**Why:** Buscar outro instante de um vídeo cancela requisições anteriores; isso pode produzir ConnectionResetError ou BrokenPipeError sem representar falha da aplicação. Um servidor estático sem HTTP 206 pode impedir a busca nos vídeos.

**How to apply:** Valide HTTP 200 e 206 e confira o processo que ocupa a porta antes de atribuir uma falha de inicialização ao conteúdo do site. Instâncias órfãs já impediram o workflow de assumir a porta.
