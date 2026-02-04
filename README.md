<div align="center">
  <img src="https://img.shields.io/badge/Status-Finished-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platform-Raspberry_Pi_5-C51A4A?style=for-the-badge&logo=raspberry-pi&logoColor=white" />
  <img src="https://img.shields.io/badge/Language-Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  
  <h1>🚗 ParkPi: IoT Smart Parking System</h1>

  <p>
    <b>A centralized embedded system for real-time parking management, access control, and occupancy monitoring.</b>
  </p>

  <p>
    <b>Universidad Nacional Autónoma de México (UNAM)</b><br>
    <i>Faculty of Engineering — Division of Electrical Engineering</i><br>
    <b>Course:</b> Fundamentals of Embedded Systems (1858)<br>
    <b>Semester:</b> 2026-1 • <b>Group:</b> 06 • <b>Brigade:</b> 02<br>
    <b>Professor:</b> Ing. Samuel Gandarilla Pérez
  </p>
</div>

---

## 📖 Overview

**ParkPi** is an automated parking system designed to solve the lack of real-time data in conventional parking lots. Unlike traditional systems that rely on manual counting, ParkPi validates entry via **NFC** and physically detects the presence of vehicles in each spot using **weight sensors (Load Cells)**.

The system runs on a **Raspberry Pi 5**, utilizing **multithreading** to handle access control and sensor monitoring simultaneously without blocking operations.

## ✨ Key Features

* **🔐 NFC Access Control:** Validates users against a whitelist (stored in RAM for O(1) lookup speed) using a **PN532** module.
* **⚖️ Physical Occupancy Detection:** Uses **Load Cells (5kg)** + **HX711 amplifiers** to detect if a car is actually parking (filtering out pedestrians or shadows).
* **🚦 Smart Traffic Control:** The entry barrier (Servo) only opens if the user is authorized **AND** there is at least one spot available.
* **🧵 Concurrent Processing:** Implements Python `threading` with Locks to manage hardware resources (GPIO) safely between the Entry Thread and the Monitoring Thread.
* **🧠 Custom Drivers:** Includes a custom "Bit-Banging" driver for the HX711 sensor to ensure precise 24-bit reading on the RPi 5.

## 🛠️ Hardware Architecture

| Component | Model | Function | Protocol |
| :--- | :--- | :--- | :--- |
| **Main Unit** | Raspberry Pi 5 | Central Processing Unit | - |
| **NFC Reader** | PN532 V3 | User Authentication | UART (Serial) |
| **Weight Sensors** | Load Cell (Bar) + HX711 | Vehicle Presence Detection | Bit-Banging (GPIO) |
| **Actuator** | MG90S Servo (Metal Gear) | Entry Barrier Control | PWM |
| **Indicators** | Green LEDs | Spot Availability Status | GPIO |

## 🏗️ Software Structure

The system is built in **Python 3** and follows a modular architecture:

* `Main.py`: Orchestrates the system. Launches two parallel threads:
    * **Thread 1 (Access):** Waits for NFC interrupts, validates UID, checks global capacity, controls the Servo.
    * **Thread 2 (Monitoring):** Polls load cells, applies hysteresis (to avoid flickering), updates global state, and toggles LEDs.
* `celda_carga.py`: Low-level driver for HX711 using `lgpio` for microsecond precision.
* `sensor_nfc.py`: Handles PN532 communication and UID whitelist caching.
* `valid_uids.txt`: Persistent database of authorized users.

## 🚀 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/LilianaVo/Parkpi.git](https://github.com/LilianaVo/Parkpi.git)
    cd Parkpi
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Requires `lgpio`, `adafruit-circuitpython-pn532`, `gpiozero`, etc.)*

3.  **Calibrate Sensors (First time only):**
    Run the calibration script for each load cell to determine the scale factor.
    ```bash
    python3 calibrar_celda.py
    ```

4.  **Run the System:**
    ```bash
    python3 Main.py
    ```

## 👥 Project Team (Brigade 02)

| Student Name | ID (No. Cuenta) | Role |
| :--- | :--- | :--- |
| **Cervantes García Eduardo** | 318123602 | Firmware & Circuit Design |
| **Lee Obando Ileana Verónica** | 318118408 | Hardware Assembly & Testing |
| **Márquez Sánchez Mirna Daniela** | 319232794 | Physical Model & Structure |
| **Montes López Emiliano** | 317119581 | Calibration & Data Analysis |

---
<div align="center">
  <i>November 26, 2025 — Mexico City 🇲🇽</i>
</div>
