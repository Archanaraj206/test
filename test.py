#test.py

from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel
from typing import List qsdxwdw

app = FastAPI()

# MySQL Database Setup
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="ash123",
    database="my_db"
)
cursor = conn.cursor()

# Pydantic model for message insertion
class Message(BaseModel):
    role: str
    content: str

# Endpoint to insert messages into the database
@app.post("/insert_message/")
async def insert_message(message: Message):
    try:
        cursor.execute(''' 
            INSERT INTO messages (role, content)
            VALUES (%s, %s)
        ''', (message.role, message.content))
        conn.commit()
        return {"status": "success", "message": "Message inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to get all messages from the database
@app.get("/get_messages/")
async def get_messages():
    try:
        cursor.execute('SELECT * FROM messages')
        messages = cursor.fetchall()
        return {"messages": [{"role": msg[1], "content": msg[2]} for msg in messages]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to get flight price by date (e.g., 'January 2')
@app.get("/get_flight_price/{date}")
async def get_flight_price(date: str):
    try:
        cursor.execute(''' 
            SELECT * FROM flight_price WHERE date = %s
        ''', (date,))
        price_info = cursor.fetchone()
        if price_info:
            return {
                "date": price_info[0],
                "price": price_info[1]
            }
        else:
            raise HTTPException(status_code=404, detail=f"Price not found for {date}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to get laptop details along with components
@app.get("/get_laptop_details/{laptop_id}")
async def get_laptop_details(laptop_id: int):
    try:
        cursor.execute('''
            SELECT laptops.brand, laptops.model, laptops.variant, laptops.release_year, laptops.price,
                   components.name, laptop_components.value, laptop_components.additional_info
            FROM laptops
            JOIN laptop_components ON laptops.id = laptop_components.laptop_id
            JOIN components ON laptop_components.component_id = components.id
            WHERE laptops.id = %s
        ''', (laptop_id,))
        laptop_info = cursor.fetchall()

        if laptop_info:
            laptop_data = {
                "brand": laptop_info[0][0],
                "model": laptop_info[0][1],
                "variant": laptop_info[0][2],
                "release_year": laptop_info[0][3],
                "price": laptop_info[0][4],
                "components": []
            }
            for row in laptop_info:
                component_data = {
                    "component_name": row[5],
                    "value": row[6],
                    "additional_info": row[7]
                }
                laptop_data["components"].append(component_data)

            return laptop_data
        else:
            raise HTTPException(status_code=404, detail="Laptop not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Close the MySQL connection when the application shuts down
@app.on_event("shutdown")
def shutdown():
    cursor.close()
    conn.close()
