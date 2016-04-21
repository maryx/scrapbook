from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader # This loads the template for html files
from .models import Images
from django.http import Http404
from django.shortcuts import get_object_or_404, render # we can remove the loader if we use this
from django.core.urlresolvers import reverse # this isn't the string reverse()

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

def edit(request, image_id):
    image = get_object_or_404(Images, pk=image_id)
    print 'hi'
    try:
        print 'heyy in here'
        print request.POST['img_source']
        #print request.POST['tagged']
        image.img_source = request.POST['img_source']
        image.tags = request.POST['tags']
        print image.img_source
        print image.tags
        # image.nsfw_probability = request.POST['nsfw_probability']
        print 'still in here'
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

