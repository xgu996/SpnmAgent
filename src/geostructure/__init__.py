"""GeoStructure-Agent: energy-preserving numerical methods on the GSGE framework.

The packages under ``geostructure`` (core, gsge, structure, space, time, solve,
experiments) form the deterministic kernel and must never import LLM libraries.
Only ``agent_tools`` and ``agents`` may depend on an LLM client.
"""

__version__ = "0.0.1"
