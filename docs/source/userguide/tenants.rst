.. _tenants:
Tenants
=======

Introduction
------------
*Tenants* are the entities for which one can provide services (think if them as customers). When Tachyonic is installed
initially, there are no tenants in the system. :ref:`Users' <users>` accounts can be associated to a *Tenant*.
Tachyonic is a multi-tier multi-tenant system.
This means when a *User* that is associated to a *Tenant* is logged in, that user can only view
*services, roles, domains* etc that is assigned to the particular *Tenant*. It also means that they can create *Tenants*
themselves. This is for example useful in a reseller model.

Most things in Tachyonic require a tenant to be selected. This is called the "Current Open Tenant", and it determines
the *Users*, *Tenants*, *Roles* and *Domains* that will be displayed and available in the system.

Typically, one would already have some CRM system that contains all the Customer/Tenant information. Since Tachyonic
comes with a REST API, it is trivial to populate Tenants from such a system. That way, there is "one source of truth"
for Tenant information, which prevents multiple systems getting out of sync.

For those who prefer to run Tachyonic as a stand-alone solution, a convienient way of managing tenants have been provided
with the Tachyonic UI, described here.

Creating/Adding Tenants
-----------------------
To Create/Add a tenant, navigate to `Accounts -> Tenants`, and click on the ``Create`` button. Only The *Name* Field
is required. By default, the *Enabled* option is not selected. Select this option to activate the *Tenant*.


Selecting Tenants
-----------------
Once a Tenant has been added (and enabled) to the system, it can be selected to become the "Current Open Tenant". To
search through the *Tenants*, use the Search bar at the top right of the Tachyonic UI. Names will auto populate after
three characters has been typed. Hit the Search button to see a list of results in the main Tachyonic window.

In order to select a *Tenant*, click on the ``Open`` button next to the *Tenant* name in the search results.
The "Current Open Tenant" is displayed at the top left of the Tachyonic screen. Once selected, all features of
the system applies only to the "Current Open Tenant".
To close the "Current Open Tenant", select another *Tenant* as described here, or hit the ``Close``
button next to the name of the "Current Open Tenant" at the top left.

.. _viewtenant:

Viewing Tenant Information
--------------------------
In order to view *Tenant* information, navigate to ``Accounts -> Tenants``, and click on the magnifying glass icon
next to the applicable *Tenant*.
This will launch the *View Tenant* window, which will display the current information associated with the Tenant.

.. _edittenant:

Modifying Tenant Information
----------------------------
In order to update Tenant information, follow the same procedure as in
:ref:`viewtenant`, and click on the ``edit`` button. This will launch the *Edit Tenant* window.
Update the information accordingly, and hit the ``Save`` button.

Deleting a Tenant
-----------------
In order to delete a Tenant, follow the same procedure as in :ref:`edittenant`, and click on
the ``delete`` button. A confirmation dialog will pop up. Hit the ``Continue`` button to permanently delete the Tenant
account, or hit ``Cancel`` to return to the previous form.

