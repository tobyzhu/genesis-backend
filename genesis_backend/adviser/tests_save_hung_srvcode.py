"""测试修复：验证 save_hung_order 中售卡时 srvcode_hung 被更新为卡号。

采用源码扫描方式（因 Django 项目有 MySQL 依赖无法在沙箱中运行完整集成测试）。
"""
import re, sys, os

project_root = '/Users/tobyzhu/Documents/AI/coding/Genesis/genesis_backend'
fp = os.path.join(project_root, 'adviser', 'views.py')

with open(fp, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'=== 检查 {fp} ===')
print(f'文件总行数: {len(lines)}\n')

# Find the key area: ttype == 'C' and srvcode block
in_card_sale_block = False
card_sale_lines = []
for i, line in enumerate(lines, 1):
    if "if ttype == 'C' and srvcode:" in line:
        in_card_sale_block = True
        print(f'【售卡块】找到 ttype=="C" 行 {i}')
    if in_card_sale_block:
        card_sale_lines.append((i, line))
        # Stop at the end of the block
        if 'exptxsernos.append' in line:
            break

print(f'\n--- 售卡块代码 ({len(card_sale_lines)} 行) ---')
for (no, ln) in card_sale_lines:
    print(f'{no:>5}: {ln}', end='')

print()

# Check for the fix
found_update = False
for (no, ln) in card_sale_lines:
    if 'update(' in ln and 'new_ccode' in ln:
        found_update = True
        if 'srvcode_hung=new_ccode' in ln and 'dnote_hung=new_ccode' in ln:
            print(f'\n✓ 修复已确认: 行 {no}')
            print(f'  update() 中同时包含 srvcode_hung=new_ccode 和 dnote_hung=new_ccode')
        elif 'srvcode_hung=new_ccode' not in ln and 'dnote_hung=new_ccode' in ln:
            print(f'\n✗ 修复缺失: 行 {no}')
            print(f'  只有 dnote_hung=new_ccode，缺少 srvcode_hung=new_ccode！')
            sys.exit(1)

if not found_update:
    print('\n✗ 未找到 update() 调用！')
    sys.exit(1)

# Also verify Python can compile the file
print('\n--- 编译检查 ---')
try:
    compile(open(fp, encoding='utf-8').read(), fp, 'exec')
    print('✓ 语法正确')
except SyntaxError as e:
    print(f'✗ 语法错误: {e}')
    sys.exit(1)

print('\n=== 全部通过 ===')
