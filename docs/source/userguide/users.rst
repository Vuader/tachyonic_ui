.. _users:
Users
=====

Introduction
------------

Each user of the Tachyonic Framework requires a User account. The default administrative login user account is *root*, and the password is *password*.

By default no URL is available if a user is not logged in, save that of the login URL. There is a time-out if there are no user activityfor 5 minutes,
after which the user is automatically logged out.

Creating/Adding Users
---------------------
To create a new user account, navigate to ``Accounts -> Users`` and click on the ``Create`` button. This will launch the *Create User* form.

The Fields are self explanatory, and only the username, password and Name fields are mandatory. Passwords require at
least one upper case, one lower case, and one numeric character. By default, the Account *enabled* check box is not checked.
In order to activate the account, check this box before hitting the ``Create`` button.

.. _viewuser:

Viewing User Account Information
--------------------------------
In order to view User Account information, navigate to ``Accounts -> Users``, and click on the magnifying glass icon. This will launch the *View User* window,
which will display the current information associated with the user.

.. _edituser:

Modifying User Account Information
----------------------------------
In order to update User account information such as username or password, follow the same procedure as in :ref:`viewuser`, and click on
the ``edit`` button. This will launch the *Edit User* window. Update the information accordingly, and hit the ``Save`` button.

Deleting a User account
-----------------------
In order to delete a User account, follow the same procedure as in :ref:`edituser`, and click on
the ``delete`` button. A confirmation dialog will pop up. Hit the ``Continue`` button to permanently delete the user
account, or hit ``Cancel`` to return to the previous form.
