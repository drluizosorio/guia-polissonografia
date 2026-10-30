---
name: guia-polissonografia
description: Lê um laudo de polissonografia (PDF com texto, escaneado ou foto) e gera um guia de leitura PARA O PACIENTE, um PDF de 3 a 4 páginas com a logo, as cores, as fontes e a assinatura do médico (nome, CRM, RQE), que vai junto com o laudo e destaca o que importa em 5 tópicos - respiração (IAH, tipo de apneia, RERA, EEG), oxigênio e coração, arquitetura do sono, padrão dos eventos (posição e REM) e outros distúrbios (insônia, bruxismo, ronco, SRVAS, pernas inquietas). Não refaz o laudo - explica o laudo, mantendo os termos e dizendo o que significam. Na primeira vez, configura o perfil do médico. Use sempre que o usuário trouxer um laudo de polissonografia, polissono, PSG, estudo do sono, exame do sono ou teste domiciliar de apneia e quiser explicar para o paciente, traduzir o laudo, deixar o laudo palatável ou destacar o que o paciente precisa saber, mesmo sem pedir um guia, e também quando quiser configurar ou mudar a logo, as cores, as fontes ou a assinatura desse guia.
---

# Guia da polissonografia para o paciente

> O paciente recebe o laudo do laboratório e não sabe o que olhar. Esta skill gera um **guia de leitura** que vai junto com o laudo: destaca o que importa, sempre nos mesmos 5 tópicos, explica cada termo e sai com a identidade visual e a assinatura do médico. Não é um laudo novo nem uma versão bonita do laudo; o laudo do laboratório continua sendo o documento oficial.
> Nunca envia nada ao paciente: só gera os arquivos. O envio é do médico.
> Método de leitura e critérios: **Dra. Luma Costa**, otorrinolaringologista, que cedeu o método aos colegas.

Caminhos `scripts/`, `assets/` e `references/` são relativos à pasta desta skill.

## 1. Perfil do médico

A pasta do perfil é `~/.config/guia-polissonografia/` (ou a da variável `GUIA_POLISSONO_PERFIL`) e guarda `perfil.json`, a logo e, se o médico quiser, critérios próprios. Fica fora da pasta da skill para que uma versão nova da skill não apague nada.

- Sem `perfil.json` é o primeiro uso: siga `references/configurar.md` antes de tudo. Se o médico já mandou um laudo, configure e depois faça o guia.
- Pedido para mudar logo, cores, fontes, pasta de saída ou assinatura: `references/configurar.md`.
- **Quem assina.** Com mais de um médico no perfil, se o pedido não disser, pergunte com `AskUserQuestion`. O texto fica na 1ª pessoa de quem assina.
- **Critérios.** Use o `criterios.md` da pasta do perfil, se existir; senão, `references/criterios.md` (o método da Dra. Luma). Leia o arquivo inteiro antes de classificar.

## 2. Entrada

- `$ARGUMENTS` = caminho do laudo (PDF ou imagem) e, se vier, o nome do paciente (o laudo traz). Sem caminho, peça o arquivo.
- Confira que é um **laudo** (tem IAH, estágios, eficiência) e não um **pedido** de polissonografia, que também traz "Polissonografia" e o CID G47.3.

## 3. Extrair os dados

