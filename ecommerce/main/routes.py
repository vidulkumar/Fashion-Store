from flask import Blueprint, render_template, jsonify, request
from ecommerce import mongo
from flask_login import current_user
from bson.objectid import ObjectId
import json
from bson.json_util import dumps

main = Blueprint('main', __name__)


def ret_brands(type):
  brands = mongo.db.items.distinct('Brand', {'Type': type})
  return brands


@main.route('/', defaults={'type': 'Shirt'})
@main.route('/<string:type>')
def home(type):
  mongo.db.items.find_one_or_404({'Type': type.title()}) #just to return 404 error if there is not a single item with that thing 
  items = mongo.db.items.find({'Type': type.title()})
  
  brands = ret_brands(type)
  types = mongo.db.items.distinct('Type')
  return render_template('home.html', items=items, brands=brands, type=type.title(), types=types)

@main.route('/newhome')
def newhome():
  itemsb = mongo.db.items.find({'Type': 'Bedsheet'}).limit(12)
  itemst = mongo.db.items.find({'Type': 'Top'}).limit(12)
  itemsd = mongo.db.items.find({'Type': 'Dress'}).limit(12)
  itemss = mongo.db.items.find({'Type': 'Shirt'}).limit(12)

  return render_template('newhome.html', itemsb=itemsb, itemst=itemst, itemsd=itemsd, itemss=itemss)



@main.route('/items/filter', methods=['POST'])
def filter():
  minDiscount=0
  maxPrice=3000
  print('here')
  print(request.json)
  brands=request.json['Brand']
  if(request.json["Price"]):
    maxPrice=100
    for price in request.json['Price']:
         maxPrice=max(maxPrice,price)
  if(request.json["Discount"]):
    minDiscount=100
    for discount in request.json['Discount']:
      minDiscount=min(minDiscount,discount)
  print('maxPrice is ',maxPrice)
  items=mongo.db.items.find(
    {'$and':[
      {'$or':brands},
      {'Price':{'$lte':maxPrice}},
      {'Discount':{'$gte':minDiscount}}
    ]
    })
  # for item in items:
  #   print(item['Brand'],item['Price'],item['Discount'])

  return(dumps(items))
  

@main.route('/item/<string:item_id>')
def item(item_id):
  item = mongo.db.items.find_one_or_404({"_id": ObjectId(item_id)})
  reviews_exist = mongo.db.review.find({'item_id': ObjectId(item_id)}, {'_id': 0, 'reviews': 1}).count()
  similar_products = mongo.db.items.find({'Category': item['Category'], 'Type': item['Type']}).limit(10)
  if reviews_exist:
    reviews_dict_cursor = mongo.db.review.aggregate([{'$project':
                                                      {
                                                          'rating_avg': {'$avg': '$reviews.rating'},
                                                          'number': {'$size': '$reviews'},
                                                          'reviews': '$reviews'
                                                      }
                                                      }])
  else:
    reviews_dict_cursor = None
  return render_template('item.html', item=item, reviews_cursor=reviews_dict_cursor, title=item['Description'], similar_products=similar_products)


@main.route('/search_results', methods=['POST'])
def search():
  search_input = request.form['search']
  search_result_count = mongo.db.items.find({'$text': {'$search': search_input}}).count()
  if search_result_count:
    search_results = mongo.db.items.find({'$text': {'$search': search_input}})
  else:
    search_results = None
  return render_template('search.html', count=search_result_count, search_results=search_results)


@main.route('/seller')
def seller():
  return render_template('sellerdashboard.html')
