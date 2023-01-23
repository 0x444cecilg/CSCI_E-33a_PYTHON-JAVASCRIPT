from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate(request, postings):
    page = request.GET.get('page', 1)
    paginator = Paginator(postings, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return posts