1. PDF com texto: se existir `pdftotext`, rode `pdftotext -layout "<laudo.pdf>" "<pasta_saida>/.trabalho/<nome do arquivo do laudo>.txt"` e leia o arquivo **inteiro**; o `-layout` mantém as tabelas em colunas, que é onde ficam os números. Sem `pdftotext`, abra o PDF com Read, todas as páginas. O mesmo dado pode estar no texto corrido, na tabela de estatísticas ou só na conclusão (ronco e bruxismo às vezes só aparecem na conclusão).
2. Escaneado (página sem texto) ou foto: abra cada página com Read e transcreva os números para a ficha. Depois confira cada número que vai para o guia olhando a imagem de novo: na leitura de imagem se troca dígito (3 e 8, 1 e 7) e se perde vírgula, e número errado vira informação errada para o paciente.
3. Monte para você a ficha dos 18 itens: o valor como está no laudo, a referência que o laudo traz e o que a conclusão do laudo diz do item. Ausente = "não informado". Exame que não mede o item (poligrafia, tipo 3, não tem EEG nem estágios) = "não medido neste tipo de exame".
4. Contas (eficiência a partir de TTS e TR, IAH no REM e no NREM a partir de eventos e minutos por estágio, IAH fora do decúbito dorsal): sempre `python3 -c`, nunca de cabeça. Valor calculado entra no guia como "calculado a partir do laudo".

Siglas e sinônimos (português e inglês) para achar cada dado, e as definições do glossário: `references/glossario.md`.

## 4. Os 5 tópicos

A ordem e os critérios estão no arquivo de critérios (seção 1). Em resumo: para classificar, valem os critérios do método e, para o resto, **só a referência ou a conclusão do próprio laudo**; sem nenhum dos dois, mostre o número sem classificar e diga que comenta na consulta. O guia nunca dá ao paciente uma gravidade diferente da conclusão do laudo: se o critério do método e o laudo divergirem, siga o laudo e avise o médico.

## 5. Redação

- 2ª pessoa (você) e 1ª pessoa de quem assina ("primeiro eu olho quantas vezes a sua respiração parou"). Frases curtas, acolhedoras e diretas.
- **Os termos do laudo ficam, em negrito, explicados na primeira vez** (o que é e por que importa). É isso que deixa o laudo palatável: o paciente passa a entender o próprio laudo. O glossário no fim reúne os termos que aparecem no laudo dele.
- Números como no laudo, com vírgula decimal (14.86 vira 14,86); horário pode virar 23h07.
- Normal também é informação: diga "normal" quando for e não procure problema.
- O guia explica, não diagnostica além do laudo e não indica tratamento (CPAP, aparelho, cirurgia, medidas de estilo de vida). Próximos passos são da consulta.
- Sem travessão (—), sem emoji, sem `[?]`.
- Privacidade: nome completo só na ficha; nada de CPF, endereço, telefone ou número do exame.

## 6. O texto do guia

Escreva só o **corpo** em HTML, com as classes abaixo. O script põe logo, cores, fontes, rodapé e numeração; `{{MEDICO}}` vira o nome de quem assina (`de {{MEDICO}}` vira "da Dra. …" ou "do Dr. …") e `<!--assinatura-->` vira a linha com nome, especialidade, CRM e RQE do perfil. `assets/exemplo.html` é um guia completo (paciente fictício) para conferir o formato.

