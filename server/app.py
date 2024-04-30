#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantClass(Resource):
    def get(self):
        restaurants = [
            restaurant.to_dict(rules=("-restaurant_pizzas",))
            for restaurant in Restaurant.query.all()
        ]
        return make_response(restaurants, 200)


api.add_resource(RestaurantClass, "/restaurants")


class RestaurantById(Resource):
    def get(self, id):
        res = Restaurant.query.filter_by(id=id).one_or_none()

        if res is not None:
            return make_response(res.to_dict(), 200)
        else:
            return make_response({"error": "Restaurant not found"}, 404)

    def delete(self, id):
        res = Restaurant.query.filter_by(id=id).one_or_none()

        if res is None:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(res)
        db.session.commit()
        return make_response({}, 204)


api.add_resource(RestaurantById, "/restaurants/<int:id>")


class PizzasClass(Resource):
    def get(self):
        pizzas = [
            pizza.to_dict(only=("id", "ingredients", "name"))
            for pizza in Pizza.query.all()
        ]
        return make_response(pizzas, 200)


api.add_resource(PizzasClass, "/pizzas")


class RestaurantPizzasClass(Resource):
    def post(self):
        # import ipdb; ipdb.set_trace()
        try:
            new_pizza = RestaurantPizza(
                price=request.get_json()["price"],
                pizza_id=request.get_json()["pizza_id"],
                restaurant_id=request.get_json()["restaurant_id"],
            )
            db.session.add(new_pizza)
            db.session.commit()

            return make_response(new_pizza.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(RestaurantPizzasClass, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)