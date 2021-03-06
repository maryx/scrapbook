import os
import requests
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader # This loads the template for html files
from .models import Images
from django.http import Http404
from django.shortcuts import get_object_or_404, render # we can remove the loader if we use this
from django.core.urlresolvers import reverse # this isn't the string reverse()
from django.utils import timezone
from clarifai.client import ClarifaiApi

def index(request):
    recent_image_list = Images.objects.order_by('-date_added')[:5]
    template = loader.get_template('images/index.html') # you get this less convoluted path
    data = {
        'recent_image_list': recent_image_list,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'images/index.html', data); # shorthand

def detail(request, image_id):
    # we're using the built in method instead
    # try:
    #     image = Images.objects.get(pk=image_id)
    # except Images.DoesNotExist:
    #     raise Http404("Image doesn't exist")
    image = get_object_or_404(Images, pk=image_id)
    return render(request, 'images/detail.html', {'image': image})

def tagged(request, tag):
    return HttpResponse("You're looking at the results for the tag %s." % tag)

def create(request):
    # this won't work unless you get a key from Clarifai
    # os.environ["CLARIFAI_APP_ID"] = <id>
    # os.environ["CLARIFAI_APP_SECRET"] = <secret>

    clarifai_api = ClarifaiApi()
    image = Images(date_added=timezone.now())
    try:
        image.img_source = request.POST['img_source']
        image.tags = get_tags(request.POST['tags'].split(', '), image.img_source, clarifai_api)
        image.nsfw_probability = get_nsfw(image.img_source)
    except (KeyError, Images.DoesNotExist):
        return render(request, 'images/index.html', {
            'error_message': 'Error Creating Image',
            })
    else:
        image.save()
        return HttpResponseRedirect(reverse('images:detail', args=(image.id,)))

def edit(request, image_id):
    image = get_object_or_404(Images, pk=image_id)
    try:
        image.img_source = request.POST['img_source']
        image.tags = request.POST['tags']
        image.nsfw_probability = get_nsfw(image.img_source)
    except (KeyError, Images.DoesNotExist):
        return render(request, 'images/detail.html', {
            'image': image,
            'error_message': "Error in Editing Image Data :(",
            })
    else:
        image.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('images:detail', args=(image.id,)))

# tags is a set containing tags from both the user input and the API
def get_tags(input_tags, img_source, clarifai_api):
    tags = set()
    for tag in input_tags:
        tags.add(tag)
    try:
        image_tag_results = clarifai_api.tag_image_urls(img_source)
    except (KeyError):
        print "You don't have authorization to use the Clarifai API."
        return render(request, 'images/index.html', {
            'error_message': 'Error Accessing Clarifai API',
        })
    else:
        # I only have 1 image so [0]
        clarifai_tags = image_tag_results["results"][0]["result"]["tag"]["classes"]

        # If still image, i.e. tag_results = [tag1, tag2]
        if (type(clarifai_tags[0]) is unicode): # unicode is actually str
            for tag in clarifai_tags:
                tags.add(tag)
        else:
            # gif, i.e. tag_results = [[tag1, tag2], [tag3, tag4]] for each frame
            for frame in clarifai_tags:
                for tag in frame:
                    tags.add(tag)

        tags.remove('') # I dunno this gets added sometimes?
        return ', '.join(list(tags))

# curl "https://api.clarifai.com/v1/tag/?model=nsfw-v1.0&url=https://samples.clarifai.com/metro-north.jpg" -H "Authorization: Bearer {access_token}"
def get_nsfw(img_source):
    # Get your own access token
    # access_token = <get your own>

    nsfw = 0
    try:
        req = requests.get("https://api.clarifai.com/v1/tag/?model=nsfw-v1.0&url=" + img_source + "&access_token=" + access_token)
        response = json.loads(req.text)
        print response
        tag_response = response["results"][0]["result"]["tag"]
        if (tag_response["classes"][0] == 'nsfw'):
            nsfw = tag_response["probs"][0] * 100
        else:
            nsfw = tag_response["probs"][1] * 100
    except (KeyError):
        print "Error in getting NSFW number??"
    return nsfw

