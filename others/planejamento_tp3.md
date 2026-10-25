## Planejamento TP3. Modelo de Classificação e Teste Adversarial

Este documento apresenta o planejamento da próxima etapa do projeto: desenvolver um modelo de classificação de intenção para substituir o mock da rota `POST /predict` e definir o alvo autorizado para os testes adversariais do TP4/TP5.

## 1. Modelo candidato

**Algoritmo escolhido: Regressão Logística multiclasse.**

Motivos:

- **Compatível com a API atual.** A rota `/predict` já retorna o campo `confidence` (`PredictResponse.confidence`). A Regressão Logística calcula probabilidades por meio de `predict_proba`, permitindo usar esses valores diretamente nesse campo, sem precisar de uma etapa extra de calibração.
- **Classes relativamente equilibradas.** A análise univariada do TP2 mostrou que `Ticket Type`, uma opção natural para a variável que o modelo deve prever, está bem distribuída entre as categorias, sem uma classe dominante. Isso favorece o uso de um classificador linear simples, sem a necessidade de técnicas de balanceamento.
- **Treinamento rápido e fácil interpretação.** Como a base tem cerca de 8.469 linhas, o treinamento é rápido, mesmo sem GPU. Além disso, os coeficientes ajudam a entender por que o modelo escolheu determinada intenção, mostrando, por exemplo, quais palavras tiveram mais influência na classificação como "Cancellation request".
- **Alternativa considerada, mas deixada de lado por enquanto: SVM (`LinearSVC`).** Esse algoritmo também apresenta bons resultados na classificação de textos, mas não gera probabilidades diretamente. Para preencher o campo `confidence`, seria necessário adicionar uma etapa de calibração, como `CalibratedClassifierCV`. Isso aumentaria a complexidade sem trazer uma vantagem clara nesta etapa.

### 1.1 Objetivo, variáveis e distribuição das classes

O objetivo é desenvolver um modelo de classificação capaz de prever automaticamente a categoria de um atendimento a partir da descrição escrita pelo cliente. Esse modelo substituirá o comportamento simulado (*mock*) da rota `POST /predict`, mantendo o formato de resposta esperado pela API, incluindo a classe prevista e a confiança da previsão.

**Formulação do problema:**

- **Tipo de aprendizado:** supervisionado, pois a base possui rótulos conhecidos na coluna `Ticket Type`, que serão utilizados como respostas esperadas durante o treinamento.
- **Tipo de tarefa:** classificação multiclasse, pois o modelo deverá escolher entre cinco categorias de atendimento.
- **Variável de entrada (X):** `Ticket Description`, que contém a descrição textual do problema relatado pelo cliente.
- **Variável-alvo (y):** `Ticket Type`, que identifica a categoria do atendimento.
- **Base utilizada:** `data/customer_support_tickets.csv`, com 8.469 registros e 17 colunas.

A distribuição observada da variável-alvo é apresentada a seguir:

| Classe (`Ticket Type`) | Quantidade | Percentual |
|---|---:|---:|
| Refund request | 1.752 | 20,69% |
| Technical issue | 1.747 | 20,63% |
| Cancellation request | 1.695 | 20,01% |
| Product inquiry | 1.641 | 19,38% |
| Billing inquiry | 1.634 | 19,29% |
| **Total** | **8.469** | **100,00%** |

As classes apresentam distribuição relativamente equilibrada: os percentuais variam de 19,29% a 20,69%, sem predominância expressiva de uma única categoria. Esse resultado favorece a avaliação comparativa entre classes, embora não dispense a análise de métricas individuais, como precisão (*precision*), revocação (*recall*) e F1-score.

A definição de `Ticket Description` como entrada e `Ticket Type` como alvo estabelece o problema de classificação a ser desenvolvido. Antes do treinamento, será necessário verificar a qualidade dos textos e dos rótulos, definir a separação entre treino e teste e evitar vazamento de dados (*data leakage*). A avaliação deverá considerar métricas globais e por classe, além da compatibilidade entre as probabilidades produzidas pelo modelo e o campo `confidence` da API.

### 1.2 Etapas de treinamento e avaliação

A implementação do modelo deverá seguir estas etapas:

