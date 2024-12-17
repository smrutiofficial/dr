<div align="center">
   <picture>
      <img src="./assets/drlinux.png">
   </picture>
   <h2>Dr. Linux</h2>
</div>
<div align="center">

![Static Badge](https://img.shields.io/badge/drlinux-v1.1.0-blue)  
![Static Badge](https://img.shields.io/badge/downloads-10+-green)
![Static Badge](https://img.shields.io/badge/License-MIT-yellow)
![Static Badge](https://img.shields.io/badge/total_Lines-45k-red)

| A GUI tool to manage Linux applications |
|-----------------------------------------|
</div>


# Dr.Linux

Linux App Manager GUI is a user-friendly software for managing Linux applications through a graphical user interface. It supports application installation, uninstallation, and updates using package managers like Flatpak, APT and DEB files. 

![Linux App Manager GUI](./assets/preview.gif)

## Features

- **List Installed Applications:** Displays all installed applications on your Linux system.
- **Uninstallation:** Allows easy removal of applications via the GUI.
- **Update Applications:** Checks for available updates and provides options to update applications directly from the GUI.
- **Integration:** Supports Flatpak, APT, Snap, and DEB packages.
- **Real-time Updates:** Displays updated lists after any changes (installations or removals).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/linux-app-manager.git
   cd linux-app-manager
   ```

2. Build & Run the application:
   ```bash
   bash ./run.sh
   ```

## Usage

1. Launch the application.
2. Use the navigation menu to explore installed applications, uninstall unwanted apps, or check for updates.
3. Select an application to perform the desired action (uninstall/update).

## Requirements

- Python 3.6+
- Tkinter (usually included with Python installations)
- Linux distribution with APT, Flatpak installed

## Contributing

1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.
