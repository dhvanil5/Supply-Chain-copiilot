# Supply-Chain-copilot
Overview
Smart Supply Chain CoPilot™ is an AI-powered decision support system designed for logistics and supply chain professionals. It provides an integrated platform for inventory simulation, demand forecasting, GPT-based natural language interaction, and optimization, all accessible through an interactive Streamlit dashboard.

This project combines simulation, machine learning, and optimization techniques to help organizations make data-driven decisions with greater efficiency, accuracy, and accessibility.

Key Features
Inventory Simulation Engine
Models real-world supply chain behaviors, including suppliers, warehouses, and retailers, using SimPy.

Demand Forecasting
Implements models like Prophet and LSTM to predict future demand using real or synthetic time-series data.

Natural Language Interface (GPT Integration)
Allows non-technical users to run simulations or queries using plain English via OpenAI's API and LangChain.

Optimization Module
Calculates optimal safety stock levels and delivery routing using tools such as OR-Tools and scipy.optimize.

Interactive Visualization Dashboard
Built using Streamlit to provide a dynamic interface with graphs, sliders, and real-time results.

Architecture and Modules
The project is modular and includes the following components:

Module	Technology Used	Description
Inventory Simulation	SimPy, Pandas	Simulates supply chain activities and metrics like stock levels, costs
Demand Forecasting	Prophet, LSTM, Keras, pmdarima	Predicts product demand using historical and external signals
Natural Language Interface	OpenAI API, LangChain, Pydantic	Maps user input to backend operations through GPT
Optimization Engine	OR-Tools, NetworkX, Scipy	Inventory and routing optimization with adjustable trade-offs
Dashboard & Visualization	Streamlit, Plotly, Pandas	UI for interactive exploration, control, and visual insights
Optional User System	Firebase or Supabase (optional)	Authentication and session-based data upload (CSV support)

Real-World Applications
Applicable across industries such as:

E-commerce and Retail

Manufacturing

Pharmaceuticals and Healthcare

Food & Beverage Logistics

Cold Chain Management

Multi-Warehouse Distribution Networks

Use cases include:

Managing demand spikes or seasonal trends

Planning optimal delivery routes

Avoiding overstock and stockout conditions

Enabling non-technical stakeholders to query and interact with supply data

Project Phases
Setup & Planning
Define personas, finalize MVP scope, and initialize tools.

Inventory Simulation
Model key entities and simulate supply chain behavior.

Demand Forecasting
Train time-series models and integrate external signals.

GPT Integration
Enable natural language queries and simulations.

Optimization Engine
Solve for inventory and delivery efficiency goals.

Visualization Dashboards
Build an intuitive interface using Streamlit.

User Management (Optional)
Add authentication and file upload support.

Testing and Deployment
Finalize features, perform testing, and deploy via Streamlit Cloud or Docker.

Project Impact
Impact Area	Result
Inventory Cost	10–30% potential reduction through smarter stock management
Forecast Accuracy	Improved demand planning via machine learning
Decision Efficiency	Real-time natural language interaction and dashboard-based control
Customer Satisfaction	Enhanced by minimizing delays and stockouts
Strategic Planning	Simulate future scenarios before implementation

Deployment
The application can be deployed using:

Streamlit Cloud – For quick sharing and web-based access

Docker – For containerized, production-grade deployment

License
This project is developed for academic and demonstrative purposes. Please review licensing terms before commercial use.

Acknowledgements
This system leverages open-source technologies and libraries including:

SimPy

Pandas / NumPy

Prophet / Keras

LangChain / OpenAI

OR-Tools / Scipy

Streamlit / Plotly
