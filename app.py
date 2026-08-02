from fastapi import FastAPI, Body

app = FastAPI()

book: str = ''

@app.post('/book')
def create_book(input_book: str = Body(..., embeded=True)):
    global book
    book = input_book
    return book

@app.get('/book')
def get_book():
    return f'Любимая книга: {book}'