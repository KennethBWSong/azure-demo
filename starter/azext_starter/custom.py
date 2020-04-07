# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core import get_default_cli
import random
import time


SERVICE_MAP = {
    'signalr': ('signalr', 'Azure SignalR Service', 1),
    'storage': ('storage','Azure Storage Service', 2),
    'webapp': ('webapp', 'Azure Web App Service', 3)
}
DEFAULT_CLI = get_default_cli()


# serive: string, including the service names, seperated by space
# resouce_group: name of resource group
def start(service, webapp_name, storage_name, resource_group=None):
    if not resource_group:
        raise CLIError('--resource-group not specified')
    service_list = validate(service)
    check_resource(service_list, resource_group)
    deploy(service_list, resource_group, webapp_name, storage_name)


# Check whether the serive is supported by checking in the SERVICE_MAP
def validate(service):
    result = []
    for s in service.split():
        if not s in SERVICE_MAP:
            raise CLIError('service %s is not recognized' % s)
        result.append(SERVICE_MAP[s])
    return sorted(result, key=lambda x: x[2])


# Check the status of service and resource group
def check_resource(service_list, resource_group):
    print('Resource Group %s already exists.' % resource_group)
    print('Connecting %s in resource group %s.' % (', '.join([s[1] for s in service_list]), resource_group))
    for s in service_list:
        print('No %s found.' % s[1])


# Create and deploy the services
def deploy(service_list, resource_group, webapp_name, storage_name):
    start = time.monotonic()
    deployment_id = random.randint(0, 1000000)
    settings = {}
    for service in service_list:
        if service[2] == 2:
            connectStorage(resource_group, settings, storage_name)
        elif service[2] == 3:
            connectWebApp(resource_group, settings, webapp_name)
        # create_resource(service, resource_group, deployment_id, settings)
    print('Complete in %d seconds' % (time.monotonic() - start))


def get_resource_name(resource, deployment_id):
    return '%s%d' % (resource.lower(), deployment_id)


def connectStorage(resource_group, settings, storage_name):
    parameters = [
        'storage', 'account', 'keys', 'list',
        '-n', storage_name,
        '-g', resource_group,
        '--query', '[0].value',
        '--output', 'tsv'
    ]
    DEFAULT_CLI.invoke(parameters)
    storage_key = DEFAULT_CLI.result.result
    print('Account Key of %s: %s' % (storage_name, storage_key))
    settings['AzureStorageConfig__AccountName'] = storage_name
    settings['AzureStorageConfig__AccountKey'] = storage_key
    settings['AzureStorageConfig__ImageContainer'] = 'images'
    settings['AzureStorageConfig__ThumbnailContainer'] = 'thumbnails'

def connectWebApp(resource_group, settings, webapp_name):
    parameters = [
        'webapp', 'config', 'appsettings', 'set',
        '--name', webapp_name,
        '--resource-group', resource_group,
        '--settings'
    ]
    for k, v in settings.items():
        parameters.append('%s=%s' % (k, v))
    DEFAULT_CLI.invoke(parameters)

