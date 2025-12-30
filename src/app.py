from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/{param}")
async def root(param):
    return {'message': param}

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)