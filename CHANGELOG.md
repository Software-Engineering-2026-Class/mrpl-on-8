# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-framework code generator supporting CrewAI and LangGraph.
- Parsing logic for Agentic AI Ontology RDF/Turtle Knowledge Graphs.
- Docker configuration (`Dockerfile` and `docker-compose.yml`) for containerized workflow execution.
- Added comprehensive Use Cases documentation and Architecture Diagram in `README.md`.
- Dynamic prompt interpolation for generated agentic configurations.

### Fixed
- Fixed an infinite looping recursion error in LangGraph cycles by implementing a DFS-based cycle detector that automatically generates conditional safeguard routing.
- Fixed `rdflib` parsing bad syntax error by appending missing periods to ontology definitions.
- Ensured interactive input `sys.argv` support for all generated python modules to prevent hardcoded queries.
