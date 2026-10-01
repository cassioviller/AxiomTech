# Render realista ("tipo Lumion") — pesquisa e plano, 01/10/2026

Pedido do Cássio: as cenas do site v2 ainda parecem maquete; ele quer um acabamento de visualização arquitetônica
(Lumion). O render passa a rodar no PC dele (Windows, RTX 3060 12 GB) por uma sessão do Claude Code
(`portfolio/cenas/RENDER-LOCAL.md`), então o custo por quadro deixa de ser o gargalo.

## 1. O que faz um render parecer real (e onde as cenas estão hoje)
O que os guias de Lumion/V-Ray repetem: luz indireta (GI) que suaviza sombras e tinge superfícies; céu HDRI que
ilumina e reflete; materiais PBR com imperfeição; vegetação variada (espécies, tamanhos, densidade); câmera de
fotógrafo (lente, profundidade de campo, desfoque de movimento); pós-produção contida (curva de tons, balanço de
branco). Lumion faz isso com rasterização + ray tracing e uma biblioteca enorme de modelos prontos.

| Ingrediente | Hoje (three.js r186, rasterização) | Lacuna |
|---|---|---|
| Luz indireta | não há; GTAO escurece os cantos, ambiente pelo PMREM do céu pintado | **grande**: sem rebatimento de cor, interiores (abertura, orçamento) chapados |
| Céu | pintado em canvas | média: HDRI fotográfico dá luz e reflexo reais |
| Materiais | PBR procedural em metros (rodada 14), bom | pequena |
| Modelos | caixas e primitivas feitas à mão (caminhão, guindaste, árvores, móveis) | **grande**: é o que mais lê como "maquete" |
| Vegetação | capim instanciado, moitas irregulares | **grande** |
| Câmera | sem DOF, sem motion blur | média |
| Tons | `NoToneMapping` (para o documento sair com as cores exatas) | média: sem curva fílmica as luzes estouram e o céu fica sem nuance |
| Vídeo | 2,5 MB, crf 34–35 | **trava tudo**: vegetação e grão realistas comprimidos nesse teto viram borrão |

Conclusão: path tracing sozinho não resolve. Os três itens grandes são luz indireta, modelos e vegetação de
verdade, e o teto de compressão do vídeo.

## 2. Caminhos avaliados

### A. Continuar no three.js e somar um path tracer (`three-gpu-pathtracer`)
- v0.0.26 (29/09/2026), exige three ≥ r185 (temos r186). A 0.0.25 criou o `WebGPUPathTracer` e **deprecou o
  `WebGLPathTracer`** (vai ser removido); nosso palco é WebGL → ou fixar a 0.0.25/0.0.26 com o WebGL, ou migrar o
  palco para o `WebGPURenderer`.
- Só aceita `MeshStandardMaterial`/`MeshPhysicalMaterial` sem shader próprio: o **box mapping do `kit.js`
  (`onBeforeCompile`) não passa** → assar as UVs em metros na geometria (exato para as caixas; as cenas são quase
  só caixas). `InstancedMesh` (capim, aço, paredes) precisa virar geometria na BVH: dezenas de milhares de
  triângulos, ok numa 3060.
- Tem exemplo de animação (`samples` por quadro) e denoiser (oidn-web) que deixa ~25–35 amostras/pixel
  aceitáveis.
- Ganho: luz indireta e reflexos reais com o mesmo código de cena, os mesmos testes de pose/enquadramento e o
  mesmo `render.py`. Não resolve modelos nem vegetação.
- Risco: cintilação de quadro a quadro (ruído e denoiser mudam a cada quadro) → semente fixa por quadro e amostras
  suficientes; o projeto está em transição WebGL → WebGPU.

### B. Exportar a cena para o Blender e renderizar no Cycles (OptiX)
- O three.js já tem `GLTFExporter`: cada cena exporta a geometria e "assa" a animação amostrando `renderCena(t)`
  quadro a quadro em keyframes (posição/rotação de cada objeto que se move, e a câmera).
- No Blender (grátis, automatizável em Python: `blender -b arquivo.blend -P script.py`, que o Claude Code roda):
  troca de materiais por PBR escaneados CC0 (Poly Haven, ambientCG), céu HDRI CC0 (Poly Haven), capim por
  *geometry nodes*/partículas, árvores e veículos CC0, AgX (curva fílmica), DOF e motion blur reais.
- Cycles + OptiX na RTX: OptiX ≈ 40 % mais rápido que CUDA; o denoiser permite 128–256 amostras no lugar de 512+.
  Estimativa para 1080p de exterior: 20–90 s por quadro → 288 quadros ≈ 2–7 h por caso (uma noite). Ressalva das
  fontes: o denoiser por quadro cintila em animação → semente fixa, amostras suficientes, denoise com passes de
  albedo/normal.
