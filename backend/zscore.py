import json
import os
from bisect import bisect_left
from typing import Optional

_REFS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "model",
    "who_refs",
    "bmi_for_age_who2007.json",
)

with open(_REFS_PATH, "r") as f:
    _REFS = json.load(f)

_MONTHS = [entry["month"] for entry in _REFS["data"]]
_INDEX = {entry["month"]: entry for entry in _REFS["data"]}


def _normalize_sex(sexo: Optional[str]) -> str:
    if not sexo:
        return "boys"
    s = sexo.strip().lower()
    if s.startswith("m") or s == "masculino" or s == "hombre":
        return "boys"
    if s.startswith("f") or s == "femenino" or s == "mujer":
        return "girls"
    return "boys"


def _resolve_entry(edad_meses: float, sexo: str) -> dict:
    key = "boys" if sexo == "boys" else "girls"
    if edad_meses <= _MONTHS[0]:
        return _INDEX[_MONTHS[0]][key]
    if edad_meses >= _MONTHS[-1]:
        return _INDEX[_MONTHS[-1]][key]
    pos = bisect_left(_MONTHS, edad_meses)
    if _MONTHS[pos] == edad_meses:
        return _INDEX[_MONTHS[pos]][key]
    lower = _INDEX[_MONTHS[pos - 1]][key]
    upper = _INDEX[_MONTHS[pos]][key]
    frac = (edad_meses - _MONTHS[pos - 1]) / (_MONTHS[pos] - _MONTHS[pos - 1])
    return {
        "L": lower["L"] + frac * (upper["L"] - lower["L"]),
        "M": lower["M"] + frac * (upper["M"] - lower["M"]),
        "S": lower["S"] + frac * (upper["S"] - lower["S"]),
    }


def imc_zscore(imc: float, edad_meses: float, sexo: Optional[str]) -> Optional[float]:
    """Calcula el z-score de IMC/edad según OMS 2007."""
    if imc <= 0 or edad_meses <= 0:
        return None
    if edad_meses < 61 or edad_meses > 228:
        return None
    key = _normalize_sex(sexo)
    lms = _resolve_entry(edad_meses, key)
    L, M, S = lms["L"], lms["M"], lms["S"]
    if M <= 0 or S <= 0:
        return None
    if L == 0:
        return float("nan")
    try:
        return (((imc / M) ** L) - 1.0) / (L * S)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def categoria_oms(z: Optional[float]) -> str:
    if z is None:
        return "Sin referencia"
    if z < -3:
        return "Delgadez severa"
    if z < -2:
        return "Delgadez"
    if z <= 1:
        return "Peso normal"
    if z <= 2:
        return "Sobrepeso"
    if z <= 3:
        return "Obesidad"
    return "Obesidad severa"


def alerta_desde_z(z: Optional[float]) -> str:
    """Mapea z-score a la semaforización de 3 colores usada por el CDSS."""
    if z is None:
        return "Verde"
    if z < -2:
        return "Roja"
    if z > 2:
        return "Roja"
    if z < -1 or z > 1:
        return "Naranja"
    return "Verde"
