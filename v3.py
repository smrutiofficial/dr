import tkinter as tk
from tkinter import PhotoImage
import customtkinter as ctk
import subprocess
import glob
import os
from PIL import Image, ImageTk
import cairosvg
import io

import pystray
from pystray import MenuItem as item
import threading

# Set appearance mode and color theme before creating the window
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Placeholder icon for apps without icons
placeholder_icon = "./icons/broken-image.png"


# Function to handle SVG conversion to PNG using cairosvg
def convert_svg_to_png(svg_path):
    try:
        with open(svg_path, "rb") as svg_file:
            png_data = cairosvg.svg2png(file_obj=svg_file)
        return Image.open(io.BytesIO(png_data))
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return None



def get_gui_apps_with_updates_and_icons():
    try:
        # Command to find and filter .desktop files
        desktop_files_cmd = (
            "find /usr/share/applications ~/.local/share/applications -name '*.desktop' -exec basename {} \\; | "
            "sed 's/\\.desktop$//' | "
            "sed 's/^\\(com\\|org\\)\\..*//' | "
            "sed -E '/^(gnome-|dev\\.|ibus-|ca\\.|display-|nm-|openjdk*|hp.*|xdg-|gcr|io-|io.|usb-|nautilus-|docker-*|apport-gtk|bluetooth-|qemu|python3.12|rygel|im-|gkbd-|feh|geoclue-|snap-|yelp|code-|software-)/d'"
        )
        desktop_files_result = subprocess.run(
            desktop_files_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )

        # Get the filtered list of .desktop file names
        desktop_file_names = desktop_files_result.stdout.splitlines()

        # Get list of upgradable packages
        apt_update_cmd = "sudo apt list --upgradable"
        apt_update_result = subprocess.run(
            apt_update_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        upgradable_packages = apt_update_result.stdout.splitlines()
        
        # Parse upgradable packages for their names
        upgradable_names = set(
            line.split('/')[0]
            for line in upgradable_packages
            if '/' in line
        )

        apps_with_icons = []

        for desktop_file_name in desktop_file_names:
            try:
                if not desktop_file_name:  # Skip if desktop_file_name is empty
                    continue

                # Construct the possible .desktop file paths
                desktop_file_path = f"/usr/share/applications/{desktop_file_name}.desktop"
                if not os.path.exists(desktop_file_path):
                    desktop_file_path = f"{os.path.expanduser('~')}/.local/share/applications/{desktop_file_name}.desktop"

                # Validate the file path
                if not os.path.exists(desktop_file_path):
                    print(f"File not found: {desktop_file_name}.desktop")
                    continue

                icon_path = None

                # Read each .desktop file for the 'Icon' field
                with open(desktop_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("Icon="):
                            icon_field = line.split("=", 1)[1].strip()
                            # Resolve the icon path
                            if os.path.isabs(icon_field) and os.path.exists(icon_field):
                                icon_path = icon_field
                            else:
                                # Fallback: Search for icons in common directories
                                possible_icon_paths = [
                                    os.path.join("/usr/share/icons/hicolor", f"**/{icon_field}.png"),
                                    os.path.join("/usr/share/icons/hicolor", f"**/{icon_field}.svg"),
                                    os.path.join("/usr/share/pixmaps", f"{icon_field}.png"),
                                    os.path.join("/usr/share/pixmaps", f"{icon_field}.svg"),
                                    os.path.join("/usr/share/icons/Papirus/128x128/apps", f"{icon_field}.svg"),
                                ]
                                for path in possible_icon_paths:
                                    found_icons = glob.glob(path, recursive=True)
                                    if found_icons:
                                        icon_path = found_icons[0]
                                        break

                # Use the desktop file name as the app name
                app_name = desktop_file_name

                # Check if the app is upgradable
                has_update = app_name.lower() in upgradable_names

                # Add the app to the list
                apps_with_icons.append({
                    "name": app_name,
                    "icon": icon_path or placeholder_icon,
                    "update_available": has_update,
                })
            except Exception as e:
                print(f"Error processing {desktop_file_name}: {e}")

        return apps_with_icons
    except Exception as e:
        print(f"Error fetching GUI applications: {e}")
        return [{"name": "Error", "icon": None, "update_available": False}]

# Example usage
apps = get_gui_apps_with_updates_and_icons()

def get_installed_apps_flatpak():
    try:
        result = subprocess.run(['flatpak', 'list', '--app', '--columns=name'], stdout=subprocess.PIPE, text=True, check=True)
        result2 = subprocess.run(['flatpak', 'list', '--app', '--columns=ref'], stdout=subprocess.PIPE, text=True, check=True)
        
        apps = result.stdout.splitlines()
        refs = result2.stdout.splitlines()
        
        app_data = []
        for app_name, ref in zip(apps, refs):
            icon_dirs = [
                f"/var/lib/flatpak/app/{ref}/active/files/share/icons/hicolor/scalable/apps/",
                f"/var/lib/flatpak/app/{ref}/active/files/share/icons/hicolor/64x64/apps",
                f"/var/lib/flatpak/app/{ref}/active/files/share/icons/hicolor/256x256/apps",
                f"/var/lib/flatpak/app/{ref}/active/files/share/icons/hicolor/512x512/apps",
            ]
            icon_path = None
            for icon_dir in icon_dirs:
                icons = glob.glob(os.path.join(icon_dir, "*"))
                if icons:
                    icon_path = icons[0]
                    break
            
            if not icon_path:
                print(f"No icon found for {app_name}, using placeholder.")
                icon_path = placeholder_icon
            
            # app_data.append({'name': app_name, 'icon': icon_path})
            app_data.append({'name': app_name, 'ref': ref, 'icon': icon_path})

        
        return app_data
    except Exception as e:
        return [{'name': f"Error fetching Flatpak apps: {e}", 'icon': None}]

# Function to fetch Flatpak apps with updates available
def get_apps_with_updates_flatpak():
    try:
        result = subprocess.run(['flatpak', 'remote-ls', '--updates', '--app', '--columns=name'], 
                                stdout=subprocess.PIPE, text=True, check=True)
        apps_with_updates = result.stdout.splitlines()
        return apps_with_updates
    except Exception as e:
        print(f"Error fetching Flatpak apps with updates: {e}")
        return []


# Function to populate the list of apps
# Function to populate the list of apps
def populate_list(package_type):
    for label in result_labels:
        label.destroy()
    result_labels.clear()

    if package_type == "APT":
        apps = get_gui_apps_with_updates_and_icons()
        updates = []  # Updates list isn't required for APT as it is handled by `update_available` field.
    elif package_type == "Flatpak":
        apps = get_installed_apps_flatpak()
        updates = get_apps_with_updates_flatpak()  # Fetch update list
    else:
        apps = ["No valid package manager selected."]
        updates = []

    # Sort apps alphabetically by name
    if isinstance(apps, list) and len(apps) > 0 and isinstance(apps[0], dict):
        apps = sorted(apps, key=lambda app: app['name'].lower())
    elif isinstance(apps, list):
        apps = sorted(apps, key=str.lower)

    for index, app in enumerate(apps, start=1):
        app_frame = ctk.CTkFrame(scrollable_frame, fg_color="#222a34")
        app_frame.pack(fill="x", padx=5, pady=8)

        if isinstance(app, dict) and app.get('icon'):
            try:
                icon_path = app['icon']
                if icon_path.lower().endswith(".svg"):
                    icon_image = convert_svg_to_png(icon_path)
                else:
                    icon_image = Image.open(icon_path)

                if icon_image:
                    icon_image = ctk.CTkImage(icon_image, size=(50, 50))
                    icon_label = ctk.CTkLabel(app_frame, image=icon_image, text="")
                    icon_label.pack(side="left", padx=(20, 10), pady=15)
            except Exception as e:
                print(f"Error loading icon: {e}")

        app_label = ctk.CTkLabel(
            app_frame,
            text=f"{app['name']}" if isinstance(app, dict) else app,
            anchor="w",
            font=("", 22),
            fg_color="#222a34"
        )
        app_label.pack(side="left", padx=5)

        uninstall_button = ctk.CTkButton(
            app_frame, text="Uninstall", 
            fg_color="#db4f5d", 
            width=100,
            command=lambda app=app: uninstall_app(app, package_type)
            )
        uninstall_button.pack(side="right", padx=(0, 20))

        # Add update button for APT apps if an update is available
        if package_type == "APT" and app.get("update_available"):
            update_button = ctk.CTkButton(
                app_frame, text="Update", fg_color="#90a470", width=100,
                command=lambda app=app: update_apt_app(app['name'])
            )
            update_button.pack(side="right", padx=5)

        # Add update button for Flatpak apps if an update is available
        if package_type == "Flatpak":
            app_name = app.get('name', "Unknown App") if isinstance(app, dict) else app
            ref = app.get('ref') if isinstance(app, dict) else None

            if app_name in updates:
                update_button = ctk.CTkButton(
                    app_frame, text="Update", fg_color="#90a470", width=100,
                    command=lambda ref=ref: update_flatpak_app(ref) if ref else None
                )
                update_button.pack(side="right", padx=5)

        result_labels.append(app_frame)


# Function to update APT apps
def update_apt_app(app_name):
    try:
        subprocess.run(['sudo', 'apt-get', 'upgrade', app_name, '-y'], check=True)
        print(f"Successfully updated {app_name}")
        populate_list("APT")
    except Exception as e:
        print(f"Error updating {app_name}: {e}")


def uninstall_app(app_id,package_type):
    # print(package_type)
    if package_type == "APT":
        try:
            # print(app_id['name'])
            # Use subprocess to run the APT remove command
            result = subprocess.run(
                ['sudo', 'apt', 'remove', '-y', app_id['name']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            populate_list("APT")
            print(f"Uninstalled {app_id['name']}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {app_id['name']}: {e.stderr}")

    elif package_type == "Flatpak":
        try:
            # print(app_id['ref'])
            # Run the Flatpak remove command
            result = subprocess.run(
                ['flatpak', 'remove', app_id['ref'], '-y'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            populate_list("Flatpak")
            print(f"Uninstalled {app_id['name']}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {app_id['name']}: {e.stderr}")

    # else:
    #     print(f"Unsupported package type: {package_type}")
# Function to handle Flatpak app updates
def update_flatpak_app(app_name):
    try:
        subprocess.run(['flatpak', 'update', app_name, '-y'], check=True)
        print(f"Successfully updated {app_name}")
        populate_list("Flatpak")
    except Exception as e:
        print(f"Error updating {app_name}: {e}")



# -----------------------------------------------------------------
def create_image():
    # Load the PNG icon (make sure the path is correct)
    image = Image.open("icons/bitmap.png")
    return image

def exit_action(icon, item):
    icon.stop()

def start_tray_icon():
    # Create and show the tray icon
    icon = pystray.Icon("Test Icon")
    icon.icon = create_image()
    icon.menu = (item('Exit', exit_action),)
    icon.run()

# Create the CTk window
app = ctk.CTk(fg_color="#151c26")
app.geometry("1000x600")
app.title("Dr. Linux")
icon_path = "icons/bitmap.png"  # Replace with the actual path to your .png icon
icon = PhotoImage(file=icon_path)
# Set the icon for the application
app.wm_iconphoto(True, icon)

row_frame = ctk.CTkFrame(app, fg_color="#151c26")
row_frame.pack(pady=10)

selected_package = ctk.StringVar()
selected_package.set("Flatpak")

dropdown = ctk.CTkComboBox(row_frame, variable=selected_package, values=["Flatpak", "APT"],font=("",14),width=200)
dropdown.grid(row=0, column=0, padx=5)

populate_button = ctk.CTkButton(
    row_frame, text="Show Apps", fg_color="#90a470", bg_color="#151c26",
    command=lambda: populate_list(selected_package.get())
)
populate_button.grid(row=0, column=1, padx=5)

scrollable_frame = ctk.CTkScrollableFrame(app, height=2000, fg_color="#151c26")
scrollable_frame.pack(fill="both", padx=10, pady=10)

scrollable_frame.bind_all("<Button-4>", lambda e: scrollable_frame._parent_canvas.yview("scroll", -1, "units"))
scrollable_frame.bind_all("<Button-5>", lambda e: scrollable_frame._parent_canvas.yview("scroll", 1, "units"))
result_labels = []
populate_list(selected_package.get())


tray_thread = threading.Thread(target=start_tray_icon)
tray_thread.daemon = True
tray_thread.start()
app.mainloop()
