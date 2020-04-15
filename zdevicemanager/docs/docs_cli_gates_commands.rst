.. _zdm-cmd-gates:


Webhooks
========

Using the ZDM you’re able to receive your device’s data on your webhooks.
You can activate a webhook to receive all the data sent on a specific tag in a workspace.
ZDM allows you also to visualize data on Ubidots through a Webhook.


List of commands:

* :ref:`Create <zdm-cmd-webhook-start>`
* :ref:`List webhooks <zdm-cmd-webhook-get-all>`
* :ref:`Get a single webhook <zdm-cmd-webhook-get-webhook>`
* :ref:`Delete a webhook <zdm-cmd-webhook-delete>`
* :ref:`Disable a webhook <zdm-cmd-webhook-disable>`
* :ref:`Enable a webhook <zdm-cmd-webhook-enable>`


    
.. _zdm-cmd-webhook-start:

Webhook creation
----------------

To create a new webhook use the command: ::

    zdm webhook start name url token period workspace_id

where :samp:`name` is the name that you want to give to your new webhook
:samp:`url` is the your webhook
:samp:`token` is the authentication token for your webhook (if needed)

:samp:`workspace_id` is the uid of the workspace you want to receive data from

You also have the possibility to add filters on data using the following options:

:option:`--tag` To specify a tag to filter data (you can specify more than one)
:option:`--fleet` To specify a fleet to filter data (you can specify more than one)
:option:`--token` Token used as value of the Authorization Bearer fot the webhook endpoint.
:option:`--origin` Webhook source (data or events) by default is data.

    
.. _zdm-cmd-webhook-get-all:

List webhooks
-------------

To see a list of your webhooks use the command: ::

    zdm webhook all workspace_id

where :samp:`workspace_id` is the uid of the workspace you want to receive data from.

You also have the possibility to add filters on data using the following options:

* :option:`--status active|disabled` to filter on webhook status
* :option:`--origin data` to filter on data origin (data)

    
.. _zdm-cmd-webhook-get-webhook:

Get a webhook
-------------

To see information about a single webhook use the command: ::

    zdm webhook get webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-webhook-disable:

Disable a webhook
-----------------

To disable a webhook use the command: ::

    zdm webhook disable webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-webhook-enable:

Enable a webhook
-----------------

To enable a webhook use the command: ::

    zdm webhook enable webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
.. _zdm-cmd-webhook-delete:

Delete a webhook
-----------------

To delete a webhook use the command: ::

    zdm webhook delete webhook_id

where :samp:`webhook_id` is the uid of the webhook.

    
