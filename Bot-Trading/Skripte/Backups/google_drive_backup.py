from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# Google Drive Authentifizierung
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Pfade für die Backups
backup_folder = "Z:\\Bot-Trading\\Skripte\\Backups"
google_drive_folder_id = "1nDfIHNB5_c1ZAPeIgeSacTIjqgzkNLOA"  # Dein freigegebener Google Drive Ordner

# Alle Dateien im Backup-Ordner hochladen
for file_name in os.listdir(backup_folder):
    file_path = os.path.join(backup_folder, file_name)
    gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': google_drive_folder_id}]})
    gfile.SetContentFile(file_path)
    gfile.Upload()
    print(f"Hochgeladen: {file_name}")

print("✅ Backup abgeschlossen!")
