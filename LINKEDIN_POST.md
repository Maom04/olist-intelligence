# LinkedIn — Olist Intelligence

Transformei uma base real de e-commerce em um projeto completo de dados, do dado bruto ao insight.

No **Olist Intelligence**, trabalhei com o Brazilian E-Commerce Public Dataset by Olist e construí um pipeline reproduzível em Python/Pandas para tratar e validar:

- 99.441 pedidos
- 112.650 itens
- 96.096 clientes únicos
- 32.951 produtos
- 3.095 vendedores

A camada analítica foi modelada em duas granularidades:

- `orders_analytics`: 1 linha por pedido
- `items_analytics`: 1 linha por item vendido

Antes de levar os dados para o Power BI, adicionei validações de integridade, conciliação de valores, auditoria de pagamentos e detecção de divergências financeiras.

Alguns números do dashboard:

- R$ 13,22 milhões de GMV em pedidos entregues
- 96.478 pedidos entregues
- R$ 137,04 de ticket médio
- avaliação média de 4,16
- taxa de atraso de 6,8%

Também adicionei uma camada de **Machine Learning/NLP** sobre os comentários reais dos clientes.

Foram analisados **40.604 reviews com texto**, usando:

- TF-IDF
- classificação de sentimento
- SGDClassifier
- NMF para descoberta de tópicos

O modelo de sentimento alcançou **83,7% de acurácia** no conjunto de teste, usando como referência rótulos derivados das próprias notas dos reviews (1–2 negativo, 3 neutro, 4–5 positivo).

Um dos insights que mais chamou atenção:

**Pedidos entregues no prazo: nota média 4,29**
**Pedidos atrasados: nota média 2,27**

Uma diferença de aproximadamente **2,02 pontos**, mostrando o impacto que a logística pode ter na experiência do cliente.

Stack utilizada:

**Python | Pandas | NumPy | Scikit-learn | TF-IDF | NMF | Parquet | Power BI | DAX**

O objetivo do projeto não foi apenas criar um dashboard bonito, mas construir um fluxo de dados que eu pudesse auditar, reproduzir e explicar de ponta a ponta.

#DataAnalytics #Python #Pandas #PowerBI #MachineLearning #DataScience #BusinessIntelligence #NLP #Portfolio

## Imagens recomendadas para o post

1. `assets/executive_overview.png`
2. `assets/customer_ai_intelligence.png`

Use as duas imagens no mesmo post. A primeira apresenta o dashboard executivo; a segunda mostra a camada de IA/NLP.
