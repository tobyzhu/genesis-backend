import re
with open('common/views.py') as f:
    content = f.read()

# Replace get_or_create pattern with order_by('uuid').first()
old = '''        with db_transaction.atomic():
            seq, _ = Sequence.objects.select_for_update().get_or_create(
                company=company, storecode=storecode, tablecode=code,
                defaults={'sequence': 0},
            )
            seq.sequence = (seq.sequence or 0) + 1
            seq.save(update_fields=['sequence'])
            return f'{company}{storecode}_{code}_{seq.sequence}''
    except (OperationalError, ProgrammingError):
        import time, uuid as _uuid
        suffix = str(int(time.time() * 1000)) + '_' + _uuid.uuid4().hex[:8]
        return f'{company}{storecode}_{code}_{suffix}''

new = '''        with transaction.atomic():
            seq = Sequence.objects.select_for_update().filter(
                company=company, storecode=storecode, tablecode=code
            ).order_by('uuid').first()
            if seq is None:
                Sequence.objects.create(
                    company=company, storecode=storecode, tablecode=code, sequence=0,
                )
                seq = Sequence.objects.select_for_update().filter(
                    company=company, storecode=storecode, tablecode=code
                ).order_by('uuid').first()
            next_val = int(seq.sequence or 0) + 1
            seq.sequence = next_val
            seq.save(update_fields=['sequence'])
            return f'{company}{storecode}_{code}_{next_val}''
    except (OperationalError, ProgrammingError):
        import time, uuid as _uuid
        suffix = str(int(time.time() * 1000)) + '_' + _uuid.uuid4().hex[:8]
        return f'{company}{storecode}_{code}_{suffix}''

if old in content:
    content = content.replace(old, new)
    with open('common/views.py', 'w') as f:
        f.write(content)
    print('✅ Fixed')
else:
    print('❌ Old pattern not found')
    idx = content.find('with db_transaction.atomic')
    if idx >= 0:
        print('Found at', idx, 'showing context:', repr(content[idx:idx+300]))
