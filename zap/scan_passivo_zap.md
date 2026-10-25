# Auditoria de segurança com OWASP ZAP: API FastAPI

## Escopo e método

- **Alvo:** API FastAPI em execução local (`http://127.0.0.1:8000`), código de `fastapi/`.
- **Ferramenta:** OWASP ZAP (imagem oficial `ghcr.io/zaproxy/zaproxy:stable`), em Docker com `--network host`.
- **Tipo de scan:** passivo. O ZAP analisa apenas as respostas recebidas. Nenhum ataque ativo (fuzzing, injeção, força bruta) foi executado.
- **Scan 1, página de documentação:** `zap-baseline.py -t http://127.0.0.1:8000/docs`. Relatórios em `zap/relatorio_zap.*`.
- **Scan 2, endpoints:** `zap-api-scan.py -t http://127.0.0.1:8000/openapi.json -f openapi -S`. Relatórios em `zap/relatorio_zap_api.*`.
- **Validação complementar:** retire.js (mesma base de vulnerabilidades usada pelo ZAP) sobre `fastapi/static/swagger/`.
- **Evidência do estado anterior:** `zap/antes/`.

## Evolução dos resultados (scan do `/docs`)

| Etapa | High | Medium | Low | Informational |
| --- | --- | --- | --- | --- |
| 1. Estado inicial (Swagger/ReDoc via CDN) | 0 | 3 | 1 | 3 |
| 2. Swagger hospedado localmente (v5.17.14) | 0 | 1 | 5 | 2 |
| 3. Swagger atualizado (v5.33.2) + headers de segurança | **0** | **0** | **1** | **2** |

Scan dos endpoints (`/openapi.json`, `/health` e demais rotas da API): sem alertas High ou Medium. O único alerta Low da etapa anterior (`Cross-Origin-Resource-Policy` ausente) foi corrigido com header (ver Finding 6). **[Confirmar no `zap/relatorio_zap_api.md` do último scan que o alerta sumiu e ajustar esta linha se necessário.]**

Observação sobre a leitura do relatório: no ZAP, `Informational (Medium)` significa **severidade Informational** com **confiança Medium**. A severidade é a primeira parte do texto.

---

## Findings Medium (todos corrigidos)

### Finding 1: CSP permite `unsafe-inline` em `script-src`

- **Finding:** Content Security Policy com `script-src 'unsafe-inline'` (ZAP 10055, CWE-693).
- **Severidade / confiança:** Medium / High.
- **URL afetada:** `/docs` e `/redoc`.
- **Problema:** `'unsafe-inline'` desliga a principal proteção da CSP contra XSS: um script injetado seria executado sem bloqueio do navegador.
- **Causa:** o Swagger UI e o ReDoc padrão do FastAPI usam script inline e CDN, o que obrigava uma CSP relaxada (`CSP_DOCS`).
- **Correção:** o Swagger UI passou a ser servido localmente (`fastapi/static/swagger/`), com um `init.js` externo no lugar do script inline. O `/docs` é uma rota própria em `main.py` e o `/redoc` foi desabilitado (`redoc_url=None`). Em `middlewares.py`, a `CSP_DOCS` foi removida e **todas** as rotas usam a CSP estrita (`script-src 'self'`).
- **Validação:** re-scan sem o alerta; teste automatizado `test_docs_are_served_without_external_resources_or_unsafe_inline`.

### Finding 2: CSP permite `unsafe-inline` em `style-src`

- **Finding:** `style-src 'unsafe-inline'` (ZAP 10055, CWE-693).
- **Severidade / confiança:** Medium / High.
- **URL afetada:** `/docs` e `/redoc`.
- **Problema:** estilos inline injetados podem alterar a interface (por exemplo, sobrepor elementos para enganar o usuário).
- **Correção:** mesma do Finding 1. A CSP estrita usa `style-src 'self'`.
- **Validação:** mesma do Finding 1.

### Finding 3: Sub Resource Integrity (SRI) ausente

- **Finding:** atributo `integrity` ausente em recursos de terceiros (ZAP 90003, CWE-345).
- **Severidade / confiança:** Medium / High.
- **URL afetada:** `/docs` (CSS e JS do jsdelivr) e `/redoc` (fontes do Google e `redoc.standalone.js`).
- **Problema:** se o CDN fosse comprometido, o navegador executaria o código alterado sem verificação.
- **Correção:** a causa foi eliminada: a página não carrega mais nenhum recurso externo. Todos os assets vêm de `/static` (mesma origem), com versão fixa, então SRI deixa de ser necessário.
- **Validação:** o HTML de `/docs` não contém nenhuma URL `http://` ou `https://` (coberto por teste automatizado). O re-scan não reporta o alerta 90003.

