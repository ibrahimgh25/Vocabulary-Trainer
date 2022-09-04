from modules.main_application import TrainerApp

if __name__=='__main__':
    excel_file = 'resources/german_database.xlsx'
    sheet_name = 'A1'
    gui_resource_dir = 'resources/gui'
    app = TrainerApp(gui_resource_dir, mode='practice')
    app.main_loop()