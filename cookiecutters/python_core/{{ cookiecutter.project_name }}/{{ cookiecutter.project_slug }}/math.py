from typing import Iterable


def dot_product(vector1: Iterable[float], vector2: Iterable[float]) -> float:
    return sum(i * j for i, j in zip(vector1, vector2))
