# Guide for Developers

This page provides information for developers of this project who wish to augment the Python API (and typically also the REST API) to WRENCH. 

## Overall Design



The Python API is built on top of the REST API. It provides users with classes for simulation objects (`Task`, `File`, `BareMetalComputeService`, `StandardJob`, etc.). These classes hold almost no


![image](./overall_architecture.svg) 
