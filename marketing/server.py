"""Genesis 推广落地页后端 — 线索收集服务
用法: python marketing/server.py
端口: 8099 (可通过 PORT 环境变量覆盖)
"""
import os, json, datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, abort

app = Flask(__name__)
LEADS_FILE = Path(__file__).parent / 'leads.jsonl'

def _load_leads():
    if not LEADS_FILE.exists():
        return []
    leads = []
    with open(LEADS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                leads.append(json.loads(line))
    return leads

def _append_lead(data):
    data['created_at'] = datetime.datetime.now().isoformat()
    data['status'] = 'pending'
    with open(LEADS_FILE, 'a') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
    return data

@app.route('/')
def index():
    html_path = Path(__file__).parent / 'index.html'
    return send_file(str(html_path))

@app.route('/api/trial-signup', methods=['POST'])
def trial_signup():
    """收集试用申请"""
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': '请求体为空'}), 400

    store_name = (data.get('store_name') or '').strip()
    contact_name = (data.get('contact_name') or '').strip()
    phone = (data.get('phone') or '').strip()

    errors = {}
    if not store_name:
        errors['store_name'] = '请填写门店名称'
    if not contact_name:
        errors['contact_name'] = '请填写联系人'
    if not phone:
        errors['phone'] = '请填写手机号'
    elif not __import__('re').match(r'^1\d{10}$', phone):
        errors['phone'] = '请填写正确的手机号(11位)'

    if errors:
        return jsonify({'error': '表单验证失败', 'fields': errors}), 400

    lead = _append_lead({
        'store_name': store_name,
        'contact_name': contact_name,
        'phone': phone,
        'store_count': data.get('store_count', 1),
        'current_system': data.get('current_system', ''),
        'remark': data.get('remark', ''),
    })
    return jsonify({'message': '申请已提交，我们将在 24 小时内与你联系。', 'id': lead['created_at']}), 201

@app.route('/api/leads')
def list_leads():
    """查看线索列表（简易后台）"""
    auth = request.args.get('token', '')
    if auth != os.environ.get('GENESIS_ADMIN_TOKEN', 'genesis123'):
        abort(401)
    leads = _load_leads()
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    start = (page - 1) * size
    end = start + size
    return jsonify({
        'total': len(leads),
        'page': page,
        'size': size,
        'data': leads[start:end],
    })

@app.route('/api/leads/count')
def lead_count():
    """线索数量统计"""
    auth = request.args.get('token', '')
    if auth != os.environ.get('GENESIS_ADMIN_TOKEN', 'genesis123'):
        abort(401)
    leads = _load_leads()
    total = len(leads)
    pending = sum(1 for l in leads if l.get('status') == 'pending')
    return jsonify({'total': total, 'pending': pending})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8099))
    print(f"Genesis 推广服务启动: http://0.0.0.0:{port}")
    print(f"线索文件: {LEADS_FILE}")
    app.run(host='0.0.0.0', port=port, debug=True)
