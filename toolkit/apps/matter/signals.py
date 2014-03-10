from django.dispatch import Signal


MATTER_ADD_PARTICIPANT = Signal(providing_args=['matter', 'user'])
