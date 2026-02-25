import enum


class UserRole(str, enum.Enum):
    operador = "operador"
    coordenador = "coordenador"
    admin = "admin"


class FoodCategory(str, enum.Enum):
    arroz = "arroz"
    feijao = "feijao"
    outros = "outros"