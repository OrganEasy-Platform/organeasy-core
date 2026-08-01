# OrganEasy — Identidade Visual (Marca)

Padrões oficiais da marca OrganEasy Platform: logomarca, ícone, paleta de cores, tipografia e aplicações.
Fonte: pranchas de identidade visual em `docs/design/assets/` (`identidade-visual-logos.png` e `identidade-visual-logos-tipografia.png`).

> Para tokens de interface do produto (componentes, badges, tabelas, modo escuro), ver `design-system.md`.
> Tokens consolidados em formato máquina: `design-tokens.json`.

## 1. Logomarca

A marca é composta pelo símbolo (hexágono com "e" estilizado) + logotipo "OrganEasy" + tagline "PLATFORM".

Significado do símbolo:

| Elemento | Significado |
| --- | --- |
| Hexágono | Organização |
| Letra "e" | Easy / Simplicidade |
| Forma de cubo | Plataforma / Conexão |

### Variações e arquivos

| Variação | Uso | Arquivo em `assets/` |
| --- | --- | --- |
| Logomarca horizontal padrão | Uso preferencial em fundos claros | `logomarca-horizontal-padrao.png` |
| Logomarca empilhada | Espaços verticais/quadrados | `logomarca-empilhada.png` |
| Monocromática (fundo branco) | Impressão P&B, documentos | `logomarca-horizontal-mono-fundo-branco.png` |
| Negativa (fundo preto) | Fundos escuros, uma cor | `logomarca-horizontal-mono-fundo-preto.png` |
| Logo clara sem fundo | Sobreposição em fundos escuros | `logo-clara-sem-fundo.png` |
| Logo escura sem fundo | Sobreposição em fundos claros | `logo-escura-sem-fundo.png` |
| Ícone fundo branco | Avatar/app em contexto claro | `logo-fundo-branco.png` |
| Ícone fundo preto | Avatar/app em contexto escuro | `logo-fundo-preto.png` |

### Regras de uso

- Preferir a versão horizontal padrão sempre que houver espaço.
- Em fundos escuros, usar a versão negativa ou a logo clara sem fundo.
- Versão monocromática apenas quando cor não estiver disponível (impressão, gravação).
- Ícone isolado (hexágono) para favicon, app icon, avatar e marcação em ícone.
- Não distorcer, rotacionar, alterar cores ou aplicar sombras fora do padrão.

## 2. Paleta de cores da marca

| Papel | Hex | Uso |
| --- | --- | --- |
| Primária | `#34C759` | Verde da marca; símbolo, CTAs de marketing |
| Secundária | `#0891B2` | Ciano; apoio, links e detalhes |
| Acento | `#0F172A` | Azul-escuro quase preto; logotipo, fundos escuros |
| Cinza escuro | `#64748B` | Textos secundários, tagline |
| Cinza claro | `#F1F5F9` | Fundos suaves |
| Branco | `#FFFFFF` | Fundo padrão |

### Cores semânticas (marca)

| Papel | Hex |
| --- | --- |
| Sucesso | `#34C759` |
| Informação | `#0891B2` |
| Atenção | `#F59E0B` |
| Erro | `#EF4444` |
| Neutro | `#64748B` |

### Gradiente da marca

Gradiente linear usado no símbolo, banners e destaques:

```text
#34C759 -> #0891B2 -> #0D9488
```

### Padrão de background

Textura de hexágonos em baixa opacidade sobre fundo escuro (`#0F172A`), usada em banners e materiais institucionais.

## 3. Tipografia da marca

Fonte institucional: **Poppins** (títulos, materiais de marca e marketing).

| Estilo | Tamanho/Linha | Peso |
| --- | --- | --- |
| Título 1 | 32/40 | Bold |
| Título 2 | 24/32 | SemiBold |
| Título 3 | 20/28 | Medium |
| Texto | 16/24 | Regular |
| Legenda | 14/20 | Regular |
| Pequeno | 12/16 | Regular |

> A interface do produto usa **Inter** (ver `design-system.md`). Poppins fica reservada à marca e a materiais institucionais.

## 4. Aplicações

- **Assinatura de e-mail / rodapé**: logomarca horizontal + descrição "Plataforma completa para gestão integrada de empresas." + `www.organeasy.com`.
- **Redes sociais**: ícone da marca (hexágono) como avatar; presença em LinkedIn, GitHub, YouTube e X.
- **Banner institucional**: fundo em gradiente da marca com logomarca negativa e tagline "Sua empresa organizada. Seu crescimento acelerado.".
- **Favicon / app icon**: ícone isolado nas variações fundo claro, gradiente, fundo escuro e monocromática.

## 5. Pranchas de referência

- `assets/identidade-visual-logos.png` — logo principal, variações do ícone e significado.
- `assets/identidade-visual-logos-tipografia.png` — variações completas, paleta, tipografia e referência de UI.
- `assets/identidade-visual-sistema.png` — design system do produto (base de `design-system.md`).
