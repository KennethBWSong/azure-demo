# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.help_files import helps


helps['starter'] = """
    type: command
    short-summary: Quick start on Azure services.
    examples:
        - name: Provision and deploy demo code for Azure services.
          text: az starter 'webapp signalr' --resource-group rg
"""


class StarterCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_starter.custom#{}')
        super(StarterCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, _):
        with self.command_group('') as g:
            # start()
            g.custom_command('starter', 'start')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('starter') as c:
            c.positional('service', help='Service you want to start, use space as delimiter for multiple services.')
            c.argument('resource_group', options_list=['--resource-group', '-g'], help='Resouce group to provision services.')
            c.argument('webapp_name', options_list = ['--webapp-name'], help = 'Name of the webapp.')
            c.argument('storage_name', options_list = ['--storage-name'], help = 'Name of the webapp.')


COMMAND_LOADER_CLS = StarterCommandsLoader