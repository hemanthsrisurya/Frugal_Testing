# Swiggy Automation Script

This repository contains a Python script that automates the process of logging into Swiggy, searching for a restaurant, adding an item to the cart, and preparing for checkout using Selenium WebDriver.

## Features
- Automated login with manual OTP entry
- Restaurant search and selection
- Add first available item to cart
- Address selection (Home or first available)
- Logging and error handling

## Requirements
- Python 3.7+
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- Selenium

## Installation
1. Clone this repository or copy the script file.
2. Install dependencies:
   ```bash
   pip install selenium
   ```
3. Download the appropriate [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) and ensure it is in your PATH or the same directory as the script.

## Usage
1. Edit the script to set your phone number and preferred restaurant name.
2. Run the script:
   ```bash
   python swiggy_automation.py
   ```
3. Follow the prompts in the terminal and browser (manual OTP entry required).

## Notes
- The script keeps the browser open at the end for manual review and payment.
- Logging output is saved to `swiggy_automation.log`.

## Disclaimer
This script is for educational purposes only. Use responsibly and respect Swiggy's terms of service.
