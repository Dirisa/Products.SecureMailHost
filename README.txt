A tool for breaking throug the acquisition of Plone.

See requirements in install.txt

With this tool you can set a breakpoint in aquisition so that only members wich are defined in local roles or  member of a group 
or member in a team are allowed to access to the folder. There is no modifying of permissions or handling roles in zope/plone.
That means if a user has a right the right is not removed in setting a breakpoint. Only the membership is remove.
if you put a Reviewer with a local member role in a folder with a breakpoint he will have still Reviewer rights in
the folder.


Fell free to give feedback so we can make this product better info@tomcom.de or kai.hoppert@tomcom.de

There is no aqusition breaking for Managers. So we can shure that we not exclude everyone :).

!!Important!! Workflow is default only installed for folder. So plz add it by hand if you want to test it with TeamSpace.