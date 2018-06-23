import os
import subprocess
from cleo import Command
from masonite.packages import create_controller, append_web_routes, append_api_routes


package_directory = os.path.dirname(os.path.realpath(__file__))

class PublishCommand(Command):
    """
    Installs needed controllers and routes into a Masonite project

    entry:publish
        {--c|controller=None : Name of the controller you want to public}
        {--p|path=app/http/controller/Entry : The location you want to publish to}
    """

    def handle(self):

        if self.option('controller') != 'None':
            create_controller(
                os.path.join(package_directory,
                            '../api/controllers/{0}.py'.format(self.option('controller'))),
                to=self.option('path')
            )
