import datetime
import mimetypes
import os
import shutil


def create_folder(base_path, folder_name):
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def determine_category(mime_type):
    if mime_type.startswith("application/pdf"):
        return "PDFs"
    elif mime_type.startswith("application/vnd.openxmlformats-officedocument.wordprocessingml"):
        return "Word Documents"
    elif mime_type.startswith("application/vnd.ms-excel") or mime_type.startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml"):
        return "Excel Files"
    elif mime_type.startswith("image/"):
        return "Images"
    elif mime_type.startswith("text/"):
        return "Text Files"
    else:
        return "Other Files"


def move_files_by_type(source_path, sorted_base_path, log_file_path):
    movement_log = []
    for file in os.listdir(source_path):
        file_path = os.path.join(source_path, file)
        if os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                try:
                    category = determine_category(mime_type)
                    target_folder = create_folder(sorted_base_path, category)
                    target_path = os.path.join(target_folder, file)
                    shutil.move(file_path, target_path)
                    movement_log.append(f"{file_path} → {target_path}")
                except PermissionError as p:
                    print(str(p))
                    continue
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(movement_log))
        log_file.write(f"\n\nSummary:\nTotal Files Moved: {len(movement_log)}")
        log_file.write(f"\nSorted Categories: {', '.join(set(category for category in os.listdir(sorted_base_path)))}")


desktop_path = os.path.expanduser("~/Desktop")
path = os.path.expanduser("~/Downloads")
today_date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
sorted_folder_name = f"sorted_files_{today_date_time}"
sorted_base_path = create_folder(desktop_path, sorted_folder_name)
log_file_path = os.path.join(sorted_base_path, "movement_log.txt")

move_files_by_type(path, sorted_base_path, log_file_path)

print(f"Files have been sorted and a log created at: {log_file_path}")
