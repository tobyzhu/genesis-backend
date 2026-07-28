import sys
with open('common/views.py', encoding='utf-8-sig') as f:
    lines = f.readlines()

target = None
for i, line in enumerate(lines):
    if 'with db_transaction.atomic()' in line:
        target = i
        break

if target is None:
    print('NOT FOUND')
    sys.exit(1)

new_block = [
    '        with transaction.atomic():\n',
    '            seq = (\n',
    '                Sequence.objects.select_for_update()\n',
    '                .filter(company=company, storecode=storecode, tablecode=code)\n',
    "                .order_by('uuid')\n",
    '                .first()\n',
    '            )\n',
    '            if seq is None:\n',
    '                Sequence.objects.create(\n',
    '                    company=company, storecode=storecode, tablecode=code, sequence=0,\n',
    '                )\n',
    '                seq = (\n',
    '                    Sequence.objects.select_for_update()\n',
    '                    .filter(company=company, storecode=storecode, tablecode=code)\n',
    "                    .order_by('uuid')\n",
    '                    .first()\n',
    '                )\n',
    '            next_val = int(seq.sequence or 0) + 1\n',
    '            seq.sequence = next_val\n',
    "            seq.save(update_fields=['sequence'])\n",
    "            return f'{company}{storecode}_{code}_{next_val}'\n",
]

del lines[target:target+8]
for j, nl in enumerate(new_block):
    lines.insert(target + j, nl)

with open('common/views.py', 'w') as f:
    f.writelines(lines)
print('FIXED')