# Using DEFAULT_CLI.invoke() to send CLI commands
def create_resource(service, resource_group, deployment_id, settings):
    if service[0] == 'signalr':
        # create SignalR resource
        resource_name = get_resource_name('mySignalR', deployment_id)
        print('Create %s resource: %s' % (service[1], resource_name))
        parameters = [
            'signalr', 'create',
            '--name', resource_name,
            '--resource-group', resource_group,
            '--sku', 'Standard_S1',
            '--unit-count', '1',
            '--service-mode', 'Default'
        ]
        if DEFAULT_CLI.invoke(parameters):
            raise CLIError('Fail to create resource %s' % resource_name)
        # get SignalR connection string
        parameters = [
            'signalr', 'key', 'list',
            '--name', resource_name,
            '--resource-group', resource_group,
            '--query', 'primaryConnectionString',
            '-o', 'tsv'
        ]
        DEFAULT_CLI.invoke(parameters)
        connection_string = DEFAULT_CLI.result.result
        settings['Azure:SignalR:ConnectionString'] = connection_string
        print('Connection string of %s: %s' % (resource_name, connection_string))

    elif service[0] == 'storage':
        # create a storage account
        account_name = get_resource_name('myStorageAccount',deployment_id)
        print('Create Storage Account: %s' % account_name)
        parameters = [
            'storage', 'account', 'create',
            '--name', account_name,
            '--resource-group', resource_group,
            '--sku', 'Standard_LRS',
            '--location', 'eastus',
            '--kind', 'StorageV2',
            '--access-tier', 'hot'
        ]
        if DEFAULT_CLI.invoke(parameters):
            raise CLIError('Fail to create storage account %s' % account_name)
        settings['AzureStorageConfig__AccountName'] = account_name
        # account_name = 'mystorageaccount269507'

        # get Storage account key
        parameters = [
            'storage', 'account', 'keys', 'list',
            '-n', account_name,
            '-g', resource_group,
            '--query', '[0].value',
            '--output', 'tsv'
        ]
        DEFAULT_CLI.invoke(parameters)
        account_key = DEFAULT_CLI.result.result
        print('Account Key of %s: %s' % (account_name, account_key))
        settings['AzureStorageConfig__AccountKey'] = account_key
        # create storage container
        parameters = [
            'storage', 'container', 'create',
            '-n', 'images',
            '--account-name', account_name,
            '--account-key', account_key,
            '--public-access', 'off'
        ]
        DEFAULT_CLI.invoke(parameters)
        settings['AzureStorageConfig__ImageContainer'] = 'images'
        parameters = [
            'storage', 'container', 'create',
            '-n', 'thumbnails',
            '--account-name', account_name,
            '--account-key', account_key,
            '--public-access', 'container'
        ]
        DEFAULT_CLI.invoke(parameters)
        settings['AzureStorageConfig__ThumbnailContainer'] = 'thumbnails'

    elif service[0] == 'webapp':
        # create App Service plan
        plan_name = get_resource_name('myAppService', deployment_id)
        print('Create App Service Plan: %s' % plan_name)
        parameters = [
            'appservice', 'plan', 'create',
            '--name', plan_name,
            '--resource-group', resource_group,
            '--sku', 'FREE'
        ]
        if DEFAULT_CLI.invoke(parameters):
            raise CLIError('Fail to create resource %s' % plan_name)
        # create Web App resource
        resource_name = get_resource_name('myWebApp', deployment_id)
        print('Create %s resource: %s' % (service[1], resource_name))
        parameters = [
            'webapp', 'create',
            '--name', resource_name,
            '--resource-group', resource_group,
            '--plan', plan_name
        ]
        if DEFAULT_CLI.invoke(parameters):
            raise CLIError('Fail to create resource %s' % resource_name)
        # config app settings
        print('Config app settings')
        parameters = [
            'webapp', 'config', 'appsettings', 'set',
            '--name', resource_name,
            '--resource-group', resource_group,
            '--settings'
        ]
        # settings['PROJECT'] = 'samples/ChatRoom/ChatRoom.csproj'
        for k, v in settings.items():
            parameters.append('%s=%s' % (k, v))
        DEFAULT_CLI.invoke(parameters)
        # deploy sample code
        # url = 'https://github.com/Azure-Samples/php-docs-hello-world'
        url = 'https://github.com/Azure-Samples/storage-blob-upload-from-webapp'
        print('Deploy sample code from %s' % url)
        parameters = [
            'webapp', 'deployment', 'source', 'config',
            '--name', resource_name,
            '--resource-group', resource_group,
            '--repo-url', url,
            '--branch', 'master',
            '--manual-integration'
        ]
        DEFAULT_CLI.invoke(parameters)
        print('App url: http://%s.azurewebsites.net/' % resource_name)
