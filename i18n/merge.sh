#!/bin/bash
for PO in pfm*.po; do
    i18ndude.py sync --pot pfm.pot -s $PO
done

for PO in plone*.po; do
    i18ndude.py sync --pot plone-pfm.pot -s $PO
done
