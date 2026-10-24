from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable


class ProveedorLLM(ABC):
    """Puerto (interfaz) para proveedores de modelos de lenguaje."""
    @abstractmethod
    def completar(self, prompt: str) -> str:
        ...


# --- ADAPTER: adapta proveedores o SDKs externos ---
class OllamaLocalAdapter(ProveedorLLM):
    def __init__(self, cliente_ollama=None) -> None:
        self._cliente = cliente_ollama

    def completar(self, prompt: str) -> str:
        if self._cliente:
            return self._cliente.generate(prompt)
        return "Respuesta reglamentaria local simulada."


class ProveedorSimulado(ProveedorLLM):
    """Doble de prueba para pruebas unitarias deterministas sin costo ni red."""
    def __init__(self, respuestas: dict[str, str] | None = None, respuesta_defecto: str = "") -> None:
        self.respuestas = respuestas or {}
        self.respuesta_defecto = respuesta_defecto
        self.llamadas = 0

    def completar(self, prompt: str) -> str:
        self.llamadas += 1
        return self.respuestas.get(prompt, self.respuesta_defecto)


# --- DECORATOR: caché de consultas para evitar costos y latencia ---
class ConCacheLLM(ProveedorLLM):
    def __init__(self, interno: ProveedorLLM) -> None:
        self._interno = interno
        self._cache: dict[str, str] = {}

    def completar(self, prompt: str) -> str:
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]


# --- CHAIN OF RESPONSIBILITY: guardrails de seguridad electoral ---
class GuardrailElectoral(ABC):
    def __init__(self, siguiente: GuardrailElectoral | None = None) -> None:
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto = self._aplicar(texto)
        if self._siguiente:
            return self._siguiente.validar(texto)
        return texto

    @abstractmethod
    def _aplicar(self, texto: str) -> str:
        ...


class SinResultadosElectorales(GuardrailElectoral):
    """Bloquea respuestas que pretendan dar conteos o ganadores (la IA no cuenta votos)."""
    PROHIBIDAS = ["ganó", "va ganando", "primer lugar", "conteo oficial", "votos computados"]

    def _aplicar(self, texto: str) -> str:
        for palabra in self.PROHIBIDAS:
            if palabra in texto.lower():
                raise ValueError(f"Guardrail: la IA intentó emitir resultados electorales ('{palabra}')")
        return texto


class SinAfirmacionesSesgadas(GuardrailElectoral):
    """Bloquea inducción o direccionamiento del voto hacia listas o candidatos."""
    SESGADAS = ["vota por", "debes votar por", "la mejor lista es", "te recomiendo elegir"]

    def _aplicar(self, texto: str) -> str:
        for frase in self.SESGADAS:
            if frase in texto.lower():
                raise ValueError(f"Guardrail: la IA emitió una recomendación electoral sesgada ('{frase}')")
        return texto


class LongitudMaxima(GuardrailElectoral):
    """Evita alucinaciones excesivas forzando respuestas concisas."""
    def __init__(self, max_caracteres: int = 250, siguiente: GuardrailElectoral | None = None) -> None:
        super().__init__(siguiente)
        self._max = max_caracteres

    def _aplicar(self, texto: str) -> str:
        if len(texto) > self._max:
            raise ValueError(f"Guardrail: la respuesta excedió la longitud máxima ({len(texto)} > {self._max})")
        return texto


class AsistenteReglamento:
    """Cliente que combina Strategy + Decorator + Chain of Responsibility."""
    def __init__(self, proveedor: ProveedorLLM, guardrails: GuardrailElectoral | None = None) -> None:
        self.proveedor = proveedor
        self.guardrails = guardrails

    def consultar(self, pregunta: str) -> str:
        prompt = f"Consulta sobre el reglamento de VotoEPIS: {pregunta}"
        respuesta = self.proveedor.completar(prompt)
        if self.guardrails:
            respuesta = self.guardrails.validar(respuesta)
        return respuesta
