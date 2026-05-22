# 🏎️ Race Car & Track Leaderboard Management System

## 📌 Project Overview
**Race Car Management System** is a modular, object-oriented Python 3 desktop application engineered as a final group project for the *Introduction to Programming 2* course. 

The system is designed for comprehensive management of race cars and street-legal sport vehicles, logging core technical configurations (mileage, brand, model), and hosting secured lap-time leaderboards across multiple iconic international race tracks with millisecond precision. A multi-tab Graphical User Interface (GUI) built on top of `Tkinter (ttk)` provides smooth view switching, interactive data filtering, and real-time data analytical visualizations.

---

##  Team Members & Contributions (Individual Accountability)

In adherence to the *Group Assignment Protocol*, individual domains and system responsibilities were cleanly separated and executed as follows:

* **Alnur (Lead Software Engineer & Data Architect):**
    * Designed and implemented the core data layer and Advanced OOP architecture (abstract base classes, class inheritance hierarchy, method polymorphism, and strict field encapsulation).
    * Engineered the robust input verification engine (`utils.py`) leveraging advanced Regular Expressions (Regex).
    * Integrated functional programming primitives (`lambda`, `map`, `filter`) to orchestrate telemetry analytics and model string transformations.
    * Developed and maintained automated test-driven test suites (9 granular, comprehensive unit tests inside `test_app.py`).

* **Zharkyn (Lead UI/UX Developer & System Integrator):**
    * Designed and implemented the multi-tab responsive Graphical User Interface (GUI) architecture utilizing the `Tkinter` and `ttk` libraries.
    * Integrated customized tabular `Treeview` layout configurations for dynamic streaming of registered vehicle profiles and lap records.
    * Configured event-driven hooks linking business logic managers (`Manager/manage.py`) to UI layout instances (`main.py`).
    * Debugged and structured package-level cross-imports to guarantee runtime environment stability.

---

##  Architecture & Architectural Design

The system enforces a strict separation of concerns, decoupling the presentation layer (UI) from the business engine (Manager), core domain entity structures (Cars), and cross-cutting utility modules.

### Class Hierarchy (OOP Blueprint)
The codebase fully satisfies the **Advanced OOP (27 Points)** rubric by combining encapsulation, structural inheritance, method overriding, and container-driven associations:

```text
       ┌───────────────────────────┐
       │    BaseVehicle (ABC)      │  <── Abstract Base Class
       ├───────────────────────────┤
       │ - _brand: str             │  <── Encapsulated Private Attributes
       │ - _model: str             │
       │ - _mileage: int           │
       ├───────────────────────────┤
       │ + get_specifications():str│  <── Abstract Polymorphic Method
       └─────────────┬─────────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
   ┌─────────────────┐ ┌───────────────┐
   │     RaceCar     │ │   StreetCar   │  <── Structural Inheritance
   ├─────────────────┤ ├───────────────┤
   │ + records: dict │ │ + fuel_type   │
   ├─────────────────┤ ├───────────────┤
   │ + get_specific─ │ │ + get_specif─ │  <── Polymorphic Overriding
   │   ations()      │ │   ications()  │
   └─────────────────┘ └───────────────┘