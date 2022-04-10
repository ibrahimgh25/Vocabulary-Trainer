from modules import LanguageTrainer

if __name__=='__main__':
    # excel_file = 'resources/german_database.xlsx'
    # sheet_name = 'A1'
    # trainer = LanguageTrainer(excel_file, sheet_name)
    # # Set the direction from english to german
    # trainer.set_direction('Backward')
    # # Do a training session
    # trainer.translation_session('noun')
    # # Save the database
    # trainer.save_database(excel_file, sheet_name)
    from modules.gui import MainApp
    app = MainApp()
    app.mainloop()
