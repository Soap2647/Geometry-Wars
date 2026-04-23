"""
Windows kayıt defteri (registry) kontrolü.
Oyunun sadece bir kez kurulmasını sağlar.
Kurulum öncesinde ve başlatıcıda çalıştırılır.
"""
import sys
import os

# Windows dışı platformlarda registry yoktur
if sys.platform != "win32":
    print("Bu betik yalnızca Windows'ta çalışır.")
    sys.exit(0)

import winreg

# Kayıt defteri anahtarı sabitleri
REGISTRY_ROOT = winreg.HKEY_LOCAL_MACHINE
REGISTRY_PATH = r"SOFTWARE\GeometryWars"
REGISTRY_VALUE_NAME = "Installed"
REGISTRY_VALUE_DATA = "1"
APP_NAME = "Geometry Wars"
APP_VERSION = "1.0.0"
APP_PUBLISHER = "GW Studios"


def is_already_installed() -> bool:
    """
    Oyunun daha önce kurulup kurulmadığını kontrol et.
    Registry anahtarı varsa True döner.
    """
    try:
        key = winreg.OpenKey(REGISTRY_ROOT, REGISTRY_PATH,
                             0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, REGISTRY_VALUE_NAME)
        winreg.CloseKey(key)
        return value == REGISTRY_VALUE_DATA
    except (FileNotFoundError, OSError, PermissionError):
        return False


def write_registry_entry(install_path: str = "") -> bool:
    """
    Kurulum kaydını registry'e yaz.
    Başarılı olursa True döner.
    """
    try:
        key = winreg.CreateKeyEx(REGISTRY_ROOT, REGISTRY_PATH,
                                  0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, REGISTRY_VALUE_NAME, 0,
                          winreg.REG_SZ, REGISTRY_VALUE_DATA)
        winreg.SetValueEx(key, "Version", 0,
                          winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0,
                          winreg.REG_SZ, APP_PUBLISHER)
        winreg.SetValueEx(key, "DisplayName", 0,
                          winreg.REG_SZ, APP_NAME)
        if install_path:
            winreg.SetValueEx(key, "InstallLocation", 0,
                              winreg.REG_SZ, install_path)
        winreg.CloseKey(key)
        return True
    except (PermissionError, OSError) as e:
        print(f"Registry yazma hatası: {e}")
        print("Yönetici olarak çalıştırın.")
        return False


def remove_registry_entry() -> bool:
    """
    Kaldırma (uninstall) sırasında registry kaydını sil.
    Başarılı olursa True döner.
    """
    try:
        winreg.DeleteKey(REGISTRY_ROOT, REGISTRY_PATH)
        return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Registry silme hatası: {e}")
        return False


def get_install_info() -> dict:
    """
    Registry'den kurulum bilgilerini oku.
    Bilgiler bulunamazsa boş dict döner.
    """
    info = {}
    try:
        key = winreg.OpenKey(REGISTRY_ROOT, REGISTRY_PATH,
                             0, winreg.KEY_READ)
        for value_name in ["Version", "Publisher", "DisplayName",
                           "InstallLocation", REGISTRY_VALUE_NAME]:
            try:
                value, _ = winreg.QueryValueEx(key, value_name)
                info[value_name] = value
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except (FileNotFoundError, OSError):
        pass
    return info


def main():
    """
    Komut satırından çağrıldığında kurulum durumunu göster.
    Kullanım: python registry_check.py [install|remove|check]
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Geometry Wars - Registry Yöneticisi"
    )
    parser.add_argument(
        "action",
        choices=["install", "remove", "check"],
        help="Yapılacak işlem"
    )
    parser.add_argument(
        "--path",
        default="",
        help="Kurulum dizini (install işlemi için)"
    )

    args = parser.parse_args()

    if args.action == "check":
        if is_already_installed():
            info = get_install_info()
            print(f"{APP_NAME} kurulu.")
            print(f"Sürüm : {info.get('Version', 'Bilinmiyor')}")
            print(f"Konum : {info.get('InstallLocation', 'Bilinmiyor')}")
            sys.exit(0)
        else:
            print(f"{APP_NAME} kurulu değil.")
            sys.exit(1)

    elif args.action == "install":
        if is_already_installed():
            print(f"{APP_NAME} zaten kurulu. Tekrar kurulum engellendi.")
            sys.exit(2)
        success = write_registry_entry(args.path)
        if success:
            print(f"{APP_NAME} başarıyla kayıt defterine eklendi.")
            sys.exit(0)
        else:
            print("Kayıt defterine yazılamadı.")
            sys.exit(1)

    elif args.action == "remove":
        if remove_registry_entry():
            print(f"{APP_NAME} kayıt defterinden kaldırıldı.")
            sys.exit(0)
        else:
            print("Kayıt defteri kaydı kaldırılamadı.")
            sys.exit(1)


if __name__ == "__main__":
    main()