- O documento real no fim de cada caso: renderizado como plano emissivo sem tone mapping **e** recomposto em 2D
  sobre o quadro (a posição dos 4 cantos é conhecida) para as cores saírem idênticas às da página.
- Ganho: é o caminho mais próximo do Lumion (GI, vegetação, assets reais, câmera). Custo: um pipeline novo
  (exportar → montar no Blender → render → `render.py` só encoda), os testes de cena passam a valer para o
  export, não para o vídeo final.

### C. Lumion, Twinmotion, Unreal
- Lumion: pago, só interface gráfica → o Claude Code não automatiza; fora.
- Twinmotion/Unreal 5 (Lumen, Movie Render Queue): muito realistas e grátis para este uso, mas instalação de
  dezenas de GB, ecossistema de assets pago (Megascans) e automação bem mais difícil que o Blender. Fora por ora.

## 3. Recomendação
**B (Blender + Cycles), com A como degrau rápido opcional**, e decidir o teto do vídeo antes de gastar render.

1. **Fase 0 — o teto do vídeo (decisão do Cássio, 10 min).** Sem isso, qualquer ganho morre no crf 35. Opções:
   AV1 (≈ 30–50 % menos bits para a mesma qualidade) com o H.264 atual de reserva; ou teto de 4–5 MB. Recomendo AV1 +
   reserva.
2. **Fase 1 — piloto Blender só no caso 4 (modulares)** (≈ 1–2 dias de montagem, 1 noite de render):
   exporter por cena (`cenas/exportar.py` + `GLTFExporter`, animação assada a 24 fps); `blender/montar.py`
   (materiais Poly Haven/ambientCG por tipo do `kit.js`, HDRI, AgX, capim por geometry nodes, 3–4 árvores CC0
   variadas, DOF leve); `blender/render.py` (Cycles OptiX, 1920×1080, semente fixa, denoise); o documento
   recomposto em 2D; `render.py --quadros <pasta>` para só encodar. Quadros de conferência lado a lado com o vídeo
   atual → o Cássio aprova ou não o caminho.
3. **Fase 2 — os outros três casos** (abertura e orçamento são interiores: aí a luz indireta é o maior ganho;
   SIGE: galpões e canteiro). Modelos que hoje são primitivas (caminhão, guindaste, carros, móveis) trocados por CC0
   onde houver equivalente de licença livre.
4. **Degrau opcional A** (se o Cássio quiser ver ganho antes do piloto B): path tracer no three.js só na abertura
   (interior, onde a GI aparece mais), sem mexer no resto. ≈ 1 dia.

## 4. Riscos e cuidados
- **Licenças:** só assets CC0 (Poly Haven, ambientCG) ou CC-BY com crédito no site; registrar a origem de cada um num
  `blender/ASSETS.md`.
- **Sigilo:** os documentos continuam vindo de `site/docs/` (já liberados); nada do zip original vai para o Blender.
- **Cintilação** em animação: conferir com quadros consecutivos lado a lado antes do render inteiro.
- **Tamanho do repositório:** HDRIs e assets ficam fora do git (baixados por script com hash), como os zips.
- **Tempo do PC:** uma noite por caso; o render retoma de onde parou (mesmo esquema de pasta de quadros).

