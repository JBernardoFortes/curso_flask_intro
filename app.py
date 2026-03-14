from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

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


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


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


if __name__ == "__main__":
    app.run(debug=True)
