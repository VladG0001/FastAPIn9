from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()

DATABASE_URL = "sqlite:///./movies.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class MovieDB(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    director = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)

Base.metadata.create_all(bind=engine)

class Movie(BaseModel):
    id: int
    title: str
    director: str
    release_year: int = Field(..., gt=1888)
    rating: float = Field(..., ge=0, le=10)

    @Field.validator("release_year")
    def check_year(cls, v):
        if v > datetime.now().year:
            raise ValueError("Рік випуску не може бути у майбутньому.")
        return v

@app.get("/movies")
def get_movies():
    with SessionLocal() as db:
        return db.query(MovieDB).all()

@app.post("/movies")
def create_movie(movie: Movie):
    with SessionLocal() as db:
        if db.query(MovieDB).filter_by(id=movie.id).first():
            raise HTTPException(400, "Фільм з таким ID вже існує.")
        new_movie = MovieDB(**movie.dict())
        db.add(new_movie)
        db.commit()
        return new_movie

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    with SessionLocal() as db:
        movie = db.query(MovieDB).filter_by(id=movie_id).first()
        if not movie:
            raise HTTPException(404, "Фільм не знайдено.")
        return movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    with SessionLocal() as db:
        movie = db.query(MovieDB).filter_by(id=movie_id).first()
        if not movie:
            raise HTTPException(404, "Фільм не знайдено.")
        db.delete(movie)
        db.commit()
        return {"message": "Фільм видалено."}
