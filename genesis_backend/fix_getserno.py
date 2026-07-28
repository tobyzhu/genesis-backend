import sys
content = open('common/views.py', encoding='utf-8').read()

old = ('        with db_transaction.atomic():\n'
       '            seq, _ = Sequence.objects.select_for_update().get_or_create(\n'
       "                company=company, storecode=storecode, tablecode=code,\n"
       "                defaults={'sequence': 0},\n"
       '            )\n'
       '            seq.sequence = (seq.sequence or 0) + 1\n'
       "            seq.save(update_fields=['sequence'])\n"
       "            return f'{company}{storecode}_{code}_{seq.sequence}'\n")

new = ('        with transaction.atomic():\n'
       '            seq = (\n'
       '                Sequence.objects.select_for_update()\n'
       '                .filter(company=company, storecode=storecode, tablecode=code)\n'
       "                .order_by('uuid')\n"
       '                .first()\n'
       '            )\n'
       '            if seq is None:\n'
       '                Sequence.objects.create(\n'
       '                    company=company, storecode=storecode, tablecode=code, sequence=0,\n'
       '                )\n'
       '                seq = (\n'
       '                    Sequence.objects.select_for_update()\n'
       '                    .filter(company=company, storecode=storecode, tablecode=code)\n'
       "                    .order_by('uuid')\n"
       '                    .first()\n'
       '                )\n'
       '            next_val = int(seq.sequence or 0) + 1\n'
       '            seq.sequence = next_val\n'
       "            seq.save(update_fields=['sequence'])\n"
       "            return f'{company}{storecode}_{code}_{next_val}'\n")

if old in content:
    content = content.replace(old, new)
    open('common/views.py', 'w', encoding='utf-8').write(content)
    print('FIXED')
else:
    print('NOT FOUND')
    sys.exit(1)
