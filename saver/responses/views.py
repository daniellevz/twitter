from django.shortcuts import get_list_or_404, render
from twitter.saver.responses.models import Response

def index(request):
    return render(request, 'responses/index.html')

def client_responses(request, client_id):
    responses = get_list_or_404(Response, client_id=client_id)
    return render(request, 'responses/client_responses.html', {'responses': responses})
