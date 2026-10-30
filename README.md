# Guia da polissonografia para o paciente

Skill do Claude Code que lê o laudo de polissonografia do seu paciente e gera um **guia de leitura** em PDF, com a sua logo, as suas cores e a sua assinatura (nome, CRM, RQE). O guia vai junto com o laudo: destaca o que importa, sempre nos mesmos 5 tópicos, e explica cada termo em palavras simples. Não substitui o laudo nem indica tratamento.

**Método de leitura e critérios:** Dra. Luma Costa, otorrinolaringologista.

## O que precisa

- Claude Code instalado.
- Python 3. No Mac, vem com as ferramentas de linha de comando: `xcode-select --install`.
- Google Chrome, Microsoft Edge, Chromium ou Brave, para gerar o PDF. Sem nenhum deles, a skill entrega o guia em HTML para você imprimir em PDF pelo navegador.
- Opcional: `pdftotext` (no Mac, `brew install poppler`), que lê melhor as tabelas do laudo.

## Instalar

Copie a pasta `guia-polissonografia` inteira para a pasta de skills do Claude Code:

- Mac e Linux: `~/.claude/skills/`
- Windows: `%USERPROFILE%\.claude\skills\`

## Primeiro uso

Abra o Claude Code e diga "configura o guia da polissonografia", ou já mande um laudo. Na primeira vez ele pergunta quem assina (pode ser mais de um médico), a logo, as cores (tiradas da logo, do seu manual de marca, de um modelo pronto ou as que você escolher), as fontes e a pasta onde salvar. Depois gera uma prévia com paciente fictício para você aprovar.

O perfil fica em `~/.config/guia-polissonografia/`, fora da pasta da skill: ao instalar uma versão nova, ele continua lá.

## Uso

"Faz o guia da polissonografia desse laudo para o paciente: <arquivo>". Funciona com PDF com texto, PDF escaneado e foto do laudo.

## Critérios próprios

A skill vem com os critérios da Dra. Luma (faixas do IAH, latência REM, saturação basal, regra do dobro no REM e na posição etc.). Para usar os seus, copie `references/criterios.md` para `~/.config/guia-polissonografia/criterios.md` e edite essa cópia, ou peça ao Claude para fazer isso com você.

## Privacidade

O laudo é lido pelo Claude dentro da sua sessão, e os arquivos ficam no seu computador, na pasta que você escolher. A skill nunca envia nada ao paciente: o envio é seu. Guarde e compartilhe os guias como faria com qualquer documento do prontuário.

Para você poder reeditar um guia, a subpasta oculta `.trabalho/`, dentro da pasta dos guias, guarda o texto extraído do laudo, recortes das páginas e o corpo de cada guia. É dado do paciente como o próprio guia: apague quando não precisar mais.
