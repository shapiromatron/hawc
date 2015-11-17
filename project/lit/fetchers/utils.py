
def get_author_short_text(authors):
    # Given a list of authors, return citation
    nAuthors = len(authors)
    if nAuthors == 0:
        return u''
    elif nAuthors == 1:
        return unicode(authors[0])
    elif nAuthors == 2:
        return u'{0} and {1}'.format(*authors)
    elif nAuthors == 3:
        return u'{0}, {1}, and {2}'.format(*authors)
    else:  # >3 authors
        return u'{0} et al.'.format(authors[0])
