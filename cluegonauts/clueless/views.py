from django.shortcuts import render

from .classes import CharacterHandler

def index(request):
    print(f"Char handler: {request.session.get('char_handler', None)}")
    char_handler = CharacterHandler(selected=request.session.get("char_handler", None)) if request.session.get("char_handler", None) else CharacterHandler()
    char_choices = char_handler.get_all_characters()
    return render( 

        request, 
        "clueless/index.html",
        {"char_choices": char_choices}
        )

#TODO: WIP
def select_character(request):
    """
    Store selected characters in session
    """
    char_id = request.POST.get("char_id")
    char_handler = CharacterHandler(selected=request.session.get("char_handler", None)) if request.session.get("char_handler", None) else CharacterHandler()
    if char_handler.is_available(char_id):
        char_handler.set_selected(char_id)
        request.session["char_handler"] = char_handler.serialize_selected()
        request.session.save()
    return render(request, "clueless/index.html", {"char_choices": char_handler.get_all_characters()})

def gameb(request):
    return render(request, "clueless/gameb.html")
