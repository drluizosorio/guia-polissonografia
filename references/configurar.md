# Configurar o perfil do médico

Leia no primeiro uso (não existe `perfil.json` na pasta do perfil) ou quando o médico pedir para mudar logo, cores, fontes, pasta de saída ou assinatura.

## Onde fica

Pasta do perfil: `~/.config/guia-polissonografia/` (ou a da variável `GUIA_POLISSONO_PERFIL`). Dentro dela:

- `perfil.json`: assinatura, identidade visual e pasta de saída;
- `logo.png` (ou `.svg`, `.jpg`, `.webp`);
- `criterios.md`, só se o médico quiser critérios próprios.

## A entrevista

Pergunte em blocos curtos: `AskUserQuestion` quando houver opções, texto livre para nomes e números. Não invente nenhum dado: CRM e RQE saem exatamente como o médico digitar.

1. **Quem assina.** Para cada médico que vai assinar (pode ser mais de um, por exemplo sócios da mesma clínica): nome como deve sair, com Dr. ou Dra.; especialidade; CRM com a UF (ex.: CRM-SP 123456); RQE, se tiver.
2. **Clínica.** Nome que vai no alto da página, à direita da logo. Sem clínica, sai o nome do médico.
3. **Logo.** Caminho do arquivo (PNG, SVG, JPG ou WEBP). Copie para a pasta do perfil como `logo.<extensão>`. Sem logo, o alto da página fica só com o nome.
4. **Identidade visual.** Ofereça quatro caminhos:
   - tirar as cores da logo: abra a imagem com Read e proponha primária, destaque e fundo suave;
   - ler o manual de marca ou o design system do médico (PDF, site, `DESIGN.md`) e extrair cores e fontes;
   - um dos modelos prontos, abaixo;
   - cores que o médico informar, em hex.
   A primária vai nos títulos e no cabeçalho das tabelas, com texto branco por cima: precisa de contraste de pelo menos 4,5:1 com o branco (confira com `python3 -c`). O destaque só aparece como filete, então pode ser claro: cor de logo clara demais vira destaque, e a primária fica numa versão mais escura dela. `texto` também precisa de 4,5:1 sobre o `fundo_suave` (fundo do quadro de destaques e de linhas das tabelas), e `texto_suave` sobre o branco (rodapé).
5. **Fontes.** Fontes do sistema (padrão; funcionam sem internet): `"serifa"` e `"sem serifa"`. Ou fontes do Google Fonts pelo nome, com `"google_fonts": true`; elas precisam de internet na hora de gerar o PDF (o pedido leva só o nome da fonte, nada do paciente). Se a fonte não aparecer na prévia, o nome está errado ou a família não tem os pesos 400 e 700: troque.
6. **Pasta de saída.** Padrão: `~/Documents/Guias de polissonografia`.
7. **Rodapé.** Opcional. Sem rodapé no perfil, cada guia sai com "Guia de leitura da polissonografia de DD/MM/AAAA · NOME · CRM · RQE". Telefone ou endereço só se o médico pedir.
8. **Critérios.** Por padrão, os do método da Dra. Luma (`references/criterios.md`). Se o médico quiser outros, copie esse arquivo para `criterios.md` na pasta do perfil e edite com ele: a cópia vale no lugar do padrão.

Mostre o resumo e salve o `perfil.json` só com o "ok" do médico.

## Modelos prontos

| Modelo | primaria | destaque | fundo_suave | texto | linha | texto_suave |
|--------|----------|----------|-------------|-------|-------|-------------|
| Petróleo | #1F4E5F | #2A7F62 | #EEF3F2 | #1B1F23 | #D3DBDA | #6B7378 |
| Vinho | #6B2737 | #A0522D | #F6EFEC | #231A1C | #E2D5D0 | #7A6A6D |
| Grafite | #2B2D42 | #3D5A80 | #F1F2F5 | #1C1D24 | #D9DBE2 | #6C6F7D |

## perfil.json

```json
{
  "medicos": [
    {"nome": "Dra. Nome Sobrenome", "especialidade": "Otorrinolaringologista", "crm": "CRM-SP 123456", "rqe": "RQE 12345"},
    {"nome": "Dr. Outro Nome", "especialidade": "Pneumologista", "crm": "CRM-SP 654321"}
  ],
  "clinica": "Nome da Clínica",
  "logo": "logo.png",
  "cores": {"primaria": "#1F4E5F", "destaque": "#2A7F62", "fundo_suave": "#EEF3F2", "texto": "#1B1F23", "linha": "#D3DBDA", "texto_suave": "#6B7378"},
  "fontes": {"titulos": "serifa", "corpo": "sem serifa", "google_fonts": false},
  "pasta_saida": "~/Documents/Guias de polissonografia",
  "rodape": ""
}
```

Obrigatórios: `medicos`, com `nome` e `crm` em cada um. O resto tem padrão (modelo Petróleo, fontes do sistema).

## Prévia

Depois de salvar, gere a prévia com paciente fictício e abra o PDF com Read para o médico ver:

```bash
python3 scripts/gerar_guia.py --exemplo --saida "<pasta_saida>/Prévia do guia.pdf" --medico 1
```

Ajuste até o médico aprovar. Mudanças depois: edite o `perfil.json` (mantenha o JSON válido) e gere a prévia de novo.
