from lib.Hlopp import HloppReader
from lib.Aiello import AielloProject
# from lib.Convert import Converter
from lib.LegacyUpgrade import LegacyUpgrader
from lib.Rename import LegacyRenamer
from lib.Rescale import Rescaler
from lib.Undo import UndoTool
from lib.Zipper import Zipper
from lib.UniqueCols import UniqueExcel
from lib.MGCLChecker import MGCLChecker
from lib.BatchMover import BatchMover


class App:
    def __init__(self):
        self.hlopp = HloppReader()
        self.aiello = AielloProject()
        # self.converter = Converter()
        self.legacy_upgrader = LegacyUpgrader()
        self.renamer = LegacyRenamer()
        self.rescaler = Rescaler()
        self.uniquer = UniqueExcel()
        self.undo_tool = UndoTool()
        self.zipper = Zipper()
        self.mgclChecker = MGCLChecker()
        self.batchMover = BatchMover()
    
    # switch
    def run_selection(self, selection):
        if selection == 'exit':
            return
        elif selection == "aiello":
            self.aiello.run()
        elif selection == "convert":
            # self.converter.run()
            pass
        elif selection == "datamatrix":
            pass
        elif selection == "hlopp":
            self.hlopp.run()
        elif selection == "legacyUp":
            self.legacy_upgrader.run()
        elif selection == "rename":
            self.renamer.run()
        elif selection == "rescale":
            self.rescaler.run()
        elif selection == "uniquer":
            self.uniquer.run()
        elif selection == "zipper":
            self.zipper.run()
        elif selection == "undo":
            self.undo_tool.run()
        elif selection == "mgcl":
            self.mgclChecker.run()
        elif selection == "mover":
            self.batchMover.run()
        else:
            pass
        
        self.render_menu()

    # switch
    def interpret_menu_selection(self, selection):
        if selection.lower() in ['1', 'aiello']:
            return "aiello"
        elif selection.lower() in ['2', 'convert']:
            return "convert"
        elif selection.lower() in ['3', 'datamatrix']:
            return "datamatrix"
        elif selection.lower() in ['4', 'hlopp']:
            return "hlopp"
        elif selection.lower() in ['5', 'legacy upgrade', 'legacy upgrade project']:
            return "legacyUp"
        elif selection.lower() in ['6', 'rename']:
            return "rename"
        elif selection.lower() in ['7', 'rescale']:
            return "rescale"
        elif selection.lower() in ['8', 'uniquer']:
            return "uniquer"
        elif selection.lower() in ['9', 'zipper']:
            return "zipper"
        elif selection.lower() in ['10', 'undo']:
            return "undo"
        elif selection.lower() in ['11', 'mgcl']:
            return "mgcl"
        elif selection.lower() in ['12', 'mover']:
            return "mover"
        elif selection.lower() == 'exit':
            return "exit"
        else:
            return "INVALID"
    
    def render_menu(self):
        menu = (
            "Select program to load:\n\n" \
            "[1] Aiello Project\n" \
            "[2] Convert CR2 -> JPG\n" \
            "[4] Datamatrix Project\n" \
            "[4] Hlopp Project\n" \
            "[5] Legacy Upgrade Project\n" \
            "[6] Rename Project (Legacy)\n" \
            "[7] Rescale JPGs (Downscaler)\n" \
            "[8] Unique Value Tool (Database CSV)\n" \
            "[9] Zipper Tool\n" \
            "[10] Undo Tool\n" \
            "[11] MGCL Checker\n" \
            "[12] Batch Mover\n\n" \
            "or 'exit' to quit.\n\n--> " \
        )

        selection = self.interpret_menu_selection(input(menu))
        print()

        if selection == 'INVALID':
            print('\nInvalid selection.\n')
            self.render_menu()
        else: 
            self.run_selection(selection)

    def run(self):
        self.render_menu()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()