from ...parsers import subscription_manager_list
from ...tests import context_wrap

import doctest

subscription_manager_list_consumed_in_docs = '''
+-------------------------------------------+
   Consumed Subscriptions
+-------------------------------------------+
Subscription Name: Red Hat Enterprise Linux Server, Premium (1-2 sockets) (Up to 1 guest)
Provides:          Oracle Java (for RHEL Server)
                   Red Hat Software Collections Beta (for RHEL Server)
                   Red Hat Enterprise Linux Server
                   Red Hat Beta
SKU:               RH0155783S
Contract:          12345678
Account:           1000001
Serial:            0102030405060708090
Pool ID:           8a85f981477e5284014783abaf5d4dcd
Active:            True
Quantity Used:     1
Service Level:     PREMIUM
Service Type:      L1-L3
Status Details:    Subscription is current
Subscription Type: Standard
Starts:            11/14/14
Ends:              07/06/15
System Type:       Physical
'''

subscription_manager_list_installed_in_docs = '''
+-------------------------------------------+
Installed Product Status
+-------------------------------------------+
Product Name:   Red Hat Software Collections (for RHEL Server)
Product ID:     201
Version:        2
Arch:           x86_64
Status:         Subscribed
Status Details:
Starts:         04/27/15
Ends:           04/27/16

Product Name:   Red Hat Enterprise Linux Server
Product ID:     69
Version:        7.1
Arch:           x86_64
Status:         Subscribed
Status Details:
Starts:         04/27/15
Ends:           04/27/16
'''

subscription_manager_repos_list_enabled_test_data = '''
+----------------------------------------------------------+
    Available Repositories in /etc/yum.repos.d/redhat.repo
+----------------------------------------------------------+
Repo ID:   rhel-7-server-ansible-2-rpms
Repo Name: Red Hat Ansible Engine 2 RPMs for Red Hat Enterprise Linux 7 Server
Repo URL:  https://cdn.redhat.com/content/dist/rhel/server/7/7Server/$basearch/ansible/2/os
Enabled:   1
'''


def test_subscription_manager_list_docs():
    env = {
        'SubscriptionManagerListConsumed': subscription_manager_list.SubscriptionManagerListConsumed,
        'SubscriptionManagerListInstalled': subscription_manager_list.SubscriptionManagerListInstalled,
        'SubscriptionManagerReposListEnabled': subscription_manager_list.SubscriptionManagerReposListEnabled,
        'shared': {
            subscription_manager_list.SubscriptionManagerListConsumed: subscription_manager_list.SubscriptionManagerListConsumed(
                context_wrap(subscription_manager_list_consumed_in_docs)
            ),
            subscription_manager_list.SubscriptionManagerListInstalled: subscription_manager_list.SubscriptionManagerListInstalled(
                context_wrap(subscription_manager_list_installed_in_docs)
            ),
            subscription_manager_list.SubscriptionManagerReposListEnabled: subscription_manager_list.SubscriptionManagerReposListEnabled(
                context_wrap(subscription_manager_repos_list_enabled_test_data)
            )
        },
    }
    failed, total = doctest.testmod(subscription_manager_list, globs=env)
    assert failed == 0


subscription_manager_list_test_data = '''
+-------------------------------------------+
   Consumed Subscriptions
+-------------------------------------------+
Subscription Name: Red Hat Enterprise Linux Server, Premium (1-2 sockets) (Up to 1 guest)
Subscription Type: Standard
Starts:            17/2
'''

subscription_manager_list_no_installed_products = '''
No installed products to list
'''


def test_subscription_manager_list_exceptions():
    sml = subscription_manager_list.SubscriptionManagerListConsumed(
        context_wrap(subscription_manager_list_test_data)
    )
    assert len(sml.records) == 1
    rec0 = sml.records[0]
    assert 'Subscription Name' in rec0
    assert 'Subscription Type' in rec0
    assert 'Starts' in rec0
    assert rec0['Starts'] == '17/2'
    assert 'Starts timestamp' not in rec0

    sml = subscription_manager_list.SubscriptionManagerListInstalled(
        context_wrap(subscription_manager_list_no_installed_products)
    )
    assert sml.records == []
