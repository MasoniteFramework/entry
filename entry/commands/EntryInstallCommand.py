import os
from masonite.packages import create_controller, append_web_routes


package_directory = os.path.dirname(os.path.realpath(__file__))

class EntryInstallCommand:

    def execute(self):
        create_controller(
            os.path.join(package_directory,
                         '../entry_snippets/controllers/PasswordGrantController.py'),
            to='app/http/controllers/Entry/Api'
        )

        append_web_routes(
            os.path.join(package_directory,
                         '../entry_snippets/routes/EntryRoutes.py')
        )

