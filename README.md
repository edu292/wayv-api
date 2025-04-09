# 📊 Wayv API - Integração de Formulários

API desenvolvida em **FastAPI** para integração com a plataforma [Wayv](https://way-v.com/). Permite:

- Upload de planilhas Excel com dados de participantes
- Listagem de participantes cadastrados
- Atualização da data de nascimento
- Remoção completa dos dados

## 🚀 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLite](https://www.sqlite.org/index.html)
- [Pandas](https://pandas.pydata.org/)
- [Uvicorn](https://www.uvicorn.org/) (Servidor ASGI)

## ⚙️ Instalação

<pre lang="bash"><code>git clone https://github.com/seu-usuario/wayv-api.git  
cd wayv-api   
pip install -r requirements.txt  
</code></pre>

## 📂 Endpoints Disponíveis

**POST /upload-excel**  
Envia uma planilha .xlsx com as colunas:  
- `Nome completo`  
- `Data de Nascimento`  
- `Sexo`  
- `E-mail`  
- `Celular`  

<pre lang="bash"><code>bash curl -X 'POST' 
'http://localhost:8000/upload-excel' 
-F 'file=@/caminho/para/arquivo.xlsx' 
</code></pre>
  
**GET /participants?gender=feminino**  
Retorna todos os participantes cadastrados, com opção de filtro por sexo (masculino, feminino, outros).  


**PUT /participants**  
Atualiza a data de nascimento com base em email, nome completo ou telefone.  
<pre lang="json"><code>
  { 
    "identifier": "exemplo@email.com",
    "new_date": "1992-01-15",
    "by": "email"
  }  </code></pre> 


**DELETE /clear**  
Remove todos os registros do banco de dados.  




Acesse a documentação interativa em:  
Swagger UI: http://localhost:8000/docs  
Redoc: http://localhost:8000/redoc  
