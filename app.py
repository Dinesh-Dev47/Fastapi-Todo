from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas

from database import engine, get_db,Base

app = FastAPI(title="Todo Management API")

# Create database tables
Base.metadata.create_all(bind=engine)


# 1. Create Todo
@app.post("/todos/", response_model=schemas.TodoResponse)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):

    try:
        new_todo = models.Todo(
            title=todo.title,
            description=todo.description
        )

        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)

        return new_todo

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 2. Get All Todos
@app.get("/todos/", response_model=list[schemas.TodoResponse])
def get_todos(db: Session = Depends(get_db)):

    todos = db.query(models.Todo).all()

    return todos


# 3. Get Todo By ID
@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):

    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo


# 4. Update Todo
@app.put("/todos/{todo_id}")
def update_todo(
    todo_id: int,
    updated_todo: schemas.TodoUpdate,
    db: Session = Depends(get_db)
):
    try:
        todo = db.query(models.Todo).filter(
            models.Todo.id == todo_id
        ).first()

        if not todo:
            raise HTTPException(
                status_code=404,
                detail="Todo not found"
            )

        data = updated_todo.model_dump(exclude_unset=True)

        # Update todo fields
        for key, value in data.items():
            setattr(todo, key, value)

        # If completed is True, delete todo
        if todo.completed is True:
            db.delete(todo)
            db.commit()

            return {
                "message": "Todo completed and deleted successfully"
            }

        db.commit()
        db.refresh(todo)

        return todo

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 5. Delete Todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):

    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}