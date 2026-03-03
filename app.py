import os
import re
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量

app = Flask(__name__)

# 模拟的违规词库（基于你提供的 FaJing中文禁词.docx）
keyword_db = [
    # A级
    {"word": "最", "level": "A"}, {"word": "最顶尖", "level": "A"}, {"word": "第一", "level": "A"},
    {"word": "顶级", "level": "A"}, {"word": "最佳", "level": "A"}, {"word": "最好", "level": "A"},
    {"word": "最强", "level": "A"}, {"word": "最高", "level": "A"}, {"word": "最便宜", "level": "A"},
    {"word": "最优秀", "level": "A"}, {"word": "最先进", "level": "A"}, {"word": "最实惠", "level": "A"},
    {"word": "最专业", "level": "A"}, {"word": "最安全", "level": "A"}, {"word": "最有效", "level": "A"},
    {"word": "100%", "level": "A"}, {"word": "百分之百", "level": "A"}, {"word": "完全", "level": "A"},
    {"word": "彻底", "level": "A"}, {"word": "绝对", "level": "A"}, {"word": "永不", "level": "A"},
    {"word": "绝无", "level": "A"}, {"word": "完美", "level": "A"}, {"word": "极致", "level": "A"},
    {"word": "无敌", "level": "A"}, {"word": "史无前例", "level": "A"}, {"word": "极品", "level": "A"},
    {"word": "终极", "level": "A"}, {"word": "国家级", "level": "A"}, {"word": "国家", "level": "A"},
    {"word": "中国", "level": "A"}, {"word": "中央", "level": "A"}, {"word": "政府", "level": "A"},
    {"word": "国务院", "level": "A"}, {"word": "党中央", "level": "A"}, {"word": "保证", "level": "A"},
    {"word": "担保", "level": "A"}, {"word": "承诺", "level": "A"}, {"word": "无效退款", "level": "A"},
    {"word": "安全无毒", "level": "A"}, {"word": "无任何副作用", "level": "A"}, {"word": "根治", "level": "A"},
    {"word": "治愈", "level": "A"}, {"word": "特效", "level": "A"}, {"word": "神奇", "level": "A"},
    {"word": "秘方", "level": "A"},
    # B级
    {"word": "专利", "level": "B"}, {"word": "专利号", "level": "B"}, {"word": "发明专利", "level": "B"},
    {"word": "实用新型", "level": "B"}, {"word": "外观设计", "level": "B"}, {"word": "认证", "level": "B"},
    {"word": "ISO", "level": "B"}, {"word": "质量认证", "level": "B"}, {"word": "环保认证", "level": "B"},
    {"word": "安全认证", "level": "B"}, {"word": "通过认证", "level": "B"}, {"word": "权威认证", "level": "B"},
    {"word": "资质", "level": "B"}, {"word": "许可证", "level": "B"}, {"word": "执照", "level": "B"},
    {"word": "资格证书", "level": "B"}, {"word": "行业标准", "level": "B"}, {"word": "国家标准", "level": "B"},
    {"word": "获奖", "level": "B"}, {"word": "金奖", "level": "B"}, {"word": "银奖", "level": "B"},
    {"word": "铜奖", "level": "B"}, {"word": "荣誉称号", "level": "B"}, {"word": "驰名商标", "level": "B"},
    {"word": "著名商标", "level": "B"}, {"word": "老字号", "level": "B"},
    # C级
    {"word": "优于", "level": "C"}, {"word": "超过", "level": "C"}, {"word": "打败", "level": "C"},
    {"word": "击败", "level": "C"}, {"word": "胜过", "level": "C"}, {"word": "强于", "level": "C"},
    {"word": "领导品牌", "level": "C"}, {"word": "领导者", "level": "C"}, {"word": "领先", "level": "C"},
    {"word": "领军", "level": "C"}, {"word": "第一品牌", "level": "C"}, {"word": "行业第一", "level": "C"},
    {"word": "十万", "level": "C"}, {"word": "百万", "level": "C"}, {"word": "千万", "level": "C"},
    {"word": "亿", "level": "C"}, {"word": "%", "level": "C"}, {"word": "立即见效", "level": "C"},
    {"word": "马上", "level": "C"}, {"word": "瞬间", "level": "C"}, {"word": "立刻", "level": "C"},
    {"word": "马上见效", "level": "C"}, {"word": "立竿见影", "level": "C"}, {"word": "显著优于", "level": "C"},
    {"word": "安全无毒", "level": "C"}, {"word": "彻底解决", "level": "C"}, {"word": "独家技术", "level": "C"},
    {"word": "特效", "level": "C"}, {"word": "独家", "level": "C"},
]

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 消费者端
@app.route('/consumer')
def consumer():
    return render_template('consumer.html')

# 商家端
@app.route('/merchant')
def merchant():
    return render_template('merchant.html')

# 登录
@app.route('/login')
def login():
    return render_template('login.html')

# 注册
@app.route('/register')
def register():
    return render_template('register.html')

# 关于我们
@app.route('/about')
def about():
    return render_template('about.html')

# 个人中心
@app.route('/dashboard')
def dashboard():
    return render_template('personal.html')

# 数据看板
@app.route('/dashboard-new')
def dashboard_new():
    return render_template('dashboard_new.html')

# 检测接口（供前端调用）
@app.route('/api/detect', methods=['POST'])
def detect():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': '请输入文本'}), 400

    # 按句号、感叹号、问号分割句子
    sentences = re.split(r'(?<=[。！？])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    result = []
    for sent in sentences:
        # 查找句子中包含的违规词
        matches = [item for item in keyword_db if item['word'] in sent]
        # 确定最高等级
        level = 'none'
        if any(m['level'] == 'A' for m in matches):
            level = 'A'
        elif any(m['level'] == 'B' for m in matches):
            level = 'B'
        elif any(m['level'] == 'C' for m in matches):
            level = 'C'
        result.append({
            'sentence': sent,
            'level': level,
            'matches': matches
        })
    return jsonify({'result': result})

# 一键美化接口（调用 DeepSeek API）
@app.route('/api/improve', methods=['POST'])
def improve():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': '请输入文本'}), 400

    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        return jsonify({'error': 'API密钥未配置'}), 500

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 构建提示词，要求返回完全合规的文案
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'system', 
                'content': '''你是一个广告合规专家。请将用户输入的广告文案改写为完全符合中国广告法的合规版本，必须遵守：
1. 删除所有绝对化用语（最、第一、国家级、100%等）
2. 删除所有虚假承诺（根治、治愈、保证等）
3. 对需要资质的表述（专利、认证等）添加"据称"、"宣称"等客观表述，或替换为更客观的说法
4. 保持原文的核心意思和产品优点
5. 返回改写后的完整文案，不要额外解释'''
            },
            {'role': 'user', 'content': text}
        ],
        'temperature': 0.7
    }

    try:
        response = requests.post('https://api.deepseek.com/v1/chat/completions', json=payload, headers=headers)
        response.raise_for_status()
        improved = response.json()['choices'][0]['message']['content']
        return jsonify({'improved': improved})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))