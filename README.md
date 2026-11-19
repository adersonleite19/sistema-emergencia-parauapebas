# Sistema de Resposta Pós-Sismo — Parauapebas

Aplicação web GIS para registo, visualização e apoio à resposta a ocorrências de emergência em Parauapebas, com cálculo de distância e tempo estimado até quartéis de bombeiros e hospitais.

## Funcionalidades
- Visualização interativa no mapa com **Leaflet.js** e marcadores personalizados (UIcons/Flaticon).
- Registo de novas ocorrências com descrição, rua, ponto de referência, severidade, horário e coordenadas (`latitude` e `longitude`).
- Remoção de ocorrências diretamente pelo painel operacional.
- Cálculo automático da unidade de socorro mais próxima (quartéis ou hospitais), distância em km e tempo estimado.
- Persistência dos dados em ficheiro `dados.json`.

## Tecnologias utilizadas
- **Backend:** Python (`http.server`)
- **Frontend:** HTML, CSS, JavaScript e Leaflet.js
- **Armazenamento:** JSON (`dados.json`)

## Como executar localmente
1. Clone o repositório:
   ```bash
   git clone [https://github.com/adersonleite19/sistema-emergencia-parauapebas.git](https://github.com/adersonleite19/sistema-emergencia-parauapebas.git)
   cd sistema-emergencia-parauapebas
