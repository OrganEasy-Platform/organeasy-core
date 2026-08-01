# OrganEasy — Design System do Produto (UI)

Padrões de interface do sistema OrganEasy: cores, tipografia, ícones, componentes e modo escuro.
Fonte: prancha `docs/design/assets/identidade-visual-sistema.png`.

> Para logomarca, paleta institucional e aplicações de marca, ver `identidade-visual.md`.
> Tokens consolidados em formato máquina: `design-tokens.json`.

## Princípios

| Princípio | Descrição |
| --- | --- |
| Modular | Habilite apenas o que sua empresa precisa |
| Escalável | Cresça sem limites com uma plataforma robusta |
| Integrado | Conecte processos e centralize informações |
| Segurança | Dados protegidos com os mais altos padrões |

## 1. Cores da interface

A UI usa uma escala alinhada ao Tailwind CSS (green/cyan/blue/slate), o que facilita a implementação no frontend.

### Cores principais

| Token | Hex | Uso |
| --- | --- | --- |
| `primary` | `#22C55E` | Ações primárias, item ativo de navegação, switch ativo |
| `secondary` | `#06B6D4` | Apoio, elementos informativos |
| `accent` | `#3B82F6` | Destaque, links, foco, paginação ativa |

### Neutros

| Token | Hex | Uso |
| --- | --- | --- |
| `neutral-900` | `#0F172A` | Sidebar, textos principais, fundo do modo escuro |
| `neutral-700` | `#334155` | Textos secundários |
| `neutral-500` | `#64748B` | Textos de apoio, ícones inativos |
| `neutral-300` | `#CBD5E1` | Bordas, divisores |
| `neutral-100` | `#F1F5F9` | Fundos de seção, hover |
| `background` | `#F8FAFC` | Fundo geral da aplicação |

### Cores semânticas

| Token | Hex | Uso |
| --- | --- | --- |
| `success` | `#22C55E` | Confirmações, badges "Ativo" |
| `warning` | `#F59E0B` | Avisos, badges "Pendente" |
| `error` | `#EF4444` | Erros, ações destrutivas |
| `info` | `#3B82F6` | Informações, badges "Novo" |

## 2. Tipografia

Fonte da interface: **Inter** (Light, Regular, Medium, Semibold, Bold).

| Estilo | Tamanho | Peso | Detalhe |
| --- | --- | --- | --- |
| H1 | 32px | Bold | letter-spacing -0.5px |
| H2 | 24px | Semibold | letter-spacing -0.25px |
| H3 | 18px | Semibold | — |
| Body | 16px | Regular | line-height 160% |
| Small | 14px | Regular | line-height 150% |
| Caption | 12px | Regular | line-height 150% |

## 3. Ícones

- Estilo: **outline (line)**, traço de **2px**, cantos **arredondados**.
- Conjunto base: home, dashboard, usuários, organizações, calendário, dispositivos, carrinho, financeiro, gráficos, mensagens, notificações, configurações, ajuda, sair.
- Recomendação de biblioteca compatível: Lucide ou Heroicons (outline).

## 4. Componentes

### Botões

| Variante | Estilo |
| --- | --- |
| Primário | Fundo `primary`, texto branco, cantos arredondados |
| Secundário | Fundo branco, borda e texto `primary` |
| Terciário | Sem fundo/borda (ghost), texto `primary` |
| Destrutivo | Borda e texto `error`; sólido `error` para confirmação |
| Com ícone | Ícone à esquerda do rótulo (ex.: "+ Novo", "Editar", "Exportar", "Excluir") |

### Campos de entrada

| Estado | Estilo |
| --- | --- |
| Padrão | Borda `neutral-300`, placeholder `neutral-500` |
| Foco | Borda `accent` com anel de foco |
| Com ícone | Ícone à esquerda (ex.: busca) |
| Erro | Borda `error` + mensagem de erro abaixo em `error` |
| Sucesso | Borda `success` + ícone de check |

### Cards

Ícone em container suave, título (H3), descrição (Small) e ação "Acessar →" em `primary`. Fundo branco, borda `neutral-300` sutil, cantos arredondados.

### Abas (tabs)

Aba ativa com texto `primary` e indicador inferior; inativas em `neutral-500`.

### Badges

| Badge | Cor base |
| --- | --- |
| Ativo / Sucesso | `success` (fundo suave verde) |
| Pendente / Aviso | `warning` (fundo suave âmbar) |
| Inativo | `neutral-500` (fundo suave cinza) |
| Novo / Informação | `info` (fundo suave azul) |
| Erro | `error` (fundo suave vermelho) |

Formato pílula, texto em peso Medium.

### Tabela

- Cabeçalho em `neutral-100` com texto `neutral-700`.
- Linhas com divisor `neutral-300`; hover `neutral-100`.
- Coluna de status usa badges; coluna de ações usa ícones (visualizar, editar, mais opções).
- Rodapé com contagem ("Mostrando 1 a 3 de 24 resultados") + paginação.

### Alertas

| Tipo | Estilo |
| --- | --- |
| Sucesso | Fundo verde suave, ícone check |
| Atenção | Fundo âmbar suave, ícone alerta |
| Erro | Fundo vermelho suave, ícone erro |
| Informação | Fundo azul suave, ícone info |

Todos com ícone à esquerda e botão de fechar.

### Modal

Centralizado, com ícone de contexto no topo, título, texto de apoio e par de ações (Cancelar ghost + ação primária). Overlay escurecido.

### Paginação

Anterior / números / reticências / Próximo; página ativa com fundo `accent` e texto branco.

### Chip / Tag

Pílula com rótulo + "×" para remoção (ex.: "Cliente VIP", "Entrega Expressa", "Interno").

### Switch

Desativado em `neutral-300`; ativado em `primary`.

## 5. Navegação e layout

- **Sidebar** escura (`neutral-900`), logo no topo, itens com ícone + rótulo, item ativo com destaque `primary`, usuário logado no rodapé.
- **Topbar** com busca, notificações e avatar.
- **Dashboard**: cards de KPI (valor, variação percentual com seta verde/vermelha), gráficos de linha e donut, lista de atividades recentes e grid de módulos ativos.

## 6. Modo escuro

- Fundo geral: `neutral-900` (`#0F172A`) e superfícies em tom levemente mais claro.
- Textos: branco/`neutral-100`; secundários `neutral-500`.
- `primary`, `success`, `warning`, `error`, `info` mantêm os mesmos hex.
- Cards com borda sutil e fundo elevado escuro.

## 7. Relação com a paleta da marca

A marca usa `#34C759`/`#0891B2` (ver `identidade-visual.md`); a UI usa `#22C55E`/`#06B6D4` (escala Tailwind). Convenção adotada:

- **Marca** (logo, marketing, materiais institucionais): paleta da marca + Poppins.
- **Produto** (telas, componentes, e-mails transacionais): paleta UI + Inter.

Essa separação foi inferida das pranchas (a prancha do sistema usa Inter e a escala Tailwind; as pranchas de marca usam Poppins e o verde `#34C759`). Se preferir unificar em uma única paleta, os tokens em `design-tokens.json` devem ser ajustados.
