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
    for item in menu_items:
        food_items.append({
            'food': item.get('food', ''),
            'price': item.get('price', 0),
            'description': item.get('description', '')
        })

    
    
    
    return render_template("home.html", user=current_user, food_items=food_items)



@pages.route('/checkout', methods=['POST'])
@login_required
def checkout():
    try:
        data = request.json
        food_items = data.get('food_items')  # Corrected to match the JS code
        amount = data.get('amount')


        for food in food_items:
            new_product = Product(
                item_name=food,
                status=UserStatusEnum.ORDER_RECEIVED,  # Assuming the status starts with "order received"
                price=float(amount) / len(food_items)  # Distribute the total amount equally (this can be adjusted)
            )
            # Associate the product with the current user
            current_user.products.append(new_product)

        # Commit the changes to the database
        db.session.commit()

        if not food_items or not amount:
            raise ValueError("Invalid data received")

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






@pages.route('/success')
@login_required
def success():
    return render_template('success.html')


@pages.route('/cancel')
@login_required
def cancel():
    return render_template('cancel.html')
