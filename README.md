<img align="left" style="vertical-align: middle" src="data/icons/hicolor/256x256/apps/ir.imansalmani.iplan.png" alt="IPlan" width="128">

# IPlan
Your plan for improve personal life and workflow

<div align="center">
  <img src="data/screenshots/window.png">
</div>

## Features
* Grouping tasks with project and list
* Timer for tasks
* Global search
* Arranging projects, lists and tasks by drag and drop

## Installation
### Build

1. Clone the repo and move to project directory
```sh
git clone https://github.com/iman-salmani/iplan.git && cd iplan
```
2. Install flatpak builder (flatpak-builder package available in most distributions)
  - Fedora
  ```sh
  sudo dnf install flatpak-builder
  ```
  - Ubuntu and Debian based distributions
  ```sh
  sudo apt install flatpak-builder
  ```
  - Arch
  ```sh
  sudo pacman -S flatpak-builder
  ```

3. Build and install with flatpak builder
  - System wide (Recommended)
  ```sh
  sudo flatpak-builder --install builddir ir.imansalmani.iplan.json --force-clean
  ```
  - User (For testing)
  ```sh
  flatpak-builder --install builddir ir.imansalmani.iplan.json --force-clean --user
  ```

4. Run
> App should be appear in your applications menu.
```sh
flatpak run ir.imansalmani.iplan
```
