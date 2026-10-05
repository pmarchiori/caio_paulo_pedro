# Scan passivo com OWASP ZAP: API FastAPI

## Escopo e método

- **Alvo:** API FastAPI em execução local (`http://127.0.0.1:8000`), código de `fastapi/`.
- **Ferramenta:** OWASP ZAP 2.17.0 (imagem oficial `ghcr.io/zaproxy/zaproxy:stable`), rodando em modo daemon como **proxy**.
- **Tipo de scan:** passivo. O ZAP analisa apenas as respostas do tráfego que passa por ele. Nenhum ataque ativo (fuzzing, injeção, força bruta) foi executado.
- **Tráfego gerado:** requisições reais aos endpoints, sem arquivo de entrada e sem spider automático:
  - públicos: `/health`, `/docs`, `/redoc`, `/openapi.json`;
  - sem token (esperado 401): `/me`, `/predict`, `/auth/signin` com senha errada;
  - com token JWT do usuário `alice` (seed): `/auth/token`, `/me`, `/predict`, `/predictions`, `/predictions/1`, `/predictions/999999`;
  - CORS: `OPTIONS /health` com `Origin` externo;
  - erro de login: `POST /auth/token` com credenciais inválidas.
- **Cobertura:** nenhuma rota de escrita de conta foi usada (`/auth/signup` não foi chamado, para não alterar o banco). O `/predict` gravou registros no `database.db`.

## Resultado geral

| Severidade (risk) | Quantidade de alertas (após correção) |
| --- | --- |
| High | 0 |
| Medium | 3 |
| Low | 1 |
| Informational | 3 |

Atenção à leitura do relatório: no ZAP, `Informational (Medium)` significa **severidade Informational** com **confiança Medium**. A severidade é a primeira parte do texto.

Não há findings **High**. Há **3 findings Medium**, detalhados abaixo. Os findings Low e Informational estão fora do escopo deste documento.

---

## Finding 1: CSP permite `unsafe-inline` em `script-src`

- **7.1 Finding:** Content Security Policy com `script-src 'unsafe-inline'` (ZAP, plugin 10055, CWE-693).
- **7.2 Severidade:** Medium.
- **7.3 Confiança:** High.
- **7.4 URL afetada:** `/docs` e `/redoc` (2 instâncias).
- **7.5 O que foi detectado:** a resposta envia `script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net`.
- **7.6 Por que é um problema:** `'unsafe-inline'` desliga a principal proteção da CSP contra XSS. Se um atacante conseguir injetar HTML, um `<script>` inline seria executado sem bloqueio do navegador.
- **7.7 Correção realizada:** em `fastapi/middlewares.py`, a API passou a enviar uma CSP estrita em todas as respostas (`CSP_API`, com `script-src 'self'`, sem `unsafe-inline`). Só `/docs` e `/redoc` mantêm uma política relaxada (`CSP_DOCS`), porque Swagger UI e ReDoc dependem de script inline e de CDN.
- **7.8 Validação:**
  - `GET /health` retorna `script-src 'self'`, sem `unsafe-inline`.
  - `GET /docs` retorna a política relaxada, como esperado.
  - Re-scan com ZAP: o alerta continua **somente** em `/docs` e `/redoc`. Nenhum endpoint da API aparece.
  - Verificação visual no navegador: `/docs` e `/redoc` carregaram normalmente, com o Swagger UI e o ReDoc renderizados sem erro.
- **7.9 Risco aceito (residual):** aceito para `/docs` e `/redoc`. Remover `unsafe-inline` dessas páginas quebraria a UI sem hospedar os assets localmente. Recomendação para produção: desabilitar a documentação (`FastAPI(docs_url=None, redoc_url=None)`) ou servir Swagger/ReDoc com nonce ou hash.

## Finding 2: CSP permite `unsafe-inline` em `style-src`

- **7.1 Finding:** Content Security Policy com `style-src 'unsafe-inline'` (ZAP, plugin 10055, CWE-693).
- **7.2 Severidade:** Medium.
- **7.3 Confiança:** High.
- **7.4 URL afetada:** `/docs` e `/redoc` (2 instâncias).
- **7.5 O que foi detectado:** a resposta envia `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net`.
- **7.6 Por que é um problema:** estilos inline injetados podem alterar a interface (por exemplo, sobrepor elementos para enganar o usuário). O risco é menor que o de script, mas a política perde essa restrição.
- **7.7 Correção realizada:** mesma correção do Finding 1. `CSP_API` usa `style-src 'self'`, sem `unsafe-inline`.
- **7.8 Validação:** mesma do Finding 1. Os headers de `/health` estão estritos. O alerta permanece apenas em `/docs` e `/redoc`.
- **7.9 Risco aceito (residual):** mesmo do Finding 1, pelo mesmo motivo.

## Finding 3: Sub Resource Integrity (SRI) ausente

- **7.1 Finding:** atributo `integrity` ausente em recursos carregados de terceiros (ZAP, plugin 90003, CWE-345).
- **7.2 Severidade:** Medium.
- **7.3 Confiança:** High.
- **7.4 URL afetada:** `/docs` (2 instâncias: `swagger-ui.css` e `swagger-ui-bundle.js` do jsdelivr) e `/redoc` (2 instâncias: fontes do Google Fonts e `redoc.standalone.js` do jsdelivr).
- **7.5 O que foi detectado:** tags `<script src>` e `<link rel="stylesheet">` apontando para CDNs externos sem o atributo `integrity`.
- **7.6 Por que é um problema:** se o CDN for comprometido ou servir um arquivo alterado, o navegador executa o código sem verificar a assinatura. Com SRI, o navegador rejeita arquivos que não batam com o hash esperado.
- **7.7 Correção realizada:** **nenhuma**. Motivo: SRI exige hash de uma versão fixa. As URLs usam versões flutuantes (`swagger-ui-dist@5`, `redoc@2`), e o FastAPI não adiciona `integrity` às páginas geradas.
- **7.8 Validação:** não se aplica, pois não houve correção. O alerta foi confirmado no re-scan.
- **7.9 Risco aceito:** sim, para a documentação de desenvolvimento. Opções futuras: fixar a versão e incluir o hash SRI, servir os assets localmente, ou desabilitar `/docs` e `/redoc` em produção.

---

## Conclusão

- A API **não** tem findings High.
- Os 3 findings Medium estão **todos** nas páginas de documentação (`/docs` e `/redoc`). Nenhum endpoint de negócio (`/auth`, `/me`, `/predict`, `/predictions`) apresentou finding Medium.
- A correção aplicada reduziu a política de segurança da API às respostas JSON, sem alterar o alerta nas páginas de docs. Os riscos residuais estão documentados e aceitos para ambiente de desenvolvimento.
