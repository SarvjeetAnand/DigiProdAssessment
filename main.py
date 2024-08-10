from fastapi import FastAPI, Response, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
import model as mo
import schema as sc
#from mangum import Mangum

sc.Base.metadata.create_all(bind=engine)
app = FastAPI()
#handler = Mangum(app)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def root():
    return {"Hello":"World"}

@app.post('/products/')
def createProduct(product : mo.Product, response : Response, db : Session = Depends(get_db)):
    db_product = sc.Product(id=product.id,name=product.name,price=product.price,stock=product.stock)
    try:
        db.add(db_product)
        db.flush()
    except IntegrityError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.body = {"error" : "Product with id already exists."}
        db.rollback()
    else:
        db.commit()
        response.status_code = status.HTTP_201_CREATED

'''
DELETE /products/{id}: Delete a product by ID.
'''

@app.get('/products/',response_model=list[mo.Product])
def getProduct(db : Session = Depends(get_db)):
    products = db.query(sc.Product).all()
    return products

@app.get('/products/{id}',response_model=mo.Product)
def getProduct(id : int,response : Response, db : Session = Depends(get_db)):
    product = db.query(sc.Product).filter(sc.Product.id == id).first()
    if product is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    return product

@app.put('/products/{id}')
def updateProduct(id : int, product_req : mo.Product, response : Response, db : Session = Depends(get_db)):
    product_db = db.query(sc.Product).filter(sc.Product.id == id).first()
    if product_db is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    if product_req.name is not None and product_req.name != '':
        product_db.name = product_req.name
    
    if product_req.price is not None and product_req.price > -1:
        product_db.price = product_req.price
    
    if product_req.stock is not None and product_req.stock > -1:
        product_db.stock = product_req.stock
    
    db.flush()

    db.commit()
    response.status_code = status.HTTP_200_OK

@app.delete('/products/{id}')
def deleteProduct(id : int,response : Response, db : Session = Depends(get_db)):
    product_db = db.query(sc.Product).filter(sc.Product.id == id).first()
    print(product_db)
    if product_db is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    db.delete(product_db)
    db.commit()
    response.status_code = status.HTTP_200_OK