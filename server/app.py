#!/usr/bin/env python3
from flask import Flask, jsonify, request
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([{'id': r.id, 'name': r.name, 'address': r.address} for r in restaurants])

class RestaurantDetail(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify({
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address,
                'restaurant_pizzas': [rp.to_dict() for rp in restaurant.restaurant_pizzas]
            })
        else:
            return jsonify({'error': 'Restaurant not found'}), 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        else:
            return jsonify({'error': 'Restaurant not found'}), 404

class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'ingredients': p.ingredients} for p in pizzas])

class RestaurantPizzaCreate(Resource):
    def post(self):
        data = request.get_json()
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        price = data.get('price')
        
        if price < 1 or price > 30:
            return jsonify({'errors': ['Price must be between 1 and 30']}), 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if pizza and restaurant:
            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()
            return jsonify(restaurant_pizza.to_dict()), 201
        else:
            return jsonify({'error': 'Pizza or Restaurant not found'}), 404

# Register routes
api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaCreate, '/restaurant_pizzas')

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)