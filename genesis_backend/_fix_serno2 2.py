import sys
content = open('common/views.py').read()

old_bits = [
    "        with db_transaction.atomic():",
    "            seq, _ = Sequence.objects.select_for_update().get_or_create(",
    '                company=company, storecode=storecode, tablecode=code,',
    "                defaults={'sequence': 0},",
    "            )",
    "            seq.sequence = (seq.sequence or 0) + 1",
    "            seq.save(update_fields=['sequence'])",
    "            return f'{company}{storecode}_{code}_{seq.sequence}'",
]
old_block = '\\n'.join(old_bits) + '\\n'

new_bits = [
    "        with transaction.atomic():",
    "            seq = (",
    "                Sequence.objects.select_for_update()",
    "                .filter(company=company, storecode=storecode, tablecode=code)",
    "                .order_by('uuid')",
    "                .first()",
    "            )",
    "            if seq is None:",
    "                Sequence.objects.create(",
    "                    company=company, storecode=storecode, tablecode=code, sequence=0,",
    "                )",
    "                seq = (",
    "                    Sequence.objects.select_for_update()",
    "                    .filter(company=company, storecode=storecode, tablecode=code)",
    "                    .order_by('uuid')",
    "                    .first()",
    "                )",
    "            next_val = int(seq.sequence or 0) + 1",
    "            seq.sequence = next_val",
    "            seq.save(update_fields=['sequence'])",
    "            return f'{company}{storecode}_{code}_{next_val}'",
]
new_block = '\\n'.join(new_bits) + '\\n'

if old_block in content:
    content = content.replace(old_block, new_block)
    open('common/views.py', 'w').write(content)
    print('OK')
else:
    print('NOT FOUND')
    sys.exit(1)
