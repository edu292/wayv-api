from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import pandas as pd
import io
import sqlite3

def init_db():
    conn = sqlite3.connect("wayv.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            birth_date TEXT,
            gender TEXT,
            email TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class UpdateBirthRequest(BaseModel):
    identifier: str = Field(..., description="Identificador do participante (email, nome completo ou telefone)")
    new_date: str = Field(..., example="1990-05-21", description="Nova data de nascimento no formato YYYY-MM-DD")
    by: Literal["email", "full_name", "phone"] = Field(..., description="Campo usado como chave para atualização")

app = FastAPI(title="Wayv API - Integração de Formulários",
              description="API para upload de participantes via planilha, atualização, listagem e integração com a plataforma Wayv.",
              version="1.0.0"
)

@app.post('/upload-excel',
          tags=['Funcionalidades'],
          summary="Enviar planilha Excel",
          description="Realiza o upload de um arquivo .xlsx com os campos: Nome completo, Data de Nascimento, Sexo, E-mail e Celular.")
async def upload_excel(file: UploadFile = File(...)):
    contents = await file.read()

    df = pd.read_excel(io.BytesIO(contents))
    conn = sqlite3.connect("wayv.db")
    cursor = conn.cursor()
    expected = {"Nome completo", "Data de Nascimento", "Sexo", "E-mail", "Celular"}
    if not expected.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Colunas esperadas: {expected}")
    for _, row in df.iterrows():
        birth = row["Data de Nascimento"]
        if isinstance(birth, pd.Timestamp):
            birth = birth.date().isoformat()
        elif isinstance(birth, str):
            birth = birth.strip()
        cursor.execute("""
                INSERT INTO participants (full_name, birth_date, gender, email, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (
            row["Nome completo"],
            birth,
            row["Sexo"].lower(),
            row["E-mail"],
            row["Celular"]
        ))
    conn.commit()
    conn.close()
    return {'message': 'Dados registrados com sucesso'}

@app.get("/participants",
         tags=['Funcionalidades'],
         summary='Listar Participantes Casdastrados',
         description="Retorna todos os participantes cadastrados. Pode-se aplicar filtro por sexo (masculino, feminino, outros).")
def list_participants(gender: str = None):
    conn = sqlite3.connect("wayv.db")
    cursor = conn.cursor()
    if gender:
        gender = gender.lower()
        cursor.execute("SELECT * FROM participants WHERE gender = ?", (gender,))
    else:
        cursor.execute("SELECT * FROM participants")
    rows = cursor.fetchall()
    conn.close()
    result = [
        {
            "id": row[0],
            "full_name": row[1],
            "birth_date": row[2],
            "gender": row[3],
            "email": row[4],
            "phone": row[5],
        }
        for row in rows
    ]
    return result

@app.put("/participants",
         tags=['Funcionalidades'],
         summary='Alterar Data de Nascimento',
         description="Atualiza a data de nascimento de um participante existente com base em email, full_name ou phone.")
def update_birth(request: UpdateBirthRequest):
    conn = sqlite3.connect("wayv.db")
    cursor = conn.cursor()
    if request.by not in ["email", "full_name", "phone"]:
        raise HTTPException(status_code=400, detail="Campo 'by' inválido")

    query = f"UPDATE participants SET birth_date = ? WHERE {request.by} = ?"
    cursor.execute(query, (request.new_date, request.identifier))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    conn.close()
    return {"message": "Data de nascimento atualizada"}

@app.delete('/clear',
            tags=['Funcionalidades'],
            summary='Limpar Banco de Dados',
            description="Remove todos os dados da base de dados")
def clear_all():
    conn = sqlite3.connect("wayv.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM participants")
    conn.commit()
    conn.close()
    return {"message": "Registros removido com sucesso"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)