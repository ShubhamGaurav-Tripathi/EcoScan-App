# 🌱 EcoScan - Your Sustainable Shopping Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-deployed-streamlit-app-url.streamlit.app/)

## Table of Contents
* [About EcoScan](#about-ecoscan)
* [Features](#features)
* [Eco-Grading System](#eco-grading-system)
* [How It Works](#how-it-works)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Running Locally](#running-locally)
* [Deployment](#deployment)
* [Project Aim](#project-aim)
* [Team](#team)
* [Contributing](#contributing)
* [License](#license)

## About EcoScan

EcoScan is a smart software application designed to empower consumers to make ecologically friendly shopping choices. By providing instant, clear, and reliable sustainability information about products, EcoScan helps combat greenwashing and encourages informed decision-making towards a more sustainable lifestyle.

The app assesses products based on various environmental factors like carbon footprint, packaging recyclability, and the presence of hazardous chemicals, consolidating complex data into an easy-to-understand "Green Score" and Eco-Grade.

## Features

* **Barcode/QR Code Scanning:** Quickly get a product's sustainability report by scanning its barcode or QR code using an uploaded image.
* **Manual Barcode Entry:** Input barcodes directly for quick lookups.
* **Demo Products:** Explore pre-selected products to see EcoScan in action.
* **Comprehensive Sustainability Report:**
    * Product's **Carbon Footprint (g CO₂e / 100g)**.
    * **Eco-Labels and Certifications** (e.g., FSC, USDA Organic).
    * **Recyclability of Packaging**.
    * Presence of **Hazardous Chemicals** or **Microplastics**.
    * Overall **Green Score** (out of 100).
    * Personalized **Eco-Grade (A-E)**.
* **Product Comparison:** Compare the carbon emissions of two different products side-by-side to make greener choices.
* **PDF Report Download:** Generate and download a detailed sustainability report for any scanned product.
* **Raw Data Access:** View and copy the full JSON data fetched from Open Food Facts for deeper analysis or development.
* **Intuitive UI:** Clean and responsive interface designed to avoid unnecessary scrolling and provide a smooth user experience.

## Eco-Grading System

EcoScan translates a product's "Green Score" (out of 100) into an easy-to-understand Eco-Grade from A to E:

* **A (Excellent):** Green Score >= 80 - Very low environmental impact. 🌳
* **B (Good):** 60 <= Green Score < 80 - Good environmental choice. 🌿
* **C (Average):** 40 <= Green Score < 60 - Average environmental impact. 🌱
* **D (Poor):** 20 <= Green Score < 40 - Higher environmental impact. ⚠️
* **E (Dangerous):** Green Score < 20 - Potentially hazardous or very high environmental impact. ☠️

## How It Works

EcoScan leverages robust open-source databases to provide its insights:

1.  **Input:** A user scans a product's barcode/QR code (via image upload) or enters it manually.
2.  **Data Fetching:** The application uses the barcode to query the **Open Food Facts API**.
3.  **Sustainability Assessment:** The fetched data (including `carbon-footprint_100g`, `ecoscore_data`, `packaging_tags`, `labels_tags`, etc.) is processed.
4.  **Green Score Calculation (Mock):** Currently, a mock `green_score` is calculated based on simulated factors (carbon, packaging, chemicals, certifications). For a production version, this would involve a sophisticated algorithm using various OFF data points.
5.  **Eco-Grade Assignment:** The `green_score` (or directly the `ecoscore_grade` from OFF API if available) is translated into an A-E Eco-Grade.
6.  **Display & Comparison:** The comprehensive report is displayed, and users can compare products' carbon footprints.

EcoScan aims to make sustainability data accessible and actionable, addressing concerns about product environmental impact and greenwashing.

## Getting Started

To run EcoScan locally on your machine, follow these steps:

### Prerequisites

* Python 3.7+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/EcoScan.git](https://github.com/your-username/EcoScan.git)
    cd EcoScan
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Make sure you have a `requirements.txt` file in your project root with all dependencies listed (e.g., `streamlit`, `requests`, `Pillow`, `pyzbar`, `fpdf`).*

### Running Locally

1.  **Ensure your virtual environment is active.**
2.  **Run the Streamlit application:**
    ```bash
    streamlit run your_app_name.py
    ```
    (Replace `your_app_name.py` with the actual name of your main Python script, e.g., `app.py` or `main.py`).

    This will open the application in your web browser, usually at `http://localhost:8501`.

## Deployment

EcoScan can be easily deployed to various cloud platforms. The recommended method for simplicity is **Streamlit Community Cloud**:

1.  **Host your code on GitHub** with a `requirements.txt` file.
2.  Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3.  Connect your GitHub account and select your EcoScan repository.
4.  Follow the prompts to deploy your app.

For more advanced deployment options (Heroku, Render, AWS, GCP), refer to their respective documentation for deploying Streamlit applications.

## Project Aim

Our goal with EcoScan is to bridge the gap between people's desire to shop sustainably and their ability to do so. We aim to:

* **Empower Consumers:** Provide tools for smart, eco-friendly shopping choices without requiring technical or scientific knowledge.
* **Centralize Data:** Make sustainability data easily accessible, understandable, and usable in one place.
* **Combat Greenwashing:** Offer clear, data-backed information to help users identify truly sustainable products.
* **Incentivize Green Behavior:** Encourage improved behavior through features like Green Scores, eco-streaks, and impact tracking.
* **Promote Circular Economy:** Help shift towards a circular economy by encouraging reuse and low-waste options.

## Team

This project was developed by **Group 9** from the **Indian Institute of Management Kozhikode**.

* Abhishek Rahi (EPGP11KC005)
* Arjun Vinod (EPGP11KC027)
* Bappa Pradhan (EPGP11KC034)
* Rhea Singh (EPGP11KC103)
* Shubham Tripathi (EPGP11KC122)

The motto of IIM Kozhikode is "योगः कर्मसु कौशलम्" (Yogaḥ Karmasu Kauśalam), which translates to "Excellence in Action" or "Skillfulness in Action".

## Contributing

We welcome contributions to EcoScan! If you have suggestions or want to contribute, please feel free to:
* Open an issue to report bugs or suggest new features.
* Fork the repository and submit a pull request with your improvements.

Please ensure your code adheres to good practices and includes appropriate tests.

## License

This project is open-source and available under the [MIT License](LICENSE). (Create a LICENSE file in your repository if you don't have one).