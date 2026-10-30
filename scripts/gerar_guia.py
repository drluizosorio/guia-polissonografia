#!/usr/bin/env python3
"""Monta o guia na identidade do médico (logo, cores, fontes, assinatura do perfil) e imprime em PDF
com o Chrome, Edge, Chromium ou Brave do próprio computador. Só usa a biblioteca padrão do Python.

Uso:
  gerar_guia.py <corpo.html> --saida <guia.pdf> [--medico N|nome] [--rodape TEXTO] [--perfil PASTA]
  gerar_guia.py --exemplo --saida <previa.pdf> [--medico N|nome] [--perfil PASTA]   (prévia com dados fictícios; serve de teste)

No corpo, {{MEDICO}} vira o nome de quem assina ("de {{MEDICO}}" vira "da Dra. ..." ou "do Dr. ...") e <!--assinatura--> vira a linha de assinatura.
Saídas: o PDF e, ao lado, o HTML completo (abre no navegador e imprime com Cmd+P).
Códigos de saída: 0 ok · 2 sem navegador compatível (o HTML fica pronto) · 3 perfil ou argumento inválido · 4 a impressão falhou.
"""
import argparse, base64, html, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PERFIL_PADRAO = os.environ.get("GUIA_POLISSONO_PERFIL", "~/.config/guia-polissonografia")
NAVEGADORES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
NOMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "brave-browser", "chrome"]
PILHAS = {
    "serifa": '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif',
    "sem serifa": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif',
}
CORES_PADRAO = {"primaria": "#1F4E5F", "destaque": "#2A7F62", "fundo_suave": "#EEF3F2", "texto": "#1B1F23",
                "linha": "#D3DBDA", "texto_suave": "#6B7378"}
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".webp": "image/webp"}


def falha(msg, codigo=3):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(codigo)


def pilha(nome, reserva):
    """Nome de fonte do perfil → font-family CSS com reserva do sistema."""
    if nome in PILHAS:
        return PILHAS[nome]
    if not re.fullmatch(r"[\w .'-]{1,60}", nome):
        falha(f"nome de fonte inválido no perfil: {nome!r}")
    return f'"{nome}", {PILHAS[reserva]}'


def texto_css(s):
    """Texto dentro de content: "..." no CSS."""
    return re.sub(r"\s+", " ", s).replace("\\", "\\\\").replace('"', '\\"')


assert texto_css('Dr. "X" \\ a\nb') == 'Dr. \\"X\\" \\\\ a b'


def contracao(nome):
    """'de' + artigo do título: 'da Dra. Ana', 'do Dr. Rui'; sem título, 'de Ana Lima'."""
    m = re.match(r"Dr(a?)\.?\s", nome)
    return ("da" if m.group(1) else "do") if m else "de"


assert [contracao(n) for n in ("Dra. Ana", "Dr. Rui", "Dr Rui", "Drauzio Lima")] == ["da", "do", "do", "de"]


def escolher_medico(medicos, alvo):
    if alvo is None:
        if len(medicos) == 1:
            return medicos[0]
        falha("o perfil tem mais de um médico; diga quem assina com --medico: "
              + "; ".join(f"{i} = {m['nome']}" for i, m in enumerate(medicos, 1)))
    if alvo.isdigit() and 1 <= int(alvo) <= len(medicos):
        return medicos[int(alvo) - 1]
    achados = [m for m in medicos if alvo.lower() in m["nome"].lower()]
    if len(achados) != 1:
        falha(f"--medico {alvo!r} não identifica um único médico do perfil")
    return achados[0]


def achar_navegador():
    candidatos = [os.environ.get("GUIA_NAVEGADOR", "")] + NAVEGADORES + [shutil.which(n) or "" for n in NOMES]
    return next((c for c in candidatos if c and os.path.isfile(c) and os.access(c, os.X_OK)), None)


