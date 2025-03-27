document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const queryByMd5Form = document.getElementById('queryByMd5Form');
    const queryByFileForm = document.getElementById('queryByFileForm');
    const resultDiv = document.getElementById('result');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const queryFileInput = document.getElementById('queryFileInput');
    const queryFilePreview = document.getElementById('queryFilePreview');

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            filePreview.innerHTML = `<div class="selected-file"><span class="file-icon">📄</span>${this.files[0].name}</div>`;
        } else {
            filePreview.innerHTML = '';
        }
    });

    queryFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            queryFilePreview.innerHTML = `<div class="selected-file"><span class="file-icon">📄</span>${this.files[0].name}</div>`;
        } else {
            queryFilePreview.innerHTML = '';
        }
    });

    function showMessage(message, isError = false) {
        resultDiv.innerHTML = `<div class="${isError ? 'error' : 'success'}-message">${message}</div>`;
    }

    function showResult(data) {
        if (data.filenames && data.filenames.length > 0) {
            const filenamesList = data.filenames.map(filename => `<li><span class="file-icon">📄</span>${filename}</li>`).join('');
            resultDiv.innerHTML = `
                <div class="result-item">
                    <h3>文件信息</h3>
                    <p>MD5：${data.md5}</p>
                    <p>版本：${data.version}</p>
                    <div class="filenames-list">
                        <p>文件名列表：</p>
                        <ul>${filenamesList}</ul>
                    </div>
                    <button onclick="deleteFile('${data.md5}')" class="btn secondary">删除文件</button>
                </div>`;
        } else {
            showMessage('未找到该文件', true);
        }
    }

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        try {
            const formData = new FormData(this);
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                showMessage(`上传成功！MD5: ${data.md5}，版本: ${data.version}`);
                this.reset();
            } else {
                showMessage(data.message || '上传失败', true);
            }
        } catch (error) {
            showMessage('上传失败：' + error.message, true);
        }
    });

    queryByMd5Form.addEventListener('submit', async function(e) {
        e.preventDefault();
        try {
            const md5 = this.elements.md5.value.trim();
            if (!md5) {
                showMessage('请输入MD5值', true);
                return;
            }

            const response = await fetch(`/query/${md5}`);
            const data = await response.json();
            
            if (response.ok) {
                showResult(data);
            } else {
                showMessage(data.message || '查询失败', true);
            }
        } catch (error) {
            showMessage('查询失败：' + error.message, true);
        }
    });

    queryByFileForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        try {
            const formData = new FormData(this);
            const response = await fetch('/query_by_file', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                showResult(data);
                this.reset();
            } else {
                showMessage(data.message || '查询失败', true);
            }
        } catch (error) {
            showMessage('查询失败：' + error.message, true);
        }
    });
});

async function listQuery() {
    try {
        const response = await fetch('/list');
        const data = await response.json();
        
        if (response.ok) {
            if (data.length === 0) {
                document.getElementById('result').innerHTML = '<div class="info-message">暂无文件记录</div>';
                return;
            }

            let table = `
                <table>
                    <thead>
                        <tr>
                            <th>文件名列表</th>
                            <th>MD5</th>
                            <th>版本</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>`;

            data.forEach(item => {
                const filenamesList = item.filenames.map(filename => `<div class="file-item"><span class="file-icon">📄</span>${filename}<button onclick="downloadFile('${item.md5}', '${filename}')" class="btn primary download-btn">下载</button></div>`).join('');
                table += `
                    <tr>
                        <td class="filenames-cell">${filenamesList}</td>
                        <td>${item.md5}</td>
                        <td>${item.version}</td>
                        <td>
                            <button onclick="deleteFile('${item.md5}')" class="btn secondary">删除</button>
                        </td>
                    </tr>`;
            });

            table += '</tbody></table>';
            document.getElementById('result').innerHTML = table;
        } else {
            showMessage('获取文件列表失败', true);
        }
    } catch (error) {
        showMessage('获取文件列表失败：' + error.message, true);
    }
}

async function deleteFile(md5) {
    if (!confirm('确定要删除该文件吗？')) return;
    
    try {
        const response = await fetch(`/delete/${md5}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            // 如果在列表页面，刷新列表
            if (document.querySelector('table')) {
                listQuery();
            }
        } else {
            showMessage(data.message || '删除失败', true);
        }
    } catch (error) {
        showMessage('删除失败：' + error.message, true);
    }
}

function showMessage(message, isError = false) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<div class="${isError ? 'error' : 'success'}-message">${message}</div>`;
}

async function downloadFile(md5, filename) {
    try {
        const response = await fetch(`/download/${md5}/${filename}`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            showMessage(data.message || '下载失败', true);
        }
    } catch (error) {
        showMessage('下载失败：' + error.message, true);
    }
}