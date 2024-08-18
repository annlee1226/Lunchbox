from flask import Blueprint, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from .data import User, Product, UserStatusEnum
from . import db
import json
import requests
import os
import stripe
from dotenv import load_dotenv

load_dotenv()
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY

pages = Blueprint('pages', __name__)


@pages.route('/', methods=['GET', 'POST'])
@login_required
def home():
    response = requests.get("https://menu-api.vercel.app/api/menu")
    menu_items = response.json()
    food_items = []

    for restaurant in menu_items:
        restaurant_name = restaurant.get('restaurant', '')
        menu = restaurant.get('menu', [])
        for item in menu:
            food = item.get('name', '')
            price = item.get('price', 0)
            description = item.get('description', '')

            # Check if the product already exists in the database
            existing_product = Product.query.filter_by(item_name=food).first()

            if not existing_product:
                # Add the product to the database if it doesn't exist
                new_product = Product(
                    item_name=food,
                    price=price,
                    status=UserStatusEnum.ORDER_RECEIVED,  # Default status for new products
                    user_id=None, # Not associated with any user yet
                    restaurant=restaurant_name
                )
                db.session.add(new_product)
                db.session.commit()

            # Add the item to the food_items list for rendering in the template
            food_items.append({
                'food': food,
                'price': price,
                'description': description
            })

    return render_template("home.html", user=current_user, food_items=food_items)

@pages.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        data = request.json
        food_items = data.get('food_items')  # Corrected to match the JS code
        amount = data.get('amount')

        # Ensure that the food_items and amount are valid
        if not food_items or not amount:
            raise ValueError("Invalid data received")

        for food in food_items:
    # Find the existing product by item name (not associated with any user)
            existing_product = Product.query.filter_by(item_name=food, user_id=None).first()
    
            if existing_product:
        # Update the existing product's status, price, and associate it with the current user
                existing_product.status = UserStatusEnum.ORDER_RECEIVED
                existing_product.user_id = current_user.id  # Associate the product with the current user's ID

        db.session.commit()

        # Create a new Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': ', '.join(food_items),  # Combine all selected items into one string
                    },
                    'unit_amount': int(float(amount) * 100),  # Convert amount to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('pages.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('pages.cancel', _external=True),
        )

        return jsonify({'checkout_url': checkout_session.url})

    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return a 400 status code for errors


@pages.route('/command', methods=['GET'])
def handle_command():
    # Get the command, order ID, and new status from the query parameters
    command = request.args.get('command')
    order_id = request.args.get('order_id')
    new_status = request.args.get('status')

    # Check if the command is "updateOrder"
    if command == "updateOrder":
        try:
            # Convert the status to the UserStatusEnum
            status_enum = UserStatusEnum(new_status)

            # Find the order in the database
            order = Product.query.filter_by(id=order_id).first()

            if order:
                # Update the order's status
                order.status = status_enum
                db.session.commit()

                return jsonify({"message": "Order status updated successfully"}), 200
            else:
                return jsonify({"error": "Order not found"}), 404

        except ValueError as e:
            return jsonify({"error": f"Invalid status: {new_status}"}), 400

    return jsonify({"error": "Invalid command"}), 400




@pages.route('/success')
@login_required
def success():
    user_products = current_user.products
    return render_template('success.html', products=user_products, user=current_user)


@pages.route('/cancel')
@login_required
def cancel():
    return render_template('cancel.html')
