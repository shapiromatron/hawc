from django import template

register = template.Library()


@register.inclusion_tag("common/dropdown_button.html")
def dropdown_button(*args):
    """
    List of arguments to build dropdown button from. Correct types and properties must be given or else nothing is rendered.

    Format:
    {% dropdown_button type [inner] [href] ... %}

    Example:
    {% dropdown_button "header" "Header name" "item" "Item name" "www.example.com" "divider" %}
    """
    index = 0
    elements = []
    try:
        while index < len(args):
            element = {"type": args[index]}
            if element["type"] == "header":
                element["inner"] = args[index + 1]
            elif element["type"] == "item":
                element["inner"] = args[index + 1]
                element["href"] = args[index + 1]
            elif element["type"] != "divider":
                return []
            index += len(element)
            elements.append(element)
        return {"elements": elements}
    except IndexError:
        return []
