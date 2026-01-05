# MibToZabbixTemplateGenerator

A modern Python desktop application to import SNMP MIB files and generate Zabbix 7.0 (or older) YAML templates.

![App Screenshot](https://github.com/user-attachments/assets/459acde2-c7bd-46d6-81e8-805cd150fffe) <!-- Replace with real screenshot if available -->

![App Screenshot](https://github.com/user-attachments/assets/4f9712b9-c184-48a4-8479-e7d57073076a)

## 🚀 Features

- **Intuitive GUI**: Built with `CustomTkinter` for a sleek dark-mode experience.
- **Smart MIB Parsing**: Extract `OBJECT-TYPE` items, SYNTAX, and DESCRIPTION using optimized regex.
- **Auto-Root Detection**: Automatically identifies the enterprise OID suffix from the MIB file.
- **Preview & Edit**: Customize item names, keys, and descriptions in a dedicated window before exporting.
- **Zabbix Compatibility**:
  - Generates YAML templates compliant with Zabbix 7.0+.
  - Supports custom Zabbix version specification.
  - Generates valid UUID v4 (32-char hex) as required by Zabbix.
- **Dynamic OID Display**: See full OIDs update in real-time as you modify the base OID.
- **Smart Units**: Automatically detects `%` or `Celsius` from descriptions to assign appropriate units.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pokertour/MibToZabbixTemplate.git
   cd MibToZabbixTemplate
   ```

2. **Install dependencies**:
   Make sure you have Python 3.8+ installed.
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Building the Executable (.exe)

To create a standalone Windows executable, we use `PyInstaller`:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the .exe**:
   Run the following command in the project root:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter --name "MibToZabbixTemplateGenerator" main.py
   ```

The generated file will be located in the `dist/` folder.

## 📖 Usage

1. **Launch the app**:
   ```bash
   python main.py
   ```
2. **Load a MIB file**: Click "Charger MIB" and select your `.mib` or `.txt` file.
3. **Configure**:
   - Check the **Base OID** (automatically filled if detected).
   - Set the **Template Name** and **Group**.
   - Specify your **Zabbix Version** (e.g., 6.4, 7.0).
4. **Select Items**: Highlight the objects you want to include in the template.
5. **Preview & Export**: Click "AVANT-PROPOS & EXPORT", review your items, and save the final `.yaml` file.
6. **Import in Zabbix**: Go to *Data collection -> Templates -> Import* in your Zabbix web interface.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*Created with ❤️ for the Zabbix Community.*
