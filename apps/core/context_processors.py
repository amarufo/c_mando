"""Variables disponibles en todas las plantillas: menú de áreas según los permisos del usuario."""

from .dashboard import areas_visibles


def navegacion(request):
    return (
        {"areas_menu": areas_visibles(request.user)}
        if request.user.is_authenticated
        else {}
    )