def contar_paginas(pdf):
    # shortcut: conta os objetos /Type /Page do PDF do Chrome; se vier 0, quem chamou confere abrindo o PDF
    return len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", pdf.read_bytes()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("corpo", nargs="?", type=Path)
    ap.add_argument("--exemplo", action="store_true")
    ap.add_argument("--saida", required=True, type=Path)
    ap.add_argument("--medico")
    ap.add_argument("--rodape")
    ap.add_argument("--perfil", default=PERFIL_PADRAO)
    a = ap.parse_args()

    pasta = Path(a.perfil).expanduser()
    arq = pasta / "perfil.json"
    if not arq.exists():
        falha(f"perfil não encontrado em {arq}; configure o perfil primeiro (references/configurar.md)")
    try:
        perfil = json.loads(arq.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        falha(f"perfil.json inválido: {e}")
    medicos = perfil.get("medicos") or []
    if not medicos or not all(m.get("nome") and m.get("crm") for m in medicos):
        falha("perfil.json precisa de 'medicos' com pelo menos nome e crm")
    medico = escolher_medico(medicos, a.medico)

    cores = {**CORES_PADRAO, **(perfil.get("cores") or {})}
    for k, v in cores.items():
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(v)):
            falha(f"cor inválida em perfil.json ({k}: {v!r}); use hex como #1F4E5F")
    fontes = perfil.get("fontes") or {}
    f_tit, f_corpo = fontes.get("titulos", "serifa"), fontes.get("corpo", "sem serifa")
    link = ""
    if fontes.get("google_fonts"):
        fam = "&".join(f"family={n.replace(' ', '+')}:wght@400;700" for n in dict.fromkeys([f_tit, f_corpo]) if n not in PILHAS)
        link = f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fam}&display=swap">' if fam else ""
    pilha_corpo = pilha(f_corpo, "sem serifa")
    variaveis = "\n".join([f"  --{k.replace('_', '-')}: {v};" for k, v in cores.items()]
                          + [f"  --fonte-titulos: {pilha(f_tit, 'serifa')};", f"  --fonte-corpo: {pilha_corpo};"])

    logo = ""
    if perfil.get("logo"):
        lp = (pasta / perfil["logo"]).expanduser()
        if not lp.exists():
            falha(f"logo não encontrada: {lp}")
        if lp.suffix.lower() not in MIME:
            falha(f"formato de logo não suportado ({lp.suffix}); use PNG, JPG, SVG ou WEBP")
        logo = f'<img src="data:{MIME[lp.suffix.lower()]};base64,{base64.b64encode(lp.read_bytes()).decode()}" alt="">'

    if a.exemplo:
        corpo = (SKILL / "assets" / "exemplo.html").read_text(encoding="utf-8")
    elif a.corpo and a.corpo.exists():
        corpo = a.corpo.read_text(encoding="utf-8")
    else:
        falha("informe o arquivo do corpo do guia (ou --exemplo)")
    if "<!--assinatura-->" not in corpo:
        print("aviso: o corpo não tem <!--assinatura-->; a assinatura do perfil não foi inserida", file=sys.stderr)
    partes = [f"<strong>{html.escape(medico['nome'])}</strong>"] + [html.escape(medico[k]) for k in ("especialidade", "crm", "rqe") if medico.get(k)]
    nome = html.escape(medico["nome"])
    corpo = corpo.replace("de {{MEDICO}}", f"{contracao(medico['nome'])} {nome}").replace("{{MEDICO}}", nome).replace("<!--assinatura-->", f'<p class="assinatura">{" · ".join(partes)}</p>')

    assinatura_txt = " · ".join(medico[k] for k in ("nome", "crm", "rqe") if medico.get(k))
    rodape = a.rodape or perfil.get("rodape") or f"Guia de leitura da polissonografia · {assinatura_txt}"
    pagina = (SKILL / "assets" / "modelo.html").read_text(encoding="utf-8")
    for chave, valor in {
        "{{TITULO}}": html.escape(a.saida.stem), "{{FONTES_LINK}}": link, "{{VARIAVEIS}}": variaveis,
        "{{RODAPE}}": texto_css(rodape), "{{FONTE_CORPO}}": pilha_corpo, "{{COR_SUAVE}}": cores["texto_suave"],
        "{{LOGO}}": logo, "{{ROTULO}}": html.escape(perfil.get("clinica") or medico["nome"]), "{{CORPO}}": corpo,
    }.items():
        pagina = pagina.replace(chave, valor)

    saida = a.saida.expanduser().resolve()
    saida.parent.mkdir(parents=True, exist_ok=True)
    html_final = saida.with_suffix(".html")
    html_final.write_text(pagina, encoding="utf-8")

    nav = achar_navegador()
    if not nav:
        print(f"Sem Chrome, Edge, Chromium ou Brave. O HTML está pronto: abra {html_final} no navegador e imprima em PDF (Cmd+P no Mac, Ctrl+P no Windows).")
        sys.exit(2)
    inicio = time.time()
    with tempfile.TemporaryDirectory() as perfil_nav:  # perfil descartável: não mexe no navegador aberto do médico
        r = subprocess.run([nav, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                            "--no-pdf-header-footer", f"--user-data-dir={perfil_nav}", "--virtual-time-budget=10000",
                            f"--print-to-pdf={saida}", html_final.as_uri()], capture_output=True, text=True, timeout=180)
    if not saida.exists() or saida.stat().st_mtime < inicio - 1:
        falha(f"o navegador não gerou o PDF ({Path(nav).name}): {r.stderr.strip()[-400:]}", 4)
    print(f"PDF: {saida} ({contar_paginas(saida)} págs.) · HTML: {html_final} · navegador: {Path(nav).name}")


if __name__ == "__main__":
    main()
