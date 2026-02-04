<div align="center">

# 🚗 ParkPi: IoT Smart Parking System

### A centralized embedded system for real-time parking management, access control, and occupancy monitoring.

![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-C51A4A?style=for-the-badge&logo=raspberry-pi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Hardware](https://img.shields.io/badge/Hardware-Sensors%20%7C%20Actuators-orange?style=for-the-badge&logo=arduino&logoColor=white)
![Status](https://img.shields.io/badge/Status-Finished-success?style=for-the-badge&logo=checkmark&logoColor=white)

[View Project Docs] • [Report Bug] • [Request Feature]

</div>

---

## 📖 Project Overview

**ParkPi** is an automated parking system designed to solve the lack of real-time data in conventional parking lots. Unlike traditional systems that rely on manual counting or cameras, ParkPi validates entry via **NFC** and physically detects the presence of vehicles in each spot using **weight sensors (Load Cells)**.

> ⚠️ **Hardware Note:** This system is optimized for the **Raspberry Pi 5** and requires specific wiring for the PN532 (UART) and HX711 (GPIO Bit-Banging).

---

## Key Features

The system implements a **Multithreaded Architecture** to handle real-time concurrency between access control and sensor monitoring:

### 1. 🔐 NFC Access Control (PN532)
* **Instant Validation:** Uses a whitelist stored in RAM for **O(1) lookup speed**.
* **Security:** Only authorized cards (UIDs) trigger the entry mechanism.
* **Traffic Logic:** The barrier only opens if the user is authorized **AND** global capacity > 0.

### 2. ⚖️ Physical Occupancy Detection
* **Weight Sensors:** Utilizes **5kg Load Cells** with **HX711 amplifiers**.
* **Hysteresis Filter:** Implements software filtering to prevent "flickering" caused by vibrations or wind.
* **Real-Time Feedback:** Updates the specific status of Spot #1 and Spot #2 instantly via LEDs.

### 3. 🚦 Automation & Actuation
* **Servo Barrier:** Controls an **MG90S** servo motor via PWM for physical entry management.
* **Concurrency:** Uses Python `threading.Lock()` to prevent race conditions when multiple threads try to access GPIO pins simultaneously.

---

## 🛠️ Hardware & Tech Stack

| Component | Model / Library | Protocol | Description |
| :--- | :--- | :--- | :--- |
| **Main Controller** | **Raspberry Pi 5** | - | Central Processing Unit. |
| **Language** | **Python 3.11+** | - | Core logic implementation. |
| **NFC Reader** | **PN532 V3** | UART | User Authentication (RFID/NFC). |
| **ADC Converter** | **HX711** | Bit-Banging | 24-Bit ADC for Load Cells. |
| **Actuator** | **MG90S Servo** | PWM | Physical barrier control. |
| **Library** | **lgpio / gpiozero** | - | Low-level GPIO control for RPi 5. |

---

## 🚀 Installation & Execution Guide

Follow these exact steps to get the project running on your Raspberry Pi.

### ⚙️ Prerequisites
Ensure you have the following ready:
1.  **Raspberry Pi** (Model 4 or 5 recommended) with Raspberry Pi OS.
2.  **Python 3**: Installed by default.
3.  **Wiring**: Ensure all sensors are connected according to the pinout in `Main.py`.

### Execution Steps

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/LilianaVo/Parkpi.git](https://github.com/LilianaVo/Parkpi.git)
    cd Parkpi
    ```

2.  **Create Virtual Environment (Recommended)**
    > Python on RPi 5 requires a virtual environment to avoid conflicts with system packages.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the System**
    ```bash
    python3 Main.py
    ```

---

## ⚖️ Calibration: Sensor Setup

> ⚠️ **Warning:** Load cells vary slightly in manufacturing. You must calibrate them before the first use to get accurate readings.

1.  **Run Calibration Script:**
    ```bash
    python3 calibrar_celda.py
    ```

2.  **Follow Instructions:**
    * Place a known weight (e.g., a phone or water bottle) on the sensor.
    * Enter the weight in grams when prompted.
    * The script will calculate the **Reference Unit**.

3.  **Update Code:**
    * Copy the resulting value and update the `reference_unit` variable in `Main.py`.

---

## Academic Context

This project was developed for the **Embedded Systems** course at the **National Autonomous University of Mexico (UNAM)**.

| **Course Information** | **Details** |
| :--- | :--- |
| **University** | Universidad Nacional Autónoma de México (UNAM) |
| **Faculty** | **Faculty of Engineering** |
| **Course** | Fundamentals of Embedded Systems (1858) |
| **Professor** | Ing. Samuel Gandarilla Pérez |
| **Group / Brigade** | Group 06 — Brigade 02 |

---

## Contributors

* **Cervantes García Eduardo** - *Firmware & Circuit Design*
* **Lee Obando Ileana Verónica** - *Hardware Assembly & Testing*
* **Márquez Sánchez Mirna Daniela** - *Physical Model & Structure*
* **Montes López Emiliano** - *Calibration & Data Analysis*

---

## 📄 License

Distributed under the MIT License.
