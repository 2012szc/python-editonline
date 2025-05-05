#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   app.py
@Describe :  交互式 Python 编辑器,实现在线运行python代码并输出运行结果
@Contact :   mrbingzhao@qq.com
@License :   (C)Copyright 2024/12/25 15:54, Liugroup-NLPR-CASIA

@Modify Time        @Author       @Version    @Desciption
----------------   -----------   ---------    -----------
2024/12/25 15:54    liubingzhao      1.0           ml
'''

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

from flask import Flask, request, jsonify, send_file
import io
import matplotlib.pyplot as plt
import sys
import base64
import pyflakes.api
import pyflakes.reporter
import jedi
import subprocess
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

class OutputCapture:
    """自定义 stdout 捕获类"""
    def __init__(self, outputs):
        self.outputs = outputs  # 引用外部输出列表

    def write(self, text):
        """捕获文本输出"""
        if text.strip():  # 忽略空白文本
            self.outputs.append({'type': 'text', 'content': text.strip()})

    def flush(self):
        """必须实现的 flush 方法，用于兼容 stdout"""
        pass

@app.route('/')
def home():
    return "Welcome to the Python Code Runner"

@app.route('/terminal', methods=['POST'])
def terminal():
    """处理命令行请求"""
    command = request.json.get('command', '')
    try:
        # 限制可执行的命令
        if not command or not isinstance(command, str):
            return jsonify({'error': 'Invalid command'}), 400
            
        # 执行命令并捕获输出
        result = subprocess.run(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    """处理文件下载请求"""
    file_path = request.args.get('file')
    if not file_path:
        return jsonify({'error': 'File parameter is required'}), 400
    
    # 安全处理文件名
    safe_path = secure_filename(file_path)
    if not os.path.exists(safe_path):
        return jsonify({'error': 'File not found'}), 404
        
    # 限制下载路径在当前目录下
    if not safe_path.startswith(os.getcwd()):
        return jsonify({'error': 'Access denied'}), 403
    
    return send_file(
        safe_path,
        as_attachment=True,
        download_name=os.path.basename(safe_path)
    )

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    inputs = request.json.get('inputs', [])
    input_index = 0

    # 输出列表
    outputs = []
    error = None

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        # 使用Popen运行代码
        process = subprocess.Popen(['python3', temp_path],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

        # 处理输入输出
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            # 检查是否需要输入
            if 'input(' in line or 'input (' in line:
                if input_index < len(inputs):
                    process.stdin.write(inputs[input_index] + '\n')
                    process.stdin.flush()
                    input_index += 1
                else:
                    process.kill()
                    error = "Missing required input"
                    break
            
            output_lines.append(line)

        # 获取完整输出
        output = ''.join(output_lines)
        outputs.append({'type': 'text', 'content': output})

        # 检查错误
        stderr = process.stderr.read()
        if stderr:
            error = stderr

    except Exception as e:
        error = str(e)
    finally:
        # 删除临时文件
        try:
            os.unlink(temp_path)
        except:
            pass

    return jsonify({
        'error': error,
        'outputs': outputs,
        'requires_input': input_index < len(inputs)
    })

@app.route('/lint_code', methods=['POST'])
def lint_code():
    code = request.json.get('code', '')
    errors = []

    try:
        # Use pyflakes for static analysis
        output = io.StringIO()
        reporter = pyflakes.reporter.Reporter(output, output)
        pyflakes.api.check(code, filename='<string>', reporter=reporter)
        error_lines = output.getvalue().strip().split('\n')
        for error in error_lines:
            if error:
                parts = error.split(':', 3)
                if len(parts) >= 3:
                    line = int(parts[1].strip())
                    message = parts[2].strip()
                    errors.append({
                        'message': message,
                        'severity': 'error',  # CodeMirror uses "error", "warning", etc.
                        'from': {'line': line - 1, 'ch': 0},  # Line and character positions
                        'to': {'line': line - 1, 'ch': 80}   # Mark the entire line
                    })
    except Exception as e:
        errors.append({
            'message': str(e),
            'severity': 'error',
            'from': {'line': 0, 'ch': 0},
            'to': {'line': 0, 'ch': 1}
        })

    return jsonify(errors)

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    data = request.json
    code = data.get('code', '')
    cursor = data.get('cursor', {})
    line = cursor.get('line', 0)
    column = cursor.get('ch', 0)

    try:
        script = jedi.Script(code, line=line + 1, column=column)  # jedi 使用 1 基索引
        completions = script.complete()
        suggestions = [
            {'text': comp.name, 'type': comp.type}
            for comp in completions
        ]
        return jsonify(suggestions)
    except Exception as e:
        return jsonify([]), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
