# Pasta de Imagens - Axiom Strategic Technologies

Esta pasta contém todas as imagens utilizadas no site da Axiom Strategic Technologies. Para substituir qualquer imagem, basta substituir o arquivo correspondente nesta pasta, mantendo o mesmo nome de arquivo.

## Arquivos de Imagens

- `axiom-logo.png` - Logo da Axiom Strategic Technologies (usado no header e footer)
- `hero-background.jpg` - Imagem de fundo da seção Hero
- `profile-cassio.jpg` - Foto de perfil do CEO Cássio Viller
- `solution-automation.jpg` - Imagem da solução "Automação Inteligente de Processos"
- `solution-data.jpg` - Imagem da solução "Engenharia de Dados e KPIs Estratégicos"
- `solution-operations.jpg` - Imagem da solução "Otimização de Operações e Rotinas Técnicas"
- `case-success.jpg` - Imagem do caso de sucesso

## Instruções para Substituição

### Durante o desenvolvimento:

1. Prepare sua nova imagem com dimensões próximas à imagem original para manter a proporção
2. Renomeie sua nova imagem para corresponder exatamente ao nome do arquivo que deseja substituir
3. Substitua o arquivo existente nesta pasta por sua nova imagem
4. Recarregue o site para ver as alterações

### Após deploy no EasyPanel:

1. Acesse o terminal da aplicação no EasyPanel
2. Navegue até um dos seguintes diretórios:
   - `/app/dist/images/`
   - `/app/dist/assets/images/`
   - `/app/dist/client/public/images/`
3. Use o comando `cp /caminho/para/nova/imagem.jpg .` para substituir cada imagem

## Formatos Recomendados

- Para imagens fotográficas: JPG/JPEG (melhor compressão)
- Para logos e gráficos com transparência: PNG
- Tamanhos recomendados:
  - Logo: 500x500px (mantendo proporção original)
  - Imagens de seção: 1920x1080px (background) ou 800x500px (cards)