from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from . import util
from markdown2 import Markdown
import re, random
from django import forms



class SearchForm(forms.Form):
    """ Form Class for Search Bar """
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "class": "search",
      "placeholder": "Search Qwikipedia"}))

class CreateForm(forms.Form):
    """ Form Class for Creating New Entries """
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "placeholder": "Page Title"}))
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
      "placeholder": "Enter Page Content using Github Markdown"
    }))


def index(request):
    """ Homepage on the website """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def page(request, text):
    """ Displays the requested entry page """

    entry = util.get_entry(text)
    if entry:
        # If entry exists, convert markdown to HTML and return rendered template
        markdowner = Markdown()
        filename = markdowner.convert(entry)
        return render(request, "encyclopedia/page.html", {
                "filename": filename,
                "text":text
            })
    else:
        return render(request, "encyclopedia/error.html", {
            "filename": text
        })


def search(request):
    """ Loads the requested page when queried """

    if request.method == "GET":
        q = request.GET["q"]
        entry = util.get_entry(q)
        # if entry exists, redirect to existing page
        if entry:
            return redirect("entry_page", q)
        # check if entry is a substring of existing page, if so redirect to page
        else:
            entries =  util.list_entries()
            substring = []
            for entry in entries:
                if re.search(q, entry, re.IGNORECASE):
                    substring.append(entry)

            if substring:
                return render(request, "encyclopedia/index.html", {
                "entries": substring
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "filename": q
                })


def new(request):
    """ Lets users create a new page in the encylopedia """

    # If reached via link, display the form:
    if request.method == "GET":
        return render(request, "encyclopedia/new.html", {
          "create_form": CreateForm(),
          "search_form": SearchForm()
        })

    # Otherwise if reached by form submission:
    elif request.method == "POST":
        form = CreateForm(request.POST)

        # If form is valid, process the form:
        if form.is_valid():
          title = form.cleaned_data['title']
          text = form.cleaned_data['text']
        else:
          messages.error(request, 'Entry form not valid, please try again!')
          return render(request, "encyclopedia/new.html", {
            "create_form": form,
            "search_form": SearchForm()
          })

        # Check that title does not already exist:
        if util.get_entry(title):
            messages.error(request, 'This page title already exists! Please go to that title page and edit it instead!')
            return render(request, "encyclopedia/new.html", {
              "create_form": form,
              "search_form": SearchForm()
            })
        # Otherwise save new title file to disk, take user to new page:
        else:
            util.save_entry(title, text)
            messages.success(request, f'New page "{title}" created successfully!')
            return redirect(reverse('entry_page', args=[title]))



def edit(request, text):
    """ Lets users edit an existing page """

    # If reached via post, update page and redirect to page
    if request.method == "POST":
        details = request.POST.get("details")
        util.save_entry(text,details)
        return redirect("entry_page", text)
    else:
        entry = util.get_entry(text)
        context = {
            "text": text,
            "details": entry
        }
        return render(request, "encyclopedia/edit.html", context)

def randomm(request):
    """ Allows users to select a random encylopedia page """

    # Get the list of entries and select one at random, redirect to page
    entries = util.list_entries()
    entry = random.choice(entries)
    return redirect("entry_page", entry)