## Fontes
- three-gpu-pathtracer: [releases](https://github.com/gkjohnson/three-gpu-pathtracer/releases),
  [CHANGELOG](https://github.com/gkjohnson/three-gpu-pathtracer/blob/main/CHANGELOG.md),
  [README/npm](https://www.npmjs.com/package/three-gpu-pathtracer),
  [PR no three.js (WebGPU)](https://github.com/mrdoob/three.js/pull/34704)
- Cycles/OptiX e denoise: [iRendering — CUDA × OptiX](https://irendering.net/consider-between-cuda-and-optix-for-blender-cycles/),
  [iRendering — denoisers](https://irendering.net/ai-denoising-for-rendering-how-optix-oidn-nlm-cut-your-render-time-by-70/),
  [Super Renders Farm — animação no Blender](https://superrendersfarm.com/article/blender-render-animation-complete-guide)
- Realismo em visualização arquitetônica: [learnarchitecture — fluxo realista no Lumion](https://learnarchitecture.net/3d-visualization/rendering/33249-realistic-lumion-render.html),
  [MyArchitectAI — ajustes do Lumion](https://www.myarchitectai.com/blog/lumion-render-settings),
  [illustrarch — renders fotorrealistas](https://illustrarch.com/architectural-visualization/25982-how-to-create-realistic-3d-architectural-rendering.html)

---

# Pesquisa aprofundada (01/10/2026, tarde): ferramentas gratuitas e automatizáveis

Decisão do Cássio: o render pesado roda no PC dele (RTX 3060), operado pelo Claude Code; o Replit monta e automatiza.

## Verificado
- **Blender 5.2.2 LTS** (15/09/2026): `blender -b -P script.py`, Cycles com `--cycles-device OPTIX` (driver NVIDIA ≥ 575).
  Grátis, sem interface. O `bpy` do pip pede Python 3.13 (o Replit tem 3.12): no Replit, só pelo tarball oficial
  (383 MB, Python próprio), e só para stills de validação em CPU (4 vCPUs, 7 GB: minutos por quadro, estimativa).
- **Poly Haven** (CC0, API sem login em `api.polyhaven.com`, pede `User-Agent` próprio): 997 HDRIs, 863 texturas,
  521 modelos. Úteis: `corrugated_iron*`, `asphalt_0x`, `gravel`, `grass_ground`, `red_dirt_mud_01`, `farm_soil`,
  `brushed_concrete`, `brown_planks_*`; árvores (20: `jacaranda_tree`, `tree_small_02`, `island_tree_0x`…), grama
  (`grass_medium_01/02`, `grass_bermuda_01`), canteiro (`cement_bag`, `concrete_road_barrier`,
  `modular_chainlink_fence`, `portable_generator`), escritório (`metal_office_desk`, `modern_arm_chair_01`,
  `potted_plant_0x`, `Shelf_01`, `classic_laptop`). **Não tem caminhão nem guindaste**: esses continuam
  procedurais, melhorados com chanfro, textura real e sujeira.
- **ambientCG** (CC0, API v3 e download direto `ambientcg.com/get?file=<id>_1K-JPG.zip`): 2.896 assets.
- **three-gpu-pathtracer 0.0.26**: exige WebGPU; o Chromium do Replit não tem adaptador WebGPU (testado, `null`).
  Só no PC, e só com materiais Standard/Physical.
- **ffmpeg do Replit** já tem `libsvtav1` e `libaom-av1`. AV1 no Safari/iOS só em aparelhos com decodificador por
  hardware (iPhone 15 Pro+, Macs M3+): o H.264 de reserva em `<source>` é obrigatório.

## Descartado (com motivo)
- IA vídeo-a-vídeo (ComfyUI + ControlNet): cintila e redesenha o documento, que tem de ficar exato.
- Unreal/Twinmotion/D5/Omniverse/Godot: grátis, mas cenas refeitas em editor, sem automação prática ou acima da 3060.
- Mitsuba, LuxCore, appleseed: reescrever cena e materiais sem vantagem sobre o Cycles.
- Sketchfab, BlenderKit (login), Share Textures (proíbe download automático), Kenney/Quaternius (low-poly).
- Add-on do Poly Haven para Blender é pago; a API resolve. Geradores de árvore (Sapling, tree-gen): piores que as
  árvores escaneadas do Poly Haven.

## Plano revisto
1. **Replit, já (sem GPU):** `cenas/baixar_assets.py` (Poly Haven + ambientCG, com hash, fora do git e `ASSETS.md`
   com a origem); nas cenas three.js: HDRI real com o sol alinhado, texturas PBR fotografadas no lugar das de
   canvas, árvores/grama/móveis em glTF, chanfros, AgX só na cena (documento fora do tone mapping). Isso melhora o
   render daqui **e** é a base do que o Blender recebe.
2. **Replit:** `cenas/exportar.py` (GLTFExporter, animação assada a 24 fps) e `blender/montar.py` +
   `blender/render.py`; um still por cena em Cycles CPU no Replit para validar o script antes de ir para o PC.
3. **PC (RTX 3060):** Cycles OptiX, 256–512 amostras + OIDN (albedo/normal), semente fixa, PNGs; piloto no caso 4.
4. **Vídeo:** AV1 + H.264 em `<source>` (pendente de decisão do Cássio sobre o teto).

## Não verificado
Tempo real do Cycles em CPU no Replit; denoise temporal do OptiX no 5.2; `InstancedMesh` no path tracer; ciclo
completo three.js → GLB → Blender com animação; ganho do AV1 neste conteúdo.

Fontes adicionais: [Blender download](https://www.blender.org/download/), [linha de comando](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html),
[Cycles 5.2](https://developer.blender.org/docs/release_notes/5.2/cycles/), [bpy no PyPI](https://pypi.org/project/bpy/),
[API do Poly Haven](https://github.com/Poly-Haven/Public-API), [termos](https://github.com/Poly-Haven/Public-API/blob/master/ToS.md),
[API do ambientCG](https://docs.ambientcg.com/api/), [licença](https://docs.ambientcg.com/license/),
[AV1 no caniuse](https://caniuse.com/av1), [ComfyUI](https://github.com/Comfy-Org/ComfyUI),
[Mitsuba 3](https://github.com/mitsuba-renderer/mitsuba3), [Godot: filmes](https://docs.godotengine.org/en/stable/tutorials/animation/creating_movies.html)