### Finding 4: Biblioteca JavaScript vulnerável (DOMPurify 3.1.4 no Swagger UI)

- **Finding:** Vulnerable JS Library (ZAP 10003, CWE-1395).
- **Severidade / confiança:** Medium / Medium.
- **URL afetada:** `/static/swagger/swagger-ui-bundle.js`.
- **Como surgiu:** apareceu no re-scan da etapa 2. Antes, com o Swagger vindo do CDN, o ZAP não analisava o arquivo.
- **Problema:** o `swagger-ui-dist` 5.17.14 embute o DOMPurify 3.1.4, que tem dezenas de vulnerabilidades de XSS conhecidas (por exemplo CVE-2025-26791 e CVE-2025-15599).
- **Correção:** atualização do `swagger-ui-dist` de 5.17.14 para **5.33.2**.
- **Validação:** o retire.js não aponta vulnerabilidades na 5.33.2, e o re-scan do ZAP não reporta mais o alerta.

---

## Findings Low e Informational corrigidos

### Finding 5: Permissions Policy ausente (Low, ZAP 10063)

Corrigido com o header `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()` em todas as respostas.

### Finding 6: Headers de isolamento cross-origin ausentes (Low, ZAP 90004)

Cross-Origin-Embedder-Policy, Cross-Origin-Opener-Policy e Cross-Origin-Resource-Policy. Corrigidos com `Cross-Origin-Embedder-Policy: require-corp`, `Cross-Origin-Opener-Policy: same-origin` e `Cross-Origin-Resource-Policy: same-origin`. Requisições de front-ends por CORS não são afetadas pela política de recursos.

### Finding 7: Conteúdo armazenável em cache (Informational, ZAP 10049)

Corrigido com `Cache-Control: no-store` em todas as respostas. No re-scan o alerta passou a se chamar **Non-Storable Content** (informativo): é a confirmação de que o header surtiu efeito, e não um problema.

Também foi adicionado `Referrer-Policy: no-referrer`. Os headers estão em `fastapi/middlewares.py` e cobertos pelo teste `test_responses_include_hardening_headers`.

---

## Alertas residuais (aceitos, justificados)

| Alerta | Risco | Justificativa |
| --- | --- | --- |
| Timestamp Disclosure - Unix | Low | **Falso positivo.** Os valores apontados em `swagger-ui-bundle.js` (por exemplo `1518500249`, `1732584193`, `1859775393`, `1894007588`) são constantes numéricas de algoritmos de hash embutidas no código minificado da biblioteca, não datas expostas pela aplicação. |
| Modern Web Application | Informational | Apenas informa que o `/docs` é uma SPA. O próprio ZAP indica que nenhuma mudança é necessária. |
| Non-Storable Content | Informational | Efeito esperado do `Cache-Control: no-store` (Finding 7). |

O contador "ZAP warnings logged" do relatório vem do spider tentando acessar `/`, que retorna 404 porque a API não define rota raiz. Não afeta a segurança.

---

## Hardening adicional (auditoria final)

Além dos findings do ZAP, a auditoria corrigiu:

- **Vazamento de hash de senha:** havia uma rota `/me` duplicada em `main.py` que devolvia o usuário sem `response_model`, expondo `hashed_password`. A rota duplicada foi removida; vale a de `routers/router.py`, que usa `UserRead`. Teste: `test_me_does_not_expose_password_hash`.
- **Rate limiting** em `/auth/signin` (10/min), `/auth/signup` (5/min), `/auth/token` e `/predict` (30/min).
- **Validação de entradas:** `username` (3 a 50 caracteres, `[A-Za-z0-9_.-]`), `password` (8 a 72) e `text` (1 a 2000).
- **Segredos e banco:** `SECRET_KEY` aleatório no `.env` (não versionado) e `database.db` fora do git.
- **OpenAPI documentado:** título, descrição, tags, `summary`, `description`, `responses` e exemplos em todas as rotas; `/docs` disponível localmente.

## Prontidão para pentest

- API sobe sem erros: `uvicorn main:app --host 0.0.0.0 --port 8000`.
- Autenticação por JWT funcionando (`/auth/signin` e botão Authorize do `/docs`).
- Dados de teste criados pelo seed: `alice`/`alice123` e `bruno`/`bruno123`.
- Suíte `pytest tests/ -v` com 16 testes passando e integrada ao GitHub Actions.

## Conclusão

- A API **não** tem findings High nem Medium.
- Os 4 findings Medium (CSP em script e estilo, SRI ausente e biblioteca vulnerável) foram **corrigidos na causa**, e não aceitos como risco.
- Restam apenas 1 Low (falso positivo) e 2 Informational, documentados acima.