from modules import LanguageTrainer

if __name__=='__main__':
    excel_file = 'resources/german_database.xlsx'
    sheet_name = 'A1'
    gui_resource_dir = 'resources/gui'
    trainer = LanguageTrainer(excel_file, sheet_name, gui_resource_dir)
    trainer.main_loop()