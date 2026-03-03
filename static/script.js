// 消费者端检测
document.addEventListener('DOMContentLoaded', function() {
    const consumerBtn = document.getElementById('consumerDetectBtn');
    if (consumerBtn) {
        consumerBtn.addEventListener('click', function() {
            const text = document.getElementById('consumerText').value;
            if (!text.trim()) {
                alert('请输入文案');
                return;
            }
            fetch('/api/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    renderResult(data.result, 'consumerResult');
                }
            })
            .catch(err => alert('网络错误'));
        });
    }

    // 商家端检测
    const merchantBtn = document.getElementById('merchantDetectBtn');
    if (merchantBtn) {
        merchantBtn.addEventListener('click', function() {
            const text = document.getElementById('merchantText').value;
            if (!text.trim()) {
                alert('请输入文案');
                return;
            }
            fetch('/api/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    renderResult(data.result, 'merchantResult');
                }
            })
            .catch(err => alert('网络错误'));
        });
    }
});

// 渲染结果（通用）
function renderResult(sentences, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    sentences.forEach((item, index) => {
        const block = document.createElement('div');
        block.className = `sentence-block level-${item.level}`;

        const sentenceDiv = document.createElement('div');
        sentenceDiv.className = 'sentence-text';
        sentenceDiv.textContent = item.sentence;
        block.appendChild(sentenceDiv);

        if (item.matches.length > 0) {
            const matchesDiv = document.createElement('div');
            matchesDiv.className = 'matches';
            matchesDiv.innerHTML = '⚠️ 包含违规词：' + item.matches.map(m => `${m.word}（${m.level}级）`).join('、');
            block.appendChild(matchesDiv);
        }

        // 如果是C级且当前是商家端，显示优化按钮（简单判断容器id）
        if (item.level === 'C' && containerId === 'merchantResult') {
            const improveBtn = document.createElement('button');
            improveBtn.className = 'improve-btn';
            improveBtn.textContent = '✨ AI 优化';
            improveBtn.onclick = () => improveSentence(item.sentence, block, index);
            block.appendChild(improveBtn);
        }

        container.appendChild(block);
    });
}

// AI优化（调用后端接口）
function improveSentence(text, block, index) {
    fetch('/api/improve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert('优化失败：' + data.error);
        } else {
            // 弹出优化结果，并可以替换原句（这里简单弹窗，你可以扩展）
            alert('优化建议：\n' + data.improved);
            // 如果你想让用户直接替换，可以添加确认后修改 textarea 的逻辑，这里先简化
        }
    })
    .catch(err => alert('网络错误'));
}
// PDF报告生成函数
function generatePDF(result) {
    if (!window.jspdf) {
        alert('PDF库加载中，请稍后');
        return;
    }
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const sentences = result.sentences || [];
    const originalText = result.text || '';
    
    // 封面
    doc.setFillColor(100, 163, 134);
    doc.rect(0, 0, 210, 40, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.text('法镜广告合规检测报告', 105, 25, { align: 'center' });
    
    // 报告信息
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.text(`报告编号: FJ-${Date.now()}`, 20, 55);
    doc.text(`生成时间: ${result.timestamp || new Date().toLocaleString('zh-CN')}`, 20, 62);
    doc.text(`检测来源: 消费者端`, 20, 69);
    
    // 风险统计
    const levelCount = {
        A: sentences.filter(s => s.level === 'A').length,
        B: sentences.filter(s => s.level === 'B').length,
        C: sentences.filter(s => s.level === 'C').length
    };
    
    doc.setFontSize(14);
    doc.text('风险统计', 20, 85);
    doc.setFontSize(10);
    doc.text(`A级风险 (严重违规): ${levelCount.A} 处`, 25, 95);
    doc.text(`B级风险 (需资质): ${levelCount.B} 处`, 25, 102);
    doc.text(`C级风险 (建议优化): ${levelCount.C} 处`, 25, 109);
    
    // 原文
    doc.setFontSize(14);
    doc.text('检测原文', 20, 125);
    doc.setFontSize(10);
    const splitText = doc.splitTextToSize(originalText, 170);
    doc.text(splitText, 20, 135);
    
    // 详细结果
    doc.addPage();
    doc.setFontSize(16);
    doc.text('详细检测结果', 105, 20, { align: 'center' });
    
    let yPos = 40;
    sentences.forEach((s, index) => {
        if (yPos > 270) {
            doc.addPage();
            yPos = 20;
        }
        
        doc.setFontSize(11);
        doc.setTextColor(
            s.level === 'A' ? 229 : (s.level === 'B' ? 221 : (s.level === 'C' ? 56 : 0)),
            s.level === 'A' ? 62 : (s.level === 'B' ? 107 : (s.level === 'C' ? 161 : 0)),
            s.level === 'A' ? 62 : (s.level === 'B' ? 32 : (s.level === 'C' ? 105 : 0))
        );
        doc.text(`${index+1}. ${s.sentence}`, 20, yPos);
        yPos += 7;
        
        if (s.matches.length > 0) {
            doc.setFontSize(9);
            doc.setTextColor(102, 102, 102);
            doc.text(`   违规词: ${s.matches.map(m => m.word).join('、')}`, 20, yPos);
            yPos += 7;
        }
        
        yPos += 5;
    });
    
    // 底部声明
    doc.setFontSize(8);
    doc.setTextColor(153, 153, 153);
    doc.text('本报告由法镜AI自动生成，仅供参考，不构成法律意见。', 105, 290, { align: 'center' });
    
    // 保存
    doc.save(`法镜报告_${new Date().toISOString().slice(0,10)}.pdf`);
}

// 在消费者端添加PDF按钮事件
document.addEventListener('DOMContentLoaded', function() {
    const downloadBtn = document.getElementById('consumerDownloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            if (window.lastDetectResult) {
                generatePDF(window.lastDetectResult);
            } else {
                alert('请先进行检测');
            }
        });
    }
});