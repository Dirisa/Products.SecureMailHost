#!/bin/bash

python=/usr/bin/python
i18ndude=../../i18ndude/i18ndude

if [ "$1" == "-c" ]; then
  # Create Master POT file
  $python $i18ndude rebuild-pot --pot psc.pot --create plonesoftwarecenter -s `find ../skins/ -iregex '.*\..?pt$'`
else
  # Update Existing POT file
  $python $i18ndude rebuild-pot --pot psc.pot -s `find ../skins/ -iregex '.*\..?pt$'`
fi

# Syncronize Language files
for PO in *.po; do
    $python $i18ndude sync --pot psc.pot -s $PO
done
