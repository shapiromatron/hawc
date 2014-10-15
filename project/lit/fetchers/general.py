
def get_author_short_text(authors_list):
    # Given multiple authors return the short-text representation of their
    # names. Expects a list of authors names, returns a string.
    num_auths = len(authors_list)
    if num_auths == 0:
        return u''
    elif num_auths == 1:
        return authors_list[0]
    elif num_auths == 2:
        return u' and '.join(authors_list)
    elif num_auths == 3:
        authors_short = u', '.join(authors_list)
        return authors_short[:authors_short.rfind(',')] + ', and' + \
               authors_short[authors_short.rfind(',')+1:]
    else:  # >3 authors
        return authors_list[0] + u' et al.'
