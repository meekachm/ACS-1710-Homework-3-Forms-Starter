from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
from dotenv import load_dotenv
import json
import os
import random
import requests

load_dotenv()


app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""
    num_compliments = int(request.args.get('num_compliments'))
    compliments = random.sample(list_of_compliments, num_compliments)

    context = {
        # TODO: Enter your context variables here.
        'user_name': request.args.get('users_name'),
        'wants_compliments': request.args.get('wants_compliments'),
        'compliments': compliments,
    }

    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.'
}

@app.route('/animal_facts')
def animal_facts():
    """Show a form to choose an animal and receive facts."""

    # TODO: Collect the form data and save as variables
    animal = request.args.get('animal')
    context = {
        # TODO: Enter your context variables here for:
        # - the list of all animals (get from animal_to_fact)
        # - the chosen animal fact (may be None if the user hasn't filled out the form yet)
        'animals': animal_to_fact.keys(),
        'animal_fact': animal_to_fact.get(animal)
    }
    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to 
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    
    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""
    filter_types = filter_types_dict.keys()

    if request.method == 'POST':
        
        # TODO: Get the user's chosen filter type (whichever one they chose in the form) and save
        # as a variable
        # HINT: remember that we're working with a POST route here so which requests function would you use?
        filter_type = request.form.get('filter_type')
        image = request.files.get('users_image')
        image_path = save_image(image, filter_type)
        apply_filter(image_path, filter_type)
        
        # Get the image file submitted by the user
        image = request.files.get('users_image')

        # TODO: call `save_image()` on the image & the user's chosen filter type, save the returned
        # value as the new file path

        # TODO: Call `apply_filter()` on the file path & filter type

        image_url = f'./static/images/{image.filename}'

        context = {
            # TODO: Add context variables here for:
            # - The full list of filter types
            # - The image URL
            'filter_types': filter_types,
            'image_url': image_url,
        }

        return render_template('image_filter.html', **context)

    else: # if it's a GET request
        context = {
            # TODO: Add context variable here for the full list of filter types
            'filter_types': filter_types,
        }
        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################

"""You'll be using the Tenor API for this next section. 
Be sure to take a look at their API. 

https://tenor.com/gifapi/documentation

Register and make an API key for yourself. 
Set up dotenv, create a .env file and define a variable 
API_KEY with a value that is the api key for your account. """


API_KEY = os.getenv('API_KEY')

TENOR_URL = 'https://tenor.googleapis.com/v2/search?'
pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        # TODO: Get the search query & number of GIFs requested by the user, store each as a 
        # variable
        search_query = request.form['search_query']
        quantity = request.form['quantity']

        response = requests.get(
            TENOR_URL,
            {
                # TODO: Add in key-value pairs for:
                # - 'q': the search query
                # - 'key': the API key (defined above)
                # - 'limit': the number of GIFs requeste
                'q': search_query,
                'key': API_KEY,
                'limit': quantity
            })

        gifs = json.loads(response.content).get('results')

        context = {
            'gifs': gifs
        }

         # Uncomment me to see the result JSON!
        # Look closely at the response! It's a list
        # list of data. The media property contains a 
        # list of media objects. Get the gif and use it's 
        # url in your template to display the gif. 
        # pp.pprint(gifs)

        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)