1. **Preparação dos dados:** verificar os registros, a descrição dos atendimentos (`Ticket Description`) e a variável-alvo (`Ticket Type`), tratando possíveis valores ausentes ou inconsistentes.
2. **Divisão da base:** separar os dados em conjuntos de treinamento e teste, mantendo, se possível, a proporção das classes em cada conjunto. O conjunto de teste não deverá ser usado durante o treinamento.
3. **Representação do texto:** transformar as descrições em valores numéricos usando o `CountVectorizer`.
4. **Treinamento:** ajustar a Regressão Logística multiclasse com os dados de treinamento.
5. **Avaliação:** medir o desempenho com métricas como acurácia, precisão, recall e F1-score. Também será analisada a matriz de confusão para identificar quais classes o modelo costuma confundir.
6. **Análise das probabilidades:** verificar os valores retornados por `predict_proba` e como eles serão usados no campo `confidence` da API. Esses valores representam as probabilidades estimadas pelo modelo e não garantem, por si só, que ele esteja bem calibrado.
7. **Integração com a API:** substituir o mock da rota `POST /predict` pelo modelo treinado, mantendo o formato de resposta esperado pela aplicação.
8. **Registro dos resultados:** documentar as métricas, os parâmetros utilizados, a divisão dos dados e as limitações identificadas, permitindo comparar os resultados com versões futuras do modelo.

Os resultados da avaliação serão usados para decidir se o modelo está adequado para a próxima etapa ou se precisa de ajustes antes dos testes adversariais.

## 2. Estratégia de representação do texto

**Técnica escolhida: `CountVectorizer` (scikit-learn).**

Motivos:

- **Simples e sem dependências extras.** Transforma o texto livre (`Ticket Description`) em uma matriz com a contagem das palavras, usando a técnica bag-of-words. Não depende de embeddings pré-treinados nem de infraestrutura adicional.
- **Combina com a Regressão Logística.** Funciona bem na classificação de textos curtos, tem treinamento rápido e é fácil de analisar, pois cada coluna representa uma palavra do vocabulário. Também serve como modelo inicial antes de testar técnicas mais avançadas, como TF-IDF e embeddings.
- **Adequado aos textos da base.** As descrições de `Ticket Description` são curtas e usam linguagem natural de atendimento. Para o primeiro modelo, não é necessário identificar relações complexas entre os significados das palavras. A contagem já deve identificar boa parte das informações importantes, como termos relacionados a "cancelar", "reembolso" e "não funciona".
- **Parâmetros definidos durante a implementação.** Os ajustes de `stop_words`, `ngram_range`, `min_df` e `max_df` serão feitos durante o desenvolvimento do modelo e não fazem parte deste planejamento.

## 3. Alvo para o teste adversarial (TP4/TP5)

**Endereço gerado via Cloudflare Tunnel (temporário):**

```
https://diagram-menu-ferry-lot.trycloudflare.com
```

- **Como foi gerado:** a API roda em um container Docker (`fastapi/Dockerfile`), sem nenhuma porta exposta diretamente no host. Um segundo container (`cloudflare/cloudflared`), definido em `docker-compose.yml`, conecta-se à API pela rede interna do Docker e abre um túnel de saída (outbound) criptografado até a Cloudflare, que publica a URL acima. Conforme a documentação da Cloudflare, a conexão utiliza troca de chaves pós-quântica.
- **Validação:** no momento da geração, uma requisição `GET /health` para a URL acima retornou `200 {"status":"Funcionando..."}`.
- **Natureza temporária:** como foi usado um túnel rápido (`cloudflared tunnel --url`, sem conta ou domínio), a URL só funciona enquanto os containers estiverem em execução e muda a cada nova execução. Os containers foram derrubados logo após a validação para reduzir o tempo de exposição. Este documento serve como evidência de que a configuração funciona, conforme solicitado para o TP3.
- **Pendência para o TP4/TP5:** antes dos testes adversariais reais, a equipe deverá iniciar os containers novamente, gerar uma URL válida para o período dos testes, atualizar este documento com o endereço vigente e registrar a autorização explícita da equipe adversária para realizar os testes nesse endereço.

Os testes deverão ser realizados apenas no endereço autorizado e durante o período definido pela equipe.