```html
<h1>Entendendo sua polissonografia</h1>
<div class="ficha"><span class="paciente">NOME COMPLETO</span>Polissonografia de DD/MM/AAAA · LABORATÓRIO · leitura de {{MEDICO}}<span class="nota">Para ler junto com o seu laudo</span></div>
<p>Abertura, 2 a 3 linhas: este guia acompanha o laudo e não o substitui; leio o exame sempre nos mesmos cinco tópicos, que vêm abaixo (respiração, oxigênio e coração, arquitetura do sono, padrão dos eventos e outros distúrbios do sono); os números são os do seu laudo.</p>
<div class="importante"><h2>O que mais importa no seu exame</h2><ul>
<li>3 a 5 itens, o mais importante primeiro: gravidade e tipo da apneia e o que a piora (posição, REM), oxigênio, qualidade do sono, outros achados alterados. O que veio normal pode virar um item só.</li>
</ul></div>
<h2>Seu exame, tópico por tópico</h2>
<h3>1. Respiração: teve apneia? De que tipo?</h3>
<table class="itens"><thead><tr><th>#</th><th>O que eu olho</th><th>No seu exame</th><th>Referência</th><th>Leitura</th></tr></thead><tbody>
<tr><td>1</td><td><strong>IAH</strong>: pausas e reduções da respiração por hora de sono</td><td>16/h</td><td>normal até 5 · leve 5,1 a 15 · moderada 15,1 a 30 · grave acima de 30</td><td><strong>Apneia moderada</strong></td></tr>
<!-- itens 2 e 3 -->
</tbody></table>
<h3>2. Oxigênio e coração</h3>
<table class="itens"><tbody>
<!-- itens 4 e 5; só a tabela do tópico 1 tem cabeçalho -->
</tbody></table>
<!-- tópicos 3, 4 e 5, do mesmo jeito -->
<h2>O que isso quer dizer</h2>
<h3>Um h3 por ponto de atenção, na ordem dos tópicos</h3><p>Alterado, no limite, cautela da eficiência, artefato, item que o laudo não permite avaliar: 2 a 4 frases cada. Sem pontos de atenção, um parágrafo dizendo isso.</p>
<p>Os próximos passos a gente conversa na consulta.</p>
<!--assinatura-->
<h2>Glossário</h2>
<table class="glossario"><thead><tr><th>Termo do laudo</th><th>Em palavras simples</th></tr></thead><tbody>
<tr><td><strong>Termo</strong></td><td>Definição</td></tr>
</tbody></table>
```

- Títulos dos tópicos, nesta ordem: 1. Respiração: teve apneia? De que tipo? · 2. Oxigênio e coração · 3. Arquitetura e qualidade do sono · 4. Padrão dos eventos: posição e fase do sono · 5. Outros distúrbios do sono.
- Coluna "Leitura": **Normal**, **Alterado** (e o quê, em poucas palavras), **No limite**, **Não informado**, **Não medido**, ou "sem referência no laudo".
- Glossário: só termos que aparecem no laudo do paciente, em ordem alfabética, no máximo uns 15.

## 7. Arquivos e PDF

Pasta: `pasta_saida` do perfil. Nome base: `Polissonografia explicada - PRIMEIRO_NOME - AAAA-MM-DD`, com a data do exame; homônimo no mesmo dia, acrescente o sobrenome. Se o arquivo já existe, olhe antes: é reedição? Edite o corpo e gere de novo. O corpo e o material de trabalho (laudo.txt, ficha) ficam em `<pasta_saida>/.trabalho/`.

```bash
python3 scripts/gerar_guia.py "<pasta_saida>/.trabalho/<nome base>.corpo.html" \
  --saida "<pasta_saida>/<nome base>.pdf" --medico <número ou nome de quem assina> \
  --rodape "Guia de leitura da polissonografia de DD/MM/AAAA · NOME · CRM · RQE"
```

O `--rodape` acima é o padrão, com a data do exame e quem assina. Se o perfil tiver `rodape` próprio, não passe `--rodape`: vale o do perfil.

Sai o PDF e, ao lado, o HTML completo. Código 2 = não há Chrome, Edge, Chromium nem Brave: entregue o HTML e diga ao médico para abrir no navegador e imprimir em PDF (Cmd+P no Mac, Ctrl+P no Windows). Código 3 = perfil ou argumento inválido: a mensagem diz o que corrigir. Código 4 = o navegador falhou: mostre a mensagem.

## 8. Verificação (antes de reportar)

1. `grep -n -E "—|\[\?\]" "<corpo>"` → vazio.
2. Cada número da coluna "No seu exame" está no laudo (com ponto ou vírgula) ou está marcado como calculado.
3. A gravidade do IAH no guia é a mesma da conclusão do laudo.
4. Abra o PDF com Read, todas as páginas: logo e assinatura certas, tabela sem corte, de 3 a 4 páginas.

## 9. Reporte ao médico (curto)

Caminho do PDF e número de páginas. **Para conferir antes de enviar:** valores calculados, provável artefato, divergência entre o critério do método e o laudo, itens no limite, o que o laudo não informa.
