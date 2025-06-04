"""Module for building an executable file for the RC-Sim application using PyInstaller."""
import os
import shutil
import site
import warnings

import PyInstaller.__main__ # pylint: disable=import-error


def build_exe() -> None:
    """Build an executable file for the RC-Sim application.

    This function configures PyInstaller to package the RC-Sim application, including
    necessary assets, source files, and dependencies (NumPy, PyQt6, matplotlib).
    The resulting executable is placed in the 'dist' directory.

    Raises:
        FileNotFoundError: If the 'assets' directory is not found.
        PyInstaller.__main__.PyInstallerException: If PyInstaller encounters an error during the build process.     # pylint: disable=line-too-long
        OSError: If file operations (e.g., copying assets) fail.
    """
    # Define paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_dir = os.path.join(project_root, 'src')
    assets_dir = os.path.join(project_root, 'assets')
    output_dir = os.path.join(project_root, 'dist')

    # Path to numpy/.libs (if exists)
    numpy_libs_dir = os.path.join(site.getsitepackages()[0], 'numpy', '.libs')

    # Check existence of assets directory
    if not os.path.exists(assets_dir):
        raise FileNotFoundError(f"Папка assets не найдена по пути: {assets_dir}")

    # Check existence of required icons
    required_icons = ['app.ico', 'help.ico', 'favicon.ico']
    for icon in required_icons:
        icon_path = os.path.join(assets_dir, icon)
        if not os.path.exists(icon_path):
            warnings.warn(f"Иконка {icon} не найдена по пути: {icon_path}")

    # Check existence of numpy/.libs
    if not os.path.exists(numpy_libs_dir):
        warnings.warn(f"Папка numpy/.libs не найдена по пути: {numpy_libs_dir}. Продолжаем без неё.")   # pylint: disable=line-too-long
        numpy_libs_dir = None

    # PyInstaller arguments
    pyinstaller_args = [
        os.path.join(src_dir, 'rc_sim', 'main.py'),
        '--name=RC_Simulator',
        f'--icon={os.path.join(assets_dir, "app.ico")}',
        f'--add-data={assets_dir};assets',
        f'--add-data={os.path.join(src_dir, "rc_sim")};rc_sim',
        '--collect-all=numpy',
        '--collect-all=PyQt6',
        '--collect-all=matplotlib',
        '--hidden-import=numpy',
        '--hidden-import=numpy._core._multiarray_umath',
        '--hidden-import=PyQt6',
        '--hidden-import=matplotlib',
        '--onedir',
        '--windowed',
        '--clean',
        f'--distpath={output_dir}',
        '--noconfirm'
    ]

    # Add numpy/.libs if it exists
    if numpy_libs_dir:
        pyinstaller_args.append(f'--add-binary={numpy_libs_dir};numpy/.libs')

    # Additional hidden imports
    additional_hidden_imports = [
        'matplotlib',
        'PyQt6',
    ]
    for module in additional_hidden_imports:
        pyinstaller_args.append(f'--hidden-import={module}')

    # Run PyInstaller
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("Сборка успешно завершена!")

        # Copy additional files if necessary
        output_app_dir = os.path.join(output_dir, 'RC_Simulator')
        if os.path.exists(assets_dir):
            shutil.copytree(assets_dir,
                            os.path.join(output_app_dir, 'assets'),
                            dirs_exist_ok=True)

    except PyInstaller.__main__.PyInstallerException as e:      # pylint: disable=no-member
        print(f"Ошибка PyInstaller при сборке: {str(e)}")
        raise
    except OSError as e:
        print(f"Ошибка при работе с файлами: {str(e)}")
        raise


if __name__ == '__main__':
    build_exe()
