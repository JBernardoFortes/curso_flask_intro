from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SECRET_KEY"] = "minha_chave_123"

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = "login"
CORS(app)

# modelagem
# product(id,name,price, description)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    cart = db.relationship("CartItem", backref="user", lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username"))[0]
    if not user:
        return jsonify({"message": "User not found"}), 400

    if data.get("password") != user.password:
        return jsonify({"message": "Incorrect password"}), 401

    login_user(user)
    return jsonify({"message": "Login successfully"}), 200


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logout successfully"}), 200


@app.route("/")
def hello_world():
    return "Hello World"


@app.route("/api/products/add", methods=["POST"])
@login_required
def add_product():
    data = request.json
    if "name" in data and "price" in data:
        product = Product(
            name=data["name"],
            price=data["price"],
            description=data.get("description", ""),
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product created"}), 200
    return jsonify({"message": "Invalid Product data"}), 400


@app.route("/api/products/delete/<int:product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id):
    # recuperar o produto
    # Verificar se ele existe
    # Se ele existir, deletar
    # Se ele nao existir, retornar 404
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted"}), 200
    return jsonify({"message": "Product not found"}), 404


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return (
            jsonify(
                {
                    "id": product.id,
                    "price": product.price,
                    "description": product.description,
                }
            ),
            200,
        )

    return jsonify({"message": "Product not found"}), 404


@app.route("/api/products/update/<int:product_id>", methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    if "name" in data:
        product.name = data["name"]
    if "price" in data:
        product.price = data["price"]
    if "description" in data:
        product.description = data["description"]
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200


@app.route("/api/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    response = []
    for product in products:
        product_data = {
            "name": product.name,
            "price": product.price,
        }
        response.append(product_data)

    return jsonify(response), 200


@app.route("/api/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_item_to_cart(product_id):

    product = Product.query.get(int(product_id))

    if not product:
        return jsonify({"message": "Invalid product"}), 404

    user = User.query.get(int(current_user.id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    cart_item = CartItem(user_id=user.id, product_id=product.id)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({"message": "Product added to cart successfully"}), 200


@app.route("/api/cart/remove/<int:product_id>", methods=["DELETE"])
@login_required
def remove_item_from_cart(product_id):

    if not product_id:
        return jsonify({"message": "Product not found"}), 400

    cart_item = CartItem.query.filter_by(
        user_id=int(current_user.id), product_id=product_id
    )[0]

    if not cart_item:
        return jsonify({"message": "Item not found in cart"}), 400

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({"message": "Item removed from cart successfully"}), 200


@app.route("/api/cart", methods=["GET"])
@login_required
def get_cart():
    user = User.query.get(int(current_user.id))
    if not user:
        return jsonify({"message": "User not found"}), 400

    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append(
            {
                "id": cart_item.id,
                "user_id": cart_item.user_id,
                "product": {
                    "product_id": cart_item.product_id,
                    "product_name": product.name,
                    "product_price": product.price,
                },
            }
        )
    return jsonify(cart_content), 200


@app.route("/api/cart/checkout", methods=["POST"])
@login_required
def checkout_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)

    db.session.commit()
    return jsonify({"message":"Checkout made with success"}), 200


if __name__ == "__main__":
    app.run(debug=